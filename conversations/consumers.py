from urllib.parse import parse_qs
import audioop
from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from conversations.services.azure_openai_service import generate_response
from conversations.services.core.dialogue_engine import process_message
import struct
from conversations.services.speech_service import create_speech_recognizer
import asyncio
import os
import azure.cognitiveservices.speech as speechsdk
import time
import base64

# 🔥 ADD THIS IMPORT
from agents.models import VoiceAgent
import numpy as np


from conversations.models import Conversation, Message
from django.utils import timezone


@sync_to_async
def create_conversation(agent_id, session_id, user_number):
    return Conversation.objects.create(
        agent_id=agent_id,
        session_id=session_id,
        user_number=user_number
    )


@sync_to_async
def save_message(conversation, role, text):
    Message.objects.create(
        conversation=conversation,
        role=role,
        text=text
    )


@sync_to_async
def close_conversation(conversation):
    conversation.ended_at = timezone.now()
    conversation.save()













@sync_to_async
def get_agent_summary(agent_id):
    try:
        agent = VoiceAgent.objects.get(id=agent_id)

        company = agent.company_name or "our company"

        # ✅ Clean summary
        if agent.summary:
            summary = agent.summary.strip().rstrip(".")
            return f"Hello, I am {agent.name} from {company}. {summary}. How can I assist you today?"
        else:
            return f"Hello, I am {agent.name} from {company}. How can I assist you today?"

    except VoiceAgent.DoesNotExist:
        return "Hello, how can I assist you today?"




def create_rtp_packet(payload, seq, ts, ssrc=12345):
    version = 2
    padding = 0
    extension = 0
    cc = 0

    # marker = 1 if seq == 0 else 0   # 🔥 first packet marker
    marker = 1
    payload_type = 0  # PCMU

    first_byte = (version << 6) | (padding << 5) | (extension << 4) | cc
    second_byte = (marker << 7) | payload_type

    header = struct.pack(
        "!BBHII",
        first_byte,
        second_byte,
        seq,
        ts,
        ssrc
    )

    return header + payload



def is_silence(chunk, threshold=200):
    
    rms = audioop.rms(chunk, 2)
    print("🔍 RMS:", rms)  # DEBUG  # PCM energy
    return rms < threshold



def fake_tts(text):
    print("Converting text to audio...")
    return b'\x00' * 320  # dummy PCM audio

def fake_stt(pcm_audio):
    print("Converting audio to text...")
    return "hello"

# ✅ STEP 2 FUNCTION (put here)
def extract_audio_from_rtp(packet):
    return packet[12:]

def decode_g711(ulaw_data):
    return audioop.ulaw2lin(ulaw_data, 2)

def encode_g711(pcm_audio):
    import audioop
    return audioop.lin2ulaw(pcm_audio, 2)

def get_bot_summary(agent_id):
    return "hello, welcome to our AI assistanat. how can i help you today?"

class VoiceBotConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.interrupt_start_time = None
        query_string = self.scope["query_string"].decode()
        params = parse_qs(query_string)

        self.agent_id = params.get("agent_id", [None])[0]
        self.user_number = params.get("from", ["unknown"])[0]

        if not self.agent_id:
            await self.close()
            return

        open("debug_stream_ulaw.raw", "wb").close()
        open("debug_full_ulaw.raw", "wb").close()


        self.recognizer, self.push_stream = create_speech_recognizer()
        import time

        self.session_id = str(time.time())

        self.conversation = await create_conversation(
            self.agent_id,
            self.session_id,
            self.user_number
        )

        self.is_bot_speaking = False
        # self.is_user_speaking = False

        self.partial_text = ""
        self.last_speech_time = time.time()

        self.tts_task = None
        self.tts_lock = asyncio.Lock()
        self.close_code = None
        self.processing_final = False
        self.finalize_task = None


        def handle_recognizing(evt):
            if evt.result.text:
                text = evt.result.text.strip()

                print("🟡 Recognizing:", text)

                self.partial_text = text
                self.last_speech_time = time.time()
                self.is_user_speaking = True


                asyncio.get_event_loop().call_soon_threadsafe(
                    lambda: asyncio.create_task(self.finalize_if_silent())
                )

                # =====================================
                # 🔥 ADD THIS (SAFE EARLY RESPONSE)
                # =====================================
                if (
                    len(text.split()) >= 3
                    and not self.processing_final
                    and not self.is_bot_speaking
                ):
                    print("⚡ EARLY RESPONSE TRIGGER")

                    self.processing_final = True

                    asyncio.get_event_loop().call_soon_threadsafe(
                        lambda: asyncio.create_task(self.handle_ai_reply(text))
                    )

        def handle_recognized(evt):
            print("🔥 CALLBACK TRIGGERED") 
            if evt.result.text:
                text = evt.result.text.strip()

                print("🟢 Final STT:", text)
                # ✅ SAVE USER MESSAGE
                asyncio.create_task(
                    save_message(self.conversation, "user", text)
                )
                self.loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self.handle_ai_reply(text))
                )


        self.recognizer.recognizing.connect(handle_recognizing)
        self.recognizer.recognized.connect(handle_recognized)

        # Start continuous STT
        self.recognizer.start_continuous_recognition_async()
        await self.accept()
        self.is_connected = True
        self.loop = asyncio.get_running_loop()

        # ✅ ADD HERE
        self.jitter_buffer = []
        self.jitter_delay = 3 

        # 🔥 STEP 2.1 — SEND GREETING TO TELECOM
        summary_text = await get_agent_summary(self.agent_id)

        print("📢 Sending summary:", summary_text)

        await asyncio.sleep(0.2)

        asyncio.create_task(self.send_tts(summary_text))
        await self.send(text_data=json.dumps({
            "message": f"Connected to agent {self.agent_id}"
        }))

    async def receive(self, text_data=None, bytes_data=None):
        print("📥 RECEIVE CALLED")


        if text_data:
            try:
                data = json.loads(text_data)

                if data.get("event") == "media":
                    payload = data["media"]["payload"]

                    ulaw_chunk = base64.b64decode(payload)

                    print("🔥 Received base64 audio:", len(ulaw_chunk))
                    rms=0

                    # decode µ-law → PCM
                    pcm_audio = decode_g711(ulaw_chunk)

                    # ✅ SAFE normalization
                    pcm_np = np.frombuffer(pcm_audio, dtype=np.int16)
                    pcm_np = np.clip(pcm_np * 1.2, -32768, 32767)
                    pcm_audio = pcm_np.astype(np.int16).tobytes()

                    if len(pcm_audio) % 2 != 0:
                        pcm_audio = pcm_audio[:-1]

                    self.jitter_buffer.append(pcm_audio)

                    if len(self.jitter_buffer) < self.jitter_delay:
                        return

                    pcm_audio = self.jitter_buffer.pop(0)
                    rms = audioop.rms(pcm_audio, 2)
                    print("🔍 RMS:", rms)


                    if rms > 10000:
                        print("⚠️ droping corrupted audio")
                        return

                    if rms > 50:

                        self.push_stream.write(pcm_audio)

                    # ✅ speech timing
                    if rms >= 80:
                        self.last_speech_time = time.time()

                    # ✅ INTERRUPT LOGIC
                    if self.is_bot_speaking:

                        if rms < 100:
                            self.interrupt_start_time = None
                            return

                        if self.interrupt_start_time is None:
                            self.interrupt_start_time = time.time()
                            return

                        if time.time() - self.interrupt_start_time < 0.3:
                            return

                        if time.time() - self.bot_start_time < 0.5:
                            return

                        print("🛑 USER INTERRUPTED BOT")

                        self.is_bot_speaking = False

                        if self.tts_task and not self.tts_task.done():
                            self.tts_task.cancel()
                        
                        self.jitter_buffer.clear()
                        self.last_speech_time = time.time() - 2

                        return
                    
                    # =========================================
                    # ✅ 🔥 PUT YOUR FORCE FINAL HERE (END ONLY)
                    # =========================================

                    if (
                        self.partial_text
                        and len(self.partial_text) > 2
                        and not self.processing_final
                        and time.time() - self.last_speech_time > 0.3
                    ):
                        print("⚡ FORCE FINAL TRIGGER")

                        self.processing_final = True

                        try:
                            await self.handle_ai_reply(self.partial_text)
                        finally:
                            self.partial_text = ""
                            self.processing_final = False


            except Exception as e:
                print("❌ Error in receive:", e)


    async def handle_ai_reply(self, text):

        print("🚀 Sending to LLM:", text)

        reply, _ = await sync_to_async(process_message)(
            self.agent_id,
            text,
            self.session_id
        )
        # ✅ SAVE BOT MESSAGE
        await save_message(self.conversation, "bot", reply)

        print("🤖 BOT:", reply)

        self.is_bot_speaking = True  # 🔥 IMPORTANT

        sentences = [s.strip() for s in reply.split(".") if s.strip()]

        async def speak_sentences():
            for sentence in sentences:

                if not self.is_connected:
                    break

                if not self.is_bot_speaking:
                    break

                await self.send_tts(sentence)

        self.tts_task = asyncio.create_task(speak_sentences())



    async def handle_bot_response(self, text):
        try:
            print("🤖 Sending to LLM:", text)

            response = await generate_response(
                agent_id=self.agent_id,   # ✅ FIX
                message=text,
                session_id=self.session_id   # ✅ FIX
            )

            print("🤖 BOT:", response)

        except Exception as e:
            print("❌ Bot error:", str(e))



    async def send_tts(self, text):
        async with self.tts_lock:
        

            # 🔥 STEP 8 START (ADD THIS LINE HERE)
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

                print("Converting text to audio...")

                loop = asyncio.get_event_loop()

                result = await loop.run_in_executor(
                    None,
                    lambda: synthesizer.speak_text_async(text).get()
                )
                pcm_audio = result.audio_data

                # 🔥 DEBUG START
                print("========== TTS DEBUG ==========")
                print("TTS TEXT:", text)
                print("PCM LENGTH:", len(pcm_audio))
                print("================================")

                if pcm_audio[:4] == b'RIFF':
                    pcm_audio = pcm_audio[44:]

                print("PCM reply length:", len(pcm_audio))

                if len(pcm_audio) % 2 != 0:
                    pcm_audio = pcm_audio[:-1]

                FRAME_PCM = 320
                processed_pcm = b""

                for i in range(0, len(pcm_audio), FRAME_PCM):
                    frame = pcm_audio[i:i+FRAME_PCM]

                    if len(frame) < FRAME_PCM:
                        frame = frame.ljust(FRAME_PCM, b'\x00')

                    processed_pcm += frame
                    
                ulaw_audio = encode_g711(processed_pcm)

                print("TOTAL ULaw SIZE:", len(ulaw_audio))
                print("EXPECTED CHUNKS:", len(ulaw_audio) // 160)

                with open("debug_full_ulaw.raw", "wb") as f:
                    f.write(ulaw_audio)

                for i in range(0, len(ulaw_audio), 160):


                    # ✅ ADD THIS BLOCK
                    if not self.is_bot_speaking:
                        print("🛑 TTS loop stopped (bot interrupted)")
                        break

                    # if i > 40000:   # ~2 sec audio
                    #     break
                    chunk = ulaw_audio[i:i+160]

                    if len(chunk) < 160:
                        chunk = chunk.ljust(160, b'\x00')

                    payload = base64.b64encode(chunk).decode()

                    with open("debug_sent_ulaw.raw", "ab") as f:
                        f.write(chunk)

                    print("Sending chunk:", i)

                    message = {
                        "event": "media",
                        "media": {
                            "payload": payload
                        }
                    }

                    try:
                        await self.send(text_data=json.dumps(message))
                    except Exception as e:
                        print("Send failed:", e)
                        break
                    
                    if i % 8000 == 0:
                        await self.send(text_data=json.dumps({
                            "event": "ping"
                        }))

                    await asyncio.sleep(0.02)
                    await asyncio.sleep(0)

            except asyncio.CancelledError:
                print("🛑 TTS cancelled due to interrupt")

            finally:
                # 🔥 STEP 8 END (ADD THIS BLOCK HERE)
                self.is_bot_speaking = False
            
        

    async def finalize_if_silent(self):
            await asyncio.sleep(0.2)

            if self.processing_final:
                return

            if time.time() - self.last_speech_time >= 0.5:
                final_text = self.clean_text(self.partial_text)

                if final_text:
                    self.processing_final = True

                    try:
                        print("🧠 FINAL USER TEXT:", final_text)

                        self.is_user_speaking = False

                        await self.handle_ai_reply(final_text)

                    finally:
                        # 🔥 ALWAYS RESET
                        self.partial_text = ""
                        self.processing_final = False

        # ✅ ADD HERE (same indentation level)
    def clean_text(self, text):
            text = text.lower().strip()

            fillers = ["uh", "um", "hmm", "you know", "like"]
            for f in fillers:
                text = text.replace(f, "")

            text = " ".join(text.split())

            return text


    # ✅ PUT IT HERE (same level)
    async def safe_tts_stream(self, text):
        try:
            # ✅ CHANGED: always use task + cancel previous
            if self.tts_task and not self.tts_task.done():
                self.tts_task.cancel()

            self.tts_task = asyncio.create_task(self.send_tts(text))
        except Exception as e:
            print("TTS stream error:", e)
    
    async def disconnect(self, close_code):
        print("🔌 WebSocket disconnected")

        self.is_connected = False

        self.close_code = close_code


        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()

        # ✅ ADD HERE (LAST LINE)
        if hasattr(self, "conversation"):
            await close_conversation(self.conversation)

