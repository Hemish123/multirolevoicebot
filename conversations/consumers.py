from urllib.parse import parse_qs
import audioop
from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from conversations.services.core.dialogue_engine import process_message
from conversations.services.speech_service import create_speech_recognizer
import struct
import asyncio
import os
import azure.cognitiveservices.speech as speechsdk
import time
import base64
import uuid
import numpy as np
from django.utils import timezone

from agents.models import VoiceAgent
from conversations.models import Conversation, Message


# ================= DATABASE =================

@sync_to_async
def create_conversation(agent_id, session_id, user_number):
    return Conversation.objects.create(
        agent_id=agent_id,
        session_id=session_id,
        user_number=user_number
    )


@sync_to_async
def save_message(conversation, role, text):
    last = Message.objects.filter(conversation=conversation).order_by('-created_at').first()
    if last and last.text.strip() == text.strip() and last.role == role:
        return
    Message.objects.create(conversation=conversation, role=role, text=text)


@sync_to_async
def update_user_number(conversation, number):
    conversation.user_number = number
    conversation.save()


@sync_to_async
def close_conversation(conversation):
    conversation.ended_at = timezone.now()
    conversation.save()


@sync_to_async
def get_agent_summary(agent_id):
    try:
        agent = VoiceAgent.objects.get(id=agent_id)
        company = agent.company_name or "our company"

        if agent.summary:
            summary = agent.summary.strip().rstrip(".")
            return f"Hello, I am {agent.name} from {company}. {summary}. How can I assist you today?"
        return f"Hello, I am {agent.name} from {company}. How can I assist you today?"

    except VoiceAgent.DoesNotExist:
        return "Hello, how can I assist you today?"


# ================= AUDIO =================

def decode_g711(ulaw):
    return audioop.ulaw2lin(ulaw, 2)


def encode_g711(pcm):
    return audioop.lin2ulaw(pcm, 2)


# ================= CONSUMER =================

class VoiceBotConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.loop = asyncio.get_running_loop()

        params = parse_qs(self.scope["query_string"].decode())

        self.agent_id = params.get("agent_id", [None])[0]
        self.user_number = params.get("from", ["unknown"])[0]

        if not self.agent_id:
            await self.close()
            return

        self.session_id = str(uuid.uuid4())

        self.conversation = await create_conversation(
            self.agent_id,
            self.session_id,
            self.user_number
        )

        # 🔥 STATE
        self.is_bot_speaking = False
        self.is_connected = True
        self.is_processing = False

        self.partial_text = ""
        self.last_final_text = ""

        self.last_sent_text = ""
        self.last_sent_time = 0

        # 🔥 LOCK (CRITICAL)
        self.final_lock = asyncio.Lock()

        # 🔥 AUDIO
        self.jitter_buffer = []
        self.jitter_delay = 3

        self.speech_active = False
        self.silence_start_time = None

        self.interrupt_start_time = None

        self.tts_task = None
        self.tts_lock = asyncio.Lock()

        # ================= STT =================
        self.recognizer, self.push_stream = create_speech_recognizer()

        def handle_recognizing(evt):
            if evt.result.text:
                self.partial_text = evt.result.text.strip()
                print("🟡 Partial:", self.partial_text)

        self.recognizer.recognizing.connect(handle_recognizing)

        self.recognizer.start_continuous_recognition_async()

        await self.accept()

        # 🔥 GREETING
        summary = await get_agent_summary(self.agent_id)
        asyncio.create_task(self.send_tts(summary))

    # ================= RECEIVE =================

    async def receive(self, text_data=None, bytes_data=None):

        if not text_data:
            return

        try:
            data = json.loads(text_data)

            # ✅ CALL START
            if data.get("event") == "start":
                try:
                    number = data["start"]["customParameters"]["callerNumber"]
                    self.user_number = number
                    await update_user_number(self.conversation, number)
                except:
                    pass

            # ================= AUDIO =================
            if data.get("event") == "media":

                payload = base64.b64decode(data["media"]["payload"])
                pcm = decode_g711(payload)

                # 🔥 NORMALIZE
                pcm_np = np.frombuffer(pcm, dtype=np.int16)
                pcm_np = np.clip(pcm_np * 1.2, -32768, 32767)
                pcm = pcm_np.astype(np.int16).tobytes()

                if len(pcm) % 2 != 0:
                    pcm = pcm[:-1]

                self.jitter_buffer.append(pcm)

                if len(self.jitter_buffer) < self.jitter_delay:
                    return

                pcm = self.jitter_buffer.pop(0)

                rms = audioop.rms(pcm, 2)

                # 🔥 DROP CORRUPT
                if rms > 20000:
                    return

                # 🔥 SEND TO STT
                if rms > 120:
                    self.push_stream.write(pcm)

                # ================= FINAL DETECTION =================
                if rms > 200:
                    self.speech_active = True
                    self.silence_start_time = None

                else:
                    if self.speech_active:
                        if self.silence_start_time is None:
                            self.silence_start_time = time.time()

                        elif time.time() - self.silence_start_time > 0.6:
                            self.speech_active = False

                            # 🔥 GUARD: skip if bot is speaking or already processing
                            if self.is_bot_speaking or self.is_processing:
                                return

                            if self.partial_text:

                                text = self.partial_text.strip()

                                # 🔥 Clear partial IMMEDIATELY to prevent re-triggers
                                self.partial_text = ""

                                # ignore very short unstable text
                                if len(text.split()) < 2:
                                    return

                                # normalize for comparison
                                normalized = text.lower().strip()

                                # prevent repeated loop
                                if normalized == self.last_sent_text:
                                    return

                                # cooldown
                                if time.time() - self.last_sent_time < 2.0:
                                    return

                                self.last_sent_text = normalized
                                self.last_sent_time = time.time()

                                print("⚡ FINAL TRIGGER:", text)

                                self.is_processing = True
                                try:
                                    async with self.final_lock:
                                        await self.handle_ai_reply(text)
                                finally:
                                    self.is_processing = False

                # ================= INTERRUPT =================
                if self.is_bot_speaking:

                    if rms < 400:
                        self.interrupt_start_time = None
                        return

                    if self.interrupt_start_time is None:
                        self.interrupt_start_time = time.time()
                        return

                    if time.time() - self.interrupt_start_time < 1.0:
                        return

                    print("🛑 INTERRUPT")

                    self.is_bot_speaking = False

                    if self.tts_task and not self.tts_task.done():
                        self.tts_task.cancel()

                    self.jitter_buffer.clear()

        except Exception as e:
            print("❌ RECEIVE ERROR:", e)

    # ================= AI =================

    async def handle_ai_reply(self, text):
        text = text.strip()
        if not text:
            return

        # 🔥 DUPLICATE BLOCK (normalized comparison)
        normalized = text.lower().strip()
        if normalized == self.last_final_text:
            print("⏭️ SKIPPED DUPLICATE:", text)
            return

        self.last_final_text = normalized

        # 🔥 Clear partial to prevent stale re-triggers
        self.partial_text = ""

        print("🧠 FINAL:", text)

        await save_message(self.conversation, "user", text)

        reply, _ = await sync_to_async(process_message)(
            self.agent_id,
            text,
            self.session_id
        )

        await save_message(self.conversation, "bot", reply)

        print("🤖 BOT:", reply)

        self.is_bot_speaking = True

        # Cancel any previous TTS before starting new one
        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()

        self.tts_task = asyncio.create_task(self.send_tts(reply))

    # ================= TTS =================

    async def send_tts(self, text):
        async with self.tts_lock:

            self.is_bot_speaking = True
            self.bot_start_time = time.time()

            try:
                speech_config = speechsdk.SpeechConfig(
                    subscription=os.getenv("AZURE_SPEECH_KEY"),
                    region=os.getenv("AZURE_SPEECH_REGION")
                )

                speech_config.speech_synthesis_voice_name = "en-IN-NeerjaNeural"
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Raw8Khz16BitMonoPcm
                )

                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=speech_config,
                    audio_config=None
                )

                loop = asyncio.get_event_loop()

                result = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: synthesizer.speak_text_async(text).get()
                    ),
                    timeout=5
                )

                pcm = result.audio_data

                if pcm[:4] == b'RIFF':
                    pcm = pcm[44:]

                if len(pcm) % 2 != 0:
                    pcm = pcm[:-1]

                ulaw = encode_g711(pcm)

                for i in range(0, len(ulaw), 160):

                    if not self.is_bot_speaking:
                        break

                    chunk = ulaw[i:i+160]
                    payload = base64.b64encode(chunk).decode()

                    await self.send(text_data=json.dumps({
                        "event": "media",
                        "media": {"payload": payload}
                    }))

                    await asyncio.sleep(0.02)

            except asyncio.CancelledError:
                print("🛑 TTS CANCELLED")

            except Exception as e:
                print("❌ TTS ERROR:", e)

            finally:
                self.is_bot_speaking = False

    # ================= DISCONNECT =================

    async def disconnect(self, close_code):
        print("🔌 DISCONNECTED")

        self.is_connected = False

        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()

        if hasattr(self, "conversation"):
            await close_conversation(self.conversation)