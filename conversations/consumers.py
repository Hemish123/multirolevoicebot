# import random
# from urllib.parse import parse_qs
# import audioop
# from asgiref.sync import sync_to_async
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from conversations.services.core.dialogue_engine import process_message
# from conversations.services.speech_service import create_speech_recognizer
# import struct
# import asyncio
# import os
# import azure.cognitiveservices.speech as speechsdk
# import time
# import base64
# import uuid
# import numpy as np
# from django.utils import timezone

# from agents.models import VoiceAgent
# from conversations.models import Conversation, Message


# # ================= DATABASE =================

# @sync_to_async
# def create_conversation(agent_id, session_id, user_number):
#     return Conversation.objects.create(
#         agent_id=agent_id,
#         session_id=session_id,
#         user_number=user_number
#     )


# @sync_to_async
# def save_message(conversation, role, text):
#     last = Message.objects.filter(conversation=conversation).order_by('-created_at').first()
#     if last and last.text.strip() == text.strip() and last.role == role:
#         return
#     Message.objects.create(conversation=conversation, role=role, text=text)


# @sync_to_async
# def update_user_number(conversation, number):
#     conversation.user_number = number
#     conversation.save()


# @sync_to_async
# def close_conversation(conversation):
#     conversation.ended_at = timezone.now()
#     conversation.save()


# @sync_to_async
# def get_agent_summary(agent_id):
#     try:
#         agent = VoiceAgent.objects.get(id=agent_id)
#         company = agent.company_name or "our company"

#         if agent.summary:
#             summary = agent.summary.strip().rstrip(".")
#             return f"Hello, I am {agent.name} from {company}. {summary}. How can I assist you today?"
#         return f"Hello, I am {agent.name} from {company}. How can I assist you today?"

#     except VoiceAgent.DoesNotExist:
#         return "Hello, how can I assist you today?"


# # ================= AUDIO =================

# def decode_g711(ulaw):
#     return audioop.ulaw2lin(ulaw, 2)


# def encode_g711(pcm):
#     return audioop.lin2ulaw(pcm, 2)


# # ✅ ADD HERE (same level, outside class)
# def is_end_intent(text: str) -> bool:
#     text = text.lower().strip()

#     end_keywords = [
#         "bye", "goodbye", "ok bye", "okay bye",
#         "thank you", "thanks", "thanks a lot",
#         "that's all", "no thanks", "nothing else",
#         "i am done", "end call", "stop"
#     ]

#     return any(keyword in text for keyword in end_keywords)


# # ================= CONSUMER =================

# class VoiceBotConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.loop = asyncio.get_running_loop()

#         params = parse_qs(self.scope["query_string"].decode())

#         self.agent_id = params.get("agent_id", [None])[0]
#         self.user_number = params.get("from", ["unknown"])[0]

#         if not self.agent_id:
#             await self.close()
#             return

#         self.session_id = str(uuid.uuid4())

#         self.conversation = await create_conversation(
#             self.agent_id,
#             self.session_id,
#             self.user_number
#         )

#         # 🔥 STATE
#         self.is_bot_speaking = False
#         self.is_connected = True
#         self.is_processing = False

#         self.partial_text = ""
#         self.last_final_text = ""

#         self.last_sent_text = ""
#         self.last_sent_time = 0

#         # 🔥 LOCK (CRITICAL)
#         self.final_lock = asyncio.Lock()

#         # 🔥 AUDIO
#         self.jitter_buffer = []
#         self.jitter_delay = 3

#         self.speech_active = False
#         self.silence_start_time = None

#         self.interrupt_start_time = None

#         self.tts_task = None
#         self.tts_lock = asyncio.Lock()

#         # ================= STT =================
#         self.recognizer, self.push_stream = create_speech_recognizer()

#         def handle_recognizing(evt):
#             if evt.result.text:
#                 self.partial_text = evt.result.text.strip()
#                 print("🟡 Partial:", self.partial_text)

#         self.recognizer.recognizing.connect(handle_recognizing)

#         self.recognizer.start_continuous_recognition_async()

#         await self.accept()

#         # 🔥 GREETING
#         summary = await get_agent_summary(self.agent_id)
#         asyncio.create_task(self.send_tts(summary))

#     # ================= RECEIVE =================

#     async def receive(self, text_data=None, bytes_data=None):

#         if not text_data:
#             return

#         try:
#             data = json.loads(text_data)

#             # ✅ CALL START
#             if data.get("event") == "start":
#                 try:
#                     number = data["start"]["customParameters"]["callerNumber"]
#                     self.user_number = number
#                     await update_user_number(self.conversation, number)
#                 except:
#                     pass

#             # ================= AUDIO =================
#             if data.get("event") == "media":

#                 payload = base64.b64decode(data["media"]["payload"])
#                 pcm = decode_g711(payload)

#                 # 🔥 NORMALIZE
#                 pcm_np = np.frombuffer(pcm, dtype=np.int16)
#                 pcm_np = np.clip(pcm_np * 1.2, -32768, 32767)
#                 pcm = pcm_np.astype(np.int16).tobytes()

#                 if len(pcm) % 2 != 0:
#                     pcm = pcm[:-1]

#                 self.jitter_buffer.append(pcm)

#                 if len(self.jitter_buffer) < self.jitter_delay:
#                     return

#                 pcm = self.jitter_buffer.pop(0)

#                 rms = audioop.rms(pcm, 2)

#                 # 🔥 DROP CORRUPT
#                 if rms > 20000:
#                     return

#                 # 🔥 SEND TO STT
#                 if rms > 120:
#                     self.push_stream.write(pcm)

#                 # ================= FINAL DETECTION =================
#                 if rms > 200:
#                     self.speech_active = True
#                     self.silence_start_time = None

#                 else:
#                     if self.speech_active:
#                         if self.silence_start_time is None:
#                             self.silence_start_time = time.time()

#                         elif time.time() - self.silence_start_time > 0.6:
#                             self.speech_active = False

#                             # 🔥 GUARD: skip if bot is speaking or already processing
#                             if self.is_bot_speaking or self.is_processing:
#                                 return

#                             if self.partial_text:

#                                 text = self.partial_text.strip()

#                                 # 🔥 Clear partial IMMEDIATELY to prevent re-triggers
#                                 self.partial_text = ""

#                                 # ignore very short unstable text
#                                 if len(text.split()) < 2:
#                                     return

#                                 # normalize for comparison
#                                 normalized = text.lower().strip()

#                                 # prevent repeated loop
#                                 if normalized == self.last_sent_text:
#                                     return

#                                 # cooldown
#                                 if time.time() - self.last_sent_time < 2.0:
#                                     return

#                                 self.last_sent_text = normalized
#                                 self.last_sent_time = time.time()

#                                 print("⚡ FINAL TRIGGER:", text)

#                                 self.is_processing = True
#                                 try:
#                                     async with self.final_lock:
#                                         await self.handle_ai_reply(text)
#                                 finally:
#                                     self.is_processing = False

#                 # ================= INTERRUPT =================
#                 if self.is_bot_speaking:

#                     if rms < 400:
#                         self.interrupt_start_time = None
#                         return

#                     if self.interrupt_start_time is None:
#                         self.interrupt_start_time = time.time()
#                         return

#                     if time.time() - self.interrupt_start_time < 1.0:
#                         return

#                     print("🛑 INTERRUPT")

#                     self.is_bot_speaking = False

#                     if self.tts_task and not self.tts_task.done():
#                         self.tts_task.cancel()

#                     self.jitter_buffer.clear()

#         except Exception as e:
#             print("❌ RECEIVE ERROR:", e)

#     # ================= AI =================

#     async def handle_ai_reply(self, text):
#         text = text.strip()
#         if not text:
#             return

#         # 🔥 DUPLICATE BLOCK (normalized comparison)
#         normalized = text.lower().strip()


#         # 🔥 END CALL DETECTION
#         if is_end_intent(normalized):
#             print("📴 END INTENT DETECTED:", text)

#             await save_message(self.conversation, "user", text)

#             farewell = random.choice([
#                 "Thank you for calling. Have a great day!",
#                 "Thanks for your time. Goodbye!",
#                 "It was nice speaking with you. Bye!"
#             ])

#             await save_message(self.conversation, "bot", farewell)

#             # Speak farewell
#             await self.send_tts(farewell)

#             # Close conversation in DB
#             await close_conversation(self.conversation)

#             # 🔥 SEND CALL END SIGNAL (IMPORTANT)
#             await self.send(text_data=json.dumps({
#                 "event": "stop"
#             }))

#             # Close websocket
#             await self.close()

#             return
#         if normalized == self.last_final_text:
#             print("⏭️ SKIPPED DUPLICATE:", text)
#             return

#         self.last_final_text = normalized

#         # 🔥 Clear partial to prevent stale re-triggers
#         self.partial_text = ""

#         print("🧠 FINAL:", text)

#         await save_message(self.conversation, "user", text)

#         reply, _ = await sync_to_async(process_message)(
#             self.agent_id,
#             text,
#             self.session_id
#         )

#         await save_message(self.conversation, "bot", reply)

#         print("🤖 BOT:", reply)

#         self.is_bot_speaking = True

#         # Cancel any previous TTS before starting new one
#         if self.tts_task and not self.tts_task.done():
#             self.tts_task.cancel()

#         self.tts_task = asyncio.create_task(self.send_tts(reply))

#     # ================= TTS =================

#     async def send_tts(self, text):
#         async with self.tts_lock:

#             self.is_bot_speaking = True
#             self.bot_start_time = time.time()

#             try:
#                 speech_config = speechsdk.SpeechConfig(
#                     subscription=os.getenv("AZURE_SPEECH_KEY"),
#                     region=os.getenv("AZURE_SPEECH_REGION")
#                 )

#                 speech_config.speech_synthesis_voice_name = "en-IN-NeerjaNeural"
#                 speech_config.set_speech_synthesis_output_format(
#                     speechsdk.SpeechSynthesisOutputFormat.Raw8Khz16BitMonoPcm
#                 )

#                 synthesizer = speechsdk.SpeechSynthesizer(
#                     speech_config=speech_config,
#                     audio_config=None
#                 )

#                 loop = asyncio.get_event_loop()

#                 result = await asyncio.wait_for(
#                     loop.run_in_executor(
#                         None,
#                         lambda: synthesizer.speak_text_async(text).get()
#                     ),
#                     timeout=5
#                 )

#                 pcm = result.audio_data

#                 if pcm[:4] == b'RIFF':
#                     pcm = pcm[44:]

#                 if len(pcm) % 2 != 0:
#                     pcm = pcm[:-1]

#                 ulaw = encode_g711(pcm)

#                 for i in range(0, len(ulaw), 160):

#                     if not self.is_bot_speaking:
#                         break

#                     chunk = ulaw[i:i+160]
#                     payload = base64.b64encode(chunk).decode()

#                     await self.send(text_data=json.dumps({
#                         "event": "media",
#                         "media": {"payload": payload}
#                     }))

#                     await asyncio.sleep(0.02)

#             except asyncio.CancelledError:
#                 print("🛑 TTS CANCELLED")

#             except Exception as e:
#                 print("❌ TTS ERROR:", e)

#             finally:
#                 self.is_bot_speaking = False

#     # ================= DISCONNECT =================

#     async def disconnect(self, close_code):
#         print("🔌 DISCONNECTED")

#         self.is_connected = False

#         if self.tts_task and not self.tts_task.done():
#             self.tts_task.cancel()

#         if hasattr(self, "conversation"):
#             await close_conversation(self.conversation)




#================================================================
#==================================================================
#========================================================================


from urllib.parse import parse_qs
import audioop
from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from conversations.services.core.dialogue_engine import process_message
from conversations.services.speech_service import create_speech_recognizer
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

# ✅ ADD HERE
def is_end_intent(text: str) -> bool:
    text = text.lower().strip()

    end_keywords = [
        "bye", "goodbye", "ok bye", "okay bye",
        "thank you", "thanks a lot",
        "that's all", "no thanks", "nothing else",
        "i am done", "end call", "stop"
    ]

    return any(keyword in text for keyword in end_keywords)


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
            self.agent_id, self.session_id, self.user_number
        )

        # ── STATE ──────────────────────────────────────────────
        self.is_bot_speaking = False
        self.is_connected = True
        self.is_processing = False

        # FIX: Two separate text holders — partial (interim) and final (from recognized event)
        self.partial_text = ""          # Updated by recognizing (interim) — thread-safe via queue
        self.final_text_queue = asyncio.Queue()  # Azure's TRUE final results land here

        self.last_dispatched_text = ""  # Dedup guard
        self.last_dispatch_time = 0.0

        # ── LOCKS & TASKS ──────────────────────────────────────
        self.processing_lock = asyncio.Lock()   # Prevents concurrent AI calls
        self.tts_task = None

        # ── AUDIO / VAD ────────────────────────────────────────
        self.jitter_buffer = []
        self.jitter_delay = 3

        self.speech_active = False
        self.silence_start_time = None

        # FIX: Separate silence threshold — longer for telecom latency
        self.SPEECH_DETECT_RMS = 200        # rms to count as "speaking"
        self.SILENCE_TRIGGER_SEC = 1.2      # wait this long after speech stops (was 0.6 — too fast)
        self.MIN_WORD_COUNT = 1              # ✅ FIX: allow single-word replies like Yes/No/Sure

        # Interrupt detection
        self.interrupt_start_time = None
        self.INTERRUPT_RMS = 400
        self.INTERRUPT_HOLD_SEC = 1.0

        # ── STT SETUP ──────────────────────────────────────────
        self.recognizer, self.push_stream = create_speech_recognizer()
        self._setup_stt_callbacks()
        self.recognizer.start_continuous_recognition_async()

        await self.accept()

        summary = await get_agent_summary(self.agent_id)
        asyncio.create_task(self.send_tts(summary))

        # FIX: Start background task that drains Azure's final results
        self.final_consumer_task = asyncio.create_task(self._final_text_consumer())

    def _setup_stt_callbacks(self):
        """
        FIX: Hook BOTH recognizing (partial) AND recognized (final) events.
        Azure's 'recognized' fires when Azure itself detects end-of-utterance — 
        this is far more accurate than manual silence detection alone.
        Callbacks run in a sync thread — use thread-safe call_soon_threadsafe.
        """

        def handle_recognizing(evt):
            # Interim partial — just for display / fast-response use
            text = evt.result.text.strip() if evt.result.text else ""
            # Thread-safe update into event loop
            self.loop.call_soon_threadsafe(self._set_partial, text)

        def handle_recognized(evt):
            # TRUE FINAL from Azure's own VAD — this is the reliable trigger
            text = evt.result.text.strip() if evt.result.text else ""
            if text:
                print("✅ Azure FINAL:", text)
                # Thread-safe enqueue into event loop
                self.loop.call_soon_threadsafe(
                    lambda: self.final_text_queue.put_nowait(text)
                )

        def handle_canceled(evt):
            print("⚠️ STT Canceled:", evt.result.cancellation_details)

        self.recognizer.recognizing.connect(handle_recognizing)
        self.recognizer.recognized.connect(handle_recognized)
        self.recognizer.canceled.connect(handle_canceled)

    def _set_partial(self, text):
        """Called from event loop via call_soon_threadsafe — safe to set directly."""
        self.partial_text = text

    async def _final_text_consumer(self):
        """
        FIX: Background coroutine that processes Azure's TRUE final results.
        This runs independently of audio frame processing — no race conditions.
        This is the PRIMARY trigger for AI replies.
        """
        while self.is_connected:
            try:
                # Wait for a final result from Azure (with timeout to allow clean shutdown)
                text = await asyncio.wait_for(self.final_text_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except Exception:
                break

            if not text:
                continue

            # Skip if bot is speaking or already processing
            if self.is_bot_speaking or self.is_processing:
                print("⏭️ Skipped (bot busy):", text)
                continue

            # Dedup check
            normalized = text.lower().strip()
            if normalized == self.last_dispatched_text:
                print("⏭️ Duplicate skipped:", text)
                continue

            # Cooldown guard
            if time.time() - self.last_dispatch_time < 1.5:
                print("⏭️ Cooldown skip:", text)
                continue

            # Minimum word filter
            if len(text.split()) < self.MIN_WORD_COUNT:
                print("⏭️ Too short:", text)
                continue

            print("⚡ DISPATCHING TO AI:", text)
            self.last_dispatched_text = normalized
            self.last_dispatch_time = time.time()
            self.partial_text = ""  # Clear stale partial

            self.is_processing = True
            try:
                async with self.processing_lock:
                    await self.handle_ai_reply(text)
            finally:
                self.is_processing = False

    # ================= RECEIVE =================

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        try:
            data = json.loads(text_data)

            if data.get("event") == "start":
                try:
                    number = data["start"]["customParameters"]["callerNumber"]
                    self.user_number = number
                    await update_user_number(self.conversation, number)
                except Exception:
                    pass

            if data.get("event") == "media":
                await self._handle_audio_chunk(data)

        except Exception as e:
            print("❌ RECEIVE ERROR:", e)

    async def _handle_audio_chunk(self, data):
        """Separated audio handling for clarity."""

        # payload = base64.b64decode(data["media"]["payload"])
        # pcm = decode_g711(payload)

        # # Normalize volume
        # pcm_np = np.frombuffer(pcm, dtype=np.int16)
        # pcm_np = np.clip(pcm_np * 1.2, -32768, 32767)
        # pcm = pcm_np.astype(np.int16).tobytes()

        # if len(pcm) % 2 != 0:
        #     pcm = pcm[:-1]

        # # Jitter buffer
        # self.jitter_buffer.append(pcm)
        # if len(self.jitter_buffer) < self.jitter_delay:
        #     return

        # pcm = self.jitter_buffer.pop(0)
        # rms = audioop.rms(pcm, 2)

        # # Drop corrupt audio
        # if rms > 20000:
        #     return

        # # Always feed audio to STT (let Azure decide what's speech)
        # # FIX: Lower threshold — don't filter too aggressively, Azure handles noise
        # if rms > 80:
        #     self.push_stream.write(pcm)
        payload = base64.b64decode(data["media"]["payload"])
        pcm = decode_g711(payload)

        # ✅ FIX: Dynamic gain — boosts quiet/soft/slow voices automatically
        pcm_np = np.frombuffer(pcm, dtype=np.int16).copy()
        current_rms = audioop.rms(pcm, 2)
        if current_rms > 50:
            gain = min(1200 / current_rms, 6.0)  # max 6x boost, no distortion
            pcm_np = np.clip(pcm_np * gain, -32768, 32767).astype(np.int16)
        pcm = pcm_np.tobytes()

        if len(pcm) % 2 != 0:
            pcm = pcm[:-1]

        # Jitter buffer
        self.jitter_buffer.append(pcm)
        if len(self.jitter_buffer) < self.jitter_delay:
            return

        pcm = self.jitter_buffer.pop(0)
        rms = audioop.rms(pcm, 2)

        # ✅ FIX: Only drop truly corrupt packets (all samples maxed out)
        pcm_check = np.frombuffer(pcm, dtype=np.int16)
        if int(np.abs(pcm_check).max()) == 32767 and rms > 28000:
            return

        # ✅ FIX: Always feed to Azure — no RMS gate. Azure's own VAD handles noise.
        self.push_stream.write(pcm)

        # ── INTERRUPT DETECTION (check FIRST before silence logic) ──
        # FIX: Check interrupt before silence detection to avoid ordering bug
        if self.is_bot_speaking:
            await self._check_interrupt(rms)
            return  # Don't do silence detection while bot is speaking

        # ── MANUAL SILENCE-BASED FALLBACK TRIGGER ──────────────────
        # This is a BACKUP only — Azure's recognized event is the primary trigger.
        # Useful for cases where Azure's VAD is slow or misses utterances.
        if rms > self.SPEECH_DETECT_RMS:
            self.speech_active = True
            self.silence_start_time = None
        else:
            if self.speech_active:
                if self.silence_start_time is None:
                    self.silence_start_time = time.time()
                elif time.time() - self.silence_start_time > self.SILENCE_TRIGGER_SEC:
                    self.speech_active = False
                    self.silence_start_time = None

                    # FIX: Only use this fallback if Azure hasn't already fired a final result
                    # and we have a meaningful partial to work with
                    if (
                        not self.is_bot_speaking
                        and not self.is_processing
                        and self.partial_text
                        and self.final_text_queue.empty()   # Azure didn't fire — use partial
                    ):
                        fallback_text = self.partial_text.strip()
                        self.partial_text = ""

                        if len(fallback_text.split()) >= self.MIN_WORD_COUNT:
                            normalized = fallback_text.lower()
                            if normalized != self.last_dispatched_text:
                                if time.time() - self.last_dispatch_time >= 1.5:
                                    print("⚡ FALLBACK TRIGGER (partial):", fallback_text)
                                    self.last_dispatched_text = normalized
                                    self.last_dispatch_time = time.time()
                                    self.is_processing = True
                                    try:
                                        async with self.processing_lock:
                                            await self.handle_ai_reply(fallback_text)
                                    finally:
                                        self.is_processing = False

    async def _check_interrupt(self, rms):
        """Handle user interrupting the bot."""
        if rms < self.INTERRUPT_RMS:
            self.interrupt_start_time = None
            return

        if self.interrupt_start_time is None:
            self.interrupt_start_time = time.time()
            return

        if time.time() - self.interrupt_start_time < self.INTERRUPT_HOLD_SEC:
            return

        print("🛑 INTERRUPT DETECTED")
        self.is_bot_speaking = False
        self.interrupt_start_time = None

        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()
            try:
                await self.tts_task
            except asyncio.CancelledError:
                pass

        self.jitter_buffer.clear()

    # ================= AI =================

    async def handle_ai_reply(self, text):
        text = text.strip()
        if not text:
            return
        
        normalized = text.lower().strip()

        # ================= 🔥 ADD HERE =================
        if is_end_intent(normalized):
            print("📴 END INTENT DETECTED:", text)

            await save_message(self.conversation, "user", text)

            farewell = "Thank you for calling. Have a great day!"

            await save_message(self.conversation, "bot", farewell)

            # Stop any running TTS
            if self.tts_task and not self.tts_task.done():
                self.tts_task.cancel()
                try:
                    await self.tts_task
                except asyncio.CancelledError:
                    pass

            # Speak farewell
            await self.send_tts(farewell)

            # Close DB conversation
            await close_conversation(self.conversation)

            # 🔥 Send telecom stop signal
            await self.send(text_data=json.dumps({
                "event": "stop"
            }))

            self.is_connected = False

            await self.close()
            return

        print("🧠 AI INPUT:", text)
        await save_message(self.conversation, "user", text)

        reply, _ = await sync_to_async(process_message)(
            self.agent_id, text, self.session_id
        )

        if not reply:
            return

        await save_message(self.conversation, "bot", reply)
        print("🤖 BOT REPLY:", reply)

        # Cancel previous TTS if somehow still running
        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()
            try:
                await self.tts_task
            except asyncio.CancelledError:
                pass

        self.tts_task = asyncio.create_task(self.send_tts(reply))

    # ================= TTS =================

    async def send_tts(self, text):
        """
        FIX: Removed tts_lock — it caused deadlock when task was cancelled while
        holding the lock. The tts_task handle + is_bot_speaking flag are sufficient.
        FIX: Increased TTS synthesis timeout to 15s for longer replies.
        """
        self.is_bot_speaking = True

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

            # FIX: Increased timeout from 5s → 15s — long replies were timing out
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: synthesizer.speak_text_async(text).get()
                ),
                timeout=15
            )

            if result.reason == speechsdk.ResultReason.Canceled:
                details = result.cancellation_details
                print("❌ TTS Canceled:", details.reason, details.error_details)
                return

            pcm = result.audio_data

            # Strip WAV header if present
            if pcm[:4] == b'RIFF':
                pcm = pcm[44:]

            if len(pcm) % 2 != 0:
                pcm = pcm[:-1]

            ulaw = encode_g711(pcm)

            # Stream audio chunks
            for i in range(0, len(ulaw), 160):
                if not self.is_bot_speaking:
                    print("🛑 TTS stopped mid-stream")
                    break

                chunk = ulaw[i:i + 160]
                payload = base64.b64encode(chunk).decode()

                await self.send(text_data=json.dumps({
                    "event": "media",
                    "media": {"payload": payload}
                }))

                await asyncio.sleep(0.02)

        except asyncio.CancelledError:
            print("🛑 TTS CANCELLED")
            raise  # Must re-raise CancelledError

        except asyncio.TimeoutError:
            print("❌ TTS TIMEOUT — reply too long or Azure slow")

        except Exception as e:
            print("❌ TTS ERROR:", e)

        finally:
            self.is_bot_speaking = False

    # ================= DISCONNECT =================

    async def disconnect(self, close_code):
        print("🔌 DISCONNECTED:", close_code)
        self.is_connected = False

        # Stop background consumer task
        if hasattr(self, "final_consumer_task"):
            self.final_consumer_task.cancel()
            try:
                await self.final_consumer_task
            except asyncio.CancelledError:
                pass

        # Stop TTS
        if self.tts_task and not self.tts_task.done():
            self.tts_task.cancel()
            try:
                await self.tts_task
            except asyncio.CancelledError:
                pass

        # Stop STT
        if hasattr(self, "recognizer"):
            try:
                self.recognizer.stop_continuous_recognition_async()
            except Exception:
                pass

        if hasattr(self, "push_stream"):
            try:
                self.push_stream.close()
            except Exception:
                pass

        if hasattr(self, "conversation"):
            await close_conversation(self.conversation)



#=========================================================================
#=============it's also working=========================================
#=========================================================================


# """
# VoiceBotConsumer — production-ready, Python 3.11
# Bridges Django Channels WebSocket ↔ Telecom call via
# Azure STT → LLM dialogue engine → Azure TTS pipeline.

# Python 3.11 notes
# ─────────────────
# - audioop is present in 3.11 stdlib (removed in 3.13) — used directly.
# - asyncio.get_running_loop() is the correct call inside coroutines (3.10+).
# - asyncio.Task type hint uses `asyncio.Task | None` (union syntax, 3.10+).

# All bugs from audit fixed
# ──────────────────────────
# 1. Echo-to-STT: push_stream.write() gated behind is_bot_speaking check.
# 2. Stale partial_text: cleared + queue flushed at send_tts() entry.
# 3. Queue echo build-up: final_text_queue drained before streaming starts.
# 4. is_bot_speaking set too early: flag set only after synthesis, before stream.
# 5. audioop: used directly from 3.11 stdlib — no workaround needed.
# 6. get_event_loop() -> get_running_loop() inside all coroutines.
# 7. SpeechConfig reuse: built once in connect(), shared across TTS calls.
# """

# from __future__ import annotations

# import asyncio
# import audioop
# import base64
# import hashlib
# import json
# import logging
# import os
# import time
# import uuid
# from urllib.parse import parse_qs

# import numpy as np
# from asgiref.sync import sync_to_async
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.utils import timezone

# import azure.cognitiveservices.speech as speechsdk

# from agents.models import VoiceAgent
# from conversations.models import Conversation, Message
# from conversations.services.core.dialogue_engine import process_message
# from conversations.services.speech_service import create_speech_recognizer

# log = logging.getLogger(__name__)


# # ═══════════════════════════════════════════════════════════════════
# # Audio helpers
# # ══════════════════════════════════════════════════════════════════

# def decode_g711(data: bytes) -> bytes:
#     """G.711 mu-law -> 16-bit linear PCM."""
#     return audioop.ulaw2lin(data, 2)


# def encode_g711(data: bytes) -> bytes:
#     """16-bit linear PCM -> G.711 mu-law."""
#     return audioop.lin2ulaw(data, 2)

# def is_end_intent(text: str) -> bool:
#     text = text.lower().strip()

#     end_keywords = [
#         "bye", "goodbye", "ok bye", "okay bye",
#         "thank you", "thanks", "thanks a lot",
#         "that's all", "no thanks", "nothing else",
#         "i am done", "end call", "stop","no i donn't want"
#     ]

#     return any(keyword in text for keyword in end_keywords)


# def pcm_rms(data: bytes) -> float:
#     """Root-mean-square of raw 16-bit PCM bytes."""
#     if len(data) < 2:
#         return 0.0
#     arr = np.frombuffer(data, dtype=np.int16).astype(np.float32)
#     return float(np.sqrt(np.mean(arr ** 2)))


# def normalise_pcm(data: bytes, gain: float = 1.2) -> bytes:
#     """Scale PCM by gain and hard-clip to int16 range."""
#     arr = np.frombuffer(data, dtype=np.int16).astype(np.float32)
#     return np.clip(arr * gain, -32768, 32767).astype(np.int16).tobytes()


# def text_fingerprint(text: str) -> str:
#     """MD5 of lowercased, stripped text — used for dedup guards."""
#     return hashlib.md5(text.strip().lower().encode()).hexdigest()


# def build_ssml(text: str, voice: str) -> str:
#     """
#     Wrap plain text in SSML for better Azure Neural prosody.
#     Special characters are escaped so the XML stays valid.
#     """
#     safe = (
#         text.replace("&", "&amp;")
#             .replace("<", "&lt;")
#             .replace(">", "&gt;")
#             .replace('"', "&quot;")
#             .replace("'", "&apos;")
#     )
#     return (
#         f'<speak version="1.0" xml:lang="en-IN">'
#         f'<voice name="{voice}">'
#         f'<prosody rate="0%" pitch="0%">{safe}</prosody>'
#         f"</voice></speak>"
#     )


# # ═══════════════════════════════════════════════════════════════════
# # Database helpers  (sync ORM -> async wrappers)
# # ═══════════════════════════════════════════════════════════════════

# @sync_to_async
# def db_create_conversation(agent_id: str, session_id: str, user_number: str) -> Conversation:
#     return Conversation.objects.create(
#         agent_id=agent_id,
#         session_id=session_id,
#         user_number=user_number,
#     )


# @sync_to_async
# def db_save_message(conversation: Conversation, role: str, text: str) -> None:
#     last = (
#         Message.objects
#         .filter(conversation=conversation)
#         .order_by("-created_at")
#         .first()
#     )
#     if last and last.role == role and last.text.strip() == text.strip():
#         return  # skip exact duplicate
#     Message.objects.create(conversation=conversation, role=role, text=text)


# @sync_to_async
# def db_update_user_number(conversation: Conversation, number: str) -> None:
#     conversation.user_number = number
#     conversation.save(update_fields=["user_number"])


# @sync_to_async
# def db_close_conversation(conversation: Conversation) -> None:
#     conversation.ended_at = timezone.now()
#     conversation.save(update_fields=["ended_at"])


# @sync_to_async
# def db_get_agent_greeting(agent_id: str) -> str:
#     try:
#         agent = VoiceAgent.objects.get(id=agent_id)
#         company = agent.company_name or "our company"
#         suffix = "How can I assist you today?"
#         if agent.summary:
#             body = agent.summary.strip().rstrip(".")
#             return f"Hello, I am {agent.name} from {company}. {body}. {suffix}"
#         return f"Hello, I am {agent.name} from {company}. {suffix}"
#     except VoiceAgent.DoesNotExist:
#         return "Hello, how can I assist you today?"


# # ═══════════════════════════════════════════════════════════════════
# # Consumer
# # ═══════════════════════════════════════════════════════════════════

# class VoiceBotConsumer(AsyncWebsocketConsumer):
#     """
#     Async WebSocket consumer that bridges a telecom voice call with an
#     Azure STT -> LLM dialogue engine -> Azure TTS pipeline.

#     Override any class constant in a subclass to tune behaviour per agent
#     without touching the core logic.
#     """

#     # ── Audio ──────────────────────────────────────────────────────
#     JITTER_DELAY: int         = 3        # frames to buffer before processing
#     GAIN: float               = 1.2      # PCM normalisation gain
#     CORRUPT_RMS: float        = 20_000   # discard frames above this RMS (line noise)
#     STT_MIN_RMS: float        = 80       # minimum RMS to forward audio to STT

#     # ── Voice activity detection / silence fallback ────────────────
#     SPEECH_DETECT_RMS: float  = 200      # RMS to consider user speaking
#     SILENCE_TRIGGER_SEC: float = 1.2     # seconds of silence before fallback fires
#     MIN_WORD_COUNT: int        = 2       # ignore utterances shorter than this

#     # ── Interrupt detection ────────────────────────────────────────
#     INTERRUPT_RMS: float       = 400
#     INTERRUPT_HOLD_SEC: float  = 1.0     # user must speak this long to interrupt

#     # ── Dispatch dedup / cooldown ──────────────────────────────────
#     DISPATCH_COOLDOWN_SEC: float = 1.5   # min seconds between AI dispatches

#     # ── LLM ───────────────────────────────────────────────────────
#     MAX_LLM_RETRIES: int       = 2
#     LLM_TIMEOUT_SEC: float     = 30.0

#     # ── TTS ───────────────────────────────────────────────────────
#     TTS_VOICE: str               = "en-IN-NeerjaNeural"
#     TTS_SYNTHESIS_TIMEOUT: float = 20.0  # seconds to wait for Azure synthesis
#     TTS_CHUNK_BYTES: int         = 160   # G.711 bytes per WS frame (~20 ms)
#     TTS_CHUNK_SLEEP: float       = 0.02  # seconds between frames

#     # ── STT reconnect ─────────────────────────────────────────────
#     STT_MAX_RECONNECTS: int       = 5
#     STT_RECONNECT_BASE_SEC: float = 1.0  # exponential back-off base

#     # ─────────────────────────────────────────────────────────────────────
#     # connect
#     # ─────────────────────────────────────────────────────────────────────

#     async def connect(self) -> None:
#         self.loop = asyncio.get_running_loop()

#         params           = parse_qs(self.scope["query_string"].decode())
#         self.agent_id    = params.get("agent_id", [None])[0]
#         self.user_number = params.get("from", ["unknown"])[0]

#         if not self.agent_id:
#             log.warning("VoiceBot: rejected connection — missing agent_id")
#             await self.close()
#             return

#         self.session_id   = str(uuid.uuid4())
#         self.conversation = await db_create_conversation(
#             self.agent_id, self.session_id, self.user_number
#         )

#         # ── State flags ───────────────────────────────────────────
#         self.is_connected    = True
#         self.is_bot_speaking = False   # True ONLY while audio frames are streaming
#         self.is_processing   = False   # True while LLM call is in flight

#         # ── STT text holders ──────────────────────────────────────
#         self.partial_text = ""
#         self.final_text_queue: asyncio.Queue[str] = asyncio.Queue()

#         # ── Dedup guards ──────────────────────────────────────────
#         self.last_dispatched_fp = ""    # fingerprint of last text sent to LLM
#         self.last_dispatch_time = 0.0
#         self.last_bot_reply_fp  = ""    # fingerprint of last reply spoken

#         # ── Locks / background tasks ──────────────────────────────
#         self.processing_lock = asyncio.Lock()
#         self.tts_task: asyncio.Task | None = None

#         # ── Audio / VAD state ─────────────────────────────────────
#         self.jitter_buffer: list[bytes]       = []
#         self.speech_active                    = False
#         self.silence_start_time: float | None = None
#         self.interrupt_start_time: float | None = None

#         # ── STT ───────────────────────────────────────────────────
#         self._stt_reconnect_count = 0
#         self._speech_config = self._build_speech_config()   # FIX 7 — built once
#         await self._start_stt()

#         await self.accept()

#         greeting = await db_get_agent_greeting(self.agent_id)
#         self.tts_task = asyncio.create_task(self.send_tts(greeting))
#         self._final_consumer_task = asyncio.create_task(self._final_text_consumer())

#         log.info(
#             "VoiceBot connected | session=%s agent=%s number=%s",
#             self.session_id, self.agent_id, self.user_number,
#         )

#     # ─────────────────────────────────────────────────────────────────────
#     # SpeechConfig — built once and reused  (FIX 7)
#     # ─────────────────────────────────────────────────────────────────────

#     def _build_speech_config(self) -> speechsdk.SpeechConfig:
#         cfg = speechsdk.SpeechConfig(
#             subscription=os.environ["AZURE_SPEECH_KEY"],
#             region=os.environ["AZURE_SPEECH_REGION"],
#         )
#         cfg.speech_synthesis_voice_name = self.TTS_VOICE
#         cfg.set_speech_synthesis_output_format(
#             speechsdk.SpeechSynthesisOutputFormat.Raw8Khz16BitMonoPcm
#         )
#         return cfg

#     # ─────────────────────────────────────────────────────────────────────
#     # STT lifecycle
#     # ─────────────────────────────────────────────────────────────────────

#     async def _start_stt(self) -> None:
#         self.recognizer, self.push_stream = create_speech_recognizer()
#         self._attach_stt_callbacks()
#         self.recognizer.start_continuous_recognition_async()
#         log.debug("STT session started")

#     def _attach_stt_callbacks(self) -> None:
#         def on_recognizing(evt):
#             text = (evt.result.text or "").strip()
#             self.loop.call_soon_threadsafe(self._set_partial, text)

#         def on_recognized(evt):
#             text = (evt.result.text or "").strip()
#             if text:
#                 log.debug("STT final: %s", text)
#                 self.loop.call_soon_threadsafe(
#                     lambda: self.final_text_queue.put_nowait(text)
#                 )

#         def on_canceled(evt):
#             details = evt.result.cancellation_details
#             log.warning("STT canceled: %s — %s", details.reason, details.error_details)
#             self.loop.call_soon_threadsafe(
#                 lambda: asyncio.create_task(self._reconnect_stt())
#             )

#         def on_session_stopped(_evt):
#             log.info("STT session stopped — scheduling reconnect")
#             self.loop.call_soon_threadsafe(
#                 lambda: asyncio.create_task(self._reconnect_stt())
#             )

#         self.recognizer.recognizing.connect(on_recognizing)
#         self.recognizer.recognized.connect(on_recognized)
#         self.recognizer.canceled.connect(on_canceled)
#         self.recognizer.session_stopped.connect(on_session_stopped)

#     async def _reconnect_stt(self) -> None:
#         """Exponential back-off reconnect when the Azure STT session drops."""
#         if not self.is_connected:
#             return
#         if self._stt_reconnect_count >= self.STT_MAX_RECONNECTS:
#             log.error("STT: max reconnect attempts (%d) reached", self.STT_MAX_RECONNECTS)
#             return

#         delay = self.STT_RECONNECT_BASE_SEC * (2 ** self._stt_reconnect_count)
#         self._stt_reconnect_count += 1
#         log.info(
#             "STT reconnecting in %.1fs (attempt %d/%d)",
#             delay, self._stt_reconnect_count, self.STT_MAX_RECONNECTS,
#         )
#         await asyncio.sleep(delay)

#         for attr, method in [
#             ("recognizer", "stop_continuous_recognition_async"),
#             ("push_stream", "close"),
#         ]:
#             try:
#                 getattr(getattr(self, attr), method)()
#             except Exception:
#                 pass

#         await self._start_stt()
#         self._stt_reconnect_count = 0   # reset counter on successful reconnect
#         log.info("STT reconnected successfully")

#     def _set_partial(self, text: str) -> None:
#         """Called thread-safely from the Azure SDK callback thread."""
#         self.partial_text = text

#     # ─────────────────────────────────────────────────────────────────────
#     # Background consumer — processes Azure final results
#     # ─────────────────────────────────────────────────────────────────────

#     async def _final_text_consumer(self) -> None:
#         """
#         Primary trigger for AI replies.
#         Runs in a dedicated task — never races with audio frame processing.
#         """
#         while self.is_connected:
#             try:
#                 text = await asyncio.wait_for(
#                     self.final_text_queue.get(), timeout=1.0
#                 )
#             except asyncio.TimeoutError:
#                 continue
#             except Exception:
#                 break

#             if not text:
#                 continue

#             if self.is_bot_speaking or self.is_processing:
#                 log.debug("Final skipped (bot busy): %s", text)
#                 continue

#             if not self._passes_dispatch_gate(text):
#                 continue

#             log.info("Dispatching to AI (Azure final): %s", text)
#             await self._dispatch_to_ai(text)

#     # ─────────────────────────────────────────────────────────────────────
#     # receive
#     # ─────────────────────────────────────────────────────────────────────

#     async def receive(self, text_data: str = None, bytes_data: bytes = None) -> None:
#         if not text_data:
#             return
#         try:
#             data  = json.loads(text_data)
#             event = data.get("event")

#             if event == "start":
#                 try:
#                     number = data["start"]["customParameters"]["callerNumber"]
#                     self.user_number = number
#                     await db_update_user_number(self.conversation, number)
#                 except (KeyError, TypeError):
#                     pass

#             elif event == "media":
#                 await self._handle_audio_chunk(data)

#             elif event == "stop":
#                 log.info("Telecom stop event received")

#         except Exception:
#             log.exception("Error in receive()")

#     # ─────────────────────────────────────────────────────────────────────
#     # Audio frame processing
#     # ─────────────────────────────────────────────────────────────────────

#     async def _handle_audio_chunk(self, data: dict) -> None:
#         try:
#             payload = base64.b64decode(data["media"]["payload"])
#         except Exception:
#             return

#         pcm = decode_g711(payload)
#         pcm = normalise_pcm(pcm, self.GAIN)

#         if len(pcm) % 2 != 0:
#             pcm = pcm[:-1]

#         # Jitter buffer — smooths out packet bursts from the telecom layer
#         self.jitter_buffer.append(pcm)
#         if len(self.jitter_buffer) < self.JITTER_DELAY:
#             return
#         pcm = self.jitter_buffer.pop(0)

#         rms = pcm_rms(pcm)

#         # Discard corrupt / overloaded frames (line-noise spikes)
#         if rms > self.CORRUPT_RMS:
#             return

#         # ── FIX 1: is_bot_speaking checked BEFORE writing to STT ────────
#         # The telecom line echoes the bot's outgoing audio back to us.
#         # Writing that echo to the STT push stream causes Azure to transcribe
#         # the bot's own voice and fire spurious AI replies.
#         # Fix: skip the STT feed entirely while the bot is streaming audio.
#         if self.is_bot_speaking:
#             await self._check_interrupt(rms)
#             return  # echo — do not forward to STT

#         # Forward genuine user audio to STT
#         if rms > self.STT_MIN_RMS:
#             try:
#                 self.push_stream.write(pcm)
#             except Exception:
#                 log.warning("push_stream.write() failed — STT may have dropped")

#         # Update VAD and fire fallback trigger if silence threshold is crossed
#         await self._vad_tick(rms)

#     # ─────────────────────────────────────────────────────────────────────
#     # VAD — silence-based fallback trigger
#     # ─────────────────────────────────────────────────────────────────────

#     async def _vad_tick(self, rms: float) -> None:
#         """
#         Secondary / fallback dispatch trigger.
#         Fires only when Azure's recognized event has not arrived and the
#         user has been silent long enough after speaking.
#         """
#         if rms > self.SPEECH_DETECT_RMS:
#             self.speech_active      = True
#             self.silence_start_time = None
#             return

#         if not self.speech_active:
#             return

#         now = time.monotonic()
#         if self.silence_start_time is None:
#             self.silence_start_time = now
#             return

#         if now - self.silence_start_time < self.SILENCE_TRIGGER_SEC:
#             return

#         # Silence threshold crossed — reset VAD
#         self.speech_active      = False
#         self.silence_start_time = None

#         # Only fire if Azure hasn't already handled this utterance
#         if (
#             not self.is_bot_speaking
#             and not self.is_processing
#             and self.partial_text
#             and self.final_text_queue.empty()
#         ):
#             text = self.partial_text.strip()
#             self.partial_text = ""

#             if self._passes_dispatch_gate(text):
#                 log.info("Dispatching to AI (VAD fallback): %s", text)
#                 await self._dispatch_to_ai(text)

#     # ─────────────────────────────────────────────────────────────────────
#     # Interrupt detection
#     # ─────────────────────────────────────────────────────────────────────

#     async def _check_interrupt(self, rms: float) -> None:
#         if rms < self.INTERRUPT_RMS:
#             self.interrupt_start_time = None
#             return

#         now = time.monotonic()
#         if self.interrupt_start_time is None:
#             self.interrupt_start_time = now
#             return

#         if now - self.interrupt_start_time < self.INTERRUPT_HOLD_SEC:
#             return

#         log.info("Interrupt detected — stopping TTS")
#         self.interrupt_start_time = None
#         await self._stop_tts()

#     async def _stop_tts(self) -> None:
#         self.is_bot_speaking = False
#         self.jitter_buffer.clear()
#         if self.tts_task and not self.tts_task.done():
#             self.tts_task.cancel()
#             try:
#                 await self.tts_task
#             except asyncio.CancelledError:
#                 pass

#     # ─────────────────────────────────────────────────────────────────────
#     # Dispatch gate — dedup + cooldown
#     # ─────────────────────────────────────────────────────────────────────

#     def _passes_dispatch_gate(self, text: str) -> bool:
#         if len(text.split()) < self.MIN_WORD_COUNT:
#             log.debug("Gate: too short — %s", text)
#             return False
#         fp = text_fingerprint(text)
#         if fp == self.last_dispatched_fp:
#             log.debug("Gate: duplicate — %s", text)
#             return False
#         if time.monotonic() - self.last_dispatch_time < self.DISPATCH_COOLDOWN_SEC:
#             log.debug("Gate: cooldown — %s", text)
#             return False
#         self.last_dispatched_fp = fp
#         self.last_dispatch_time = time.monotonic()
#         return True

#     async def _dispatch_to_ai(self, text: str) -> None:
#         self.is_processing = True
#         self.partial_text  = ""
#         try:
#             async with self.processing_lock:
#                 await self.handle_ai_reply(text)
#         except Exception:
#             log.exception("Error in _dispatch_to_ai")
#         finally:
#             self.is_processing = False

#     # ─────────────────────────────────────────────────────────────────────
#     # AI reply
#     # ─────────────────────────────────────────────────────────────────────

#     async def handle_ai_reply(self, text: str) -> None:
#         text = text.strip()
#         if not text:
#             return
        

#         normalized = text.lower().strip()

#         # ================= 🔥 END CALL LOGIC =================
#         if is_end_intent(normalized):
#             log.info("📴 END INTENT DETECTED: %s", text)

#             await db_save_message(self.conversation, "user", text)

#             farewell = "Thank you for calling. Have a great day!"

#             await db_save_message(self.conversation, "bot", farewell)

#             # Stop any running TTS
#             await self._stop_tts()

#             # Speak farewell
#             await self.send_tts(farewell)

#             # Close DB conversation
#             await db_close_conversation(self.conversation)

#             # 🔥 Send telecom stop event
#             await self.send(text_data=json.dumps({
#                 "event": "stop"
#             }))

#             # 🔥 CRITICAL: stop background loop
#             self.is_connected = False

#             # Close websocket
#             await self.close()
#             return
#         # =====================================================

#         log.info("AI input: %s", text)
#         await db_save_message(self.conversation, "user", text)

#         reply = await self._call_llm_with_retry(text)

#         if not reply:
#             log.warning("LLM returned empty reply for input: %s", text)
#             return

#         # Prevent saying the exact same sentence twice in a row
#         reply_fp = text_fingerprint(reply)
#         if reply_fp == self.last_bot_reply_fp:
#             log.debug("Bot reply deduped: %s", reply)
#             return
#         self.last_bot_reply_fp = reply_fp

#         await db_save_message(self.conversation, "bot", reply)
#         log.info("Bot reply: %s", reply)

#         await self._stop_tts()
#         self.tts_task = asyncio.create_task(self.send_tts(reply))

#     async def _call_llm_with_retry(self, text: str) -> str | None:
#         for attempt in range(1, self.MAX_LLM_RETRIES + 1):
#             try:
#                 reply, _ = await asyncio.wait_for(
#                     sync_to_async(process_message)(
#                         self.agent_id, text, self.session_id
#                     ),
#                     timeout=self.LLM_TIMEOUT_SEC,
#                 )
#                 return reply
#             except asyncio.TimeoutError:
#                 log.warning("LLM timeout (attempt %d/%d)", attempt, self.MAX_LLM_RETRIES)
#             except Exception:
#                 log.exception("LLM error (attempt %d/%d)", attempt, self.MAX_LLM_RETRIES)
#             if attempt < self.MAX_LLM_RETRIES:
#                 await asyncio.sleep(0.5 * attempt)
#         return None

#     # ─────────────────────────────────────────────────────────────────────
#     # TTS
#     # ─────────────────────────────────────────────────────────────────────

#     async def send_tts(self, text: str) -> None:
#         """
#         Synthesise text to speech and stream G.711 chunks over the WebSocket.

#         FIX 2: partial_text cleared + queue flushed at entry.
#         FIX 3: queue flushed again just before audio streaming begins.
#         FIX 4: is_bot_speaking=True set AFTER synthesis completes, not before.
#                User speech continues to be accepted during the synthesis wait.
#         FIX 6: asyncio.get_running_loop() used (not get_event_loop).
#         FIX 7: self._speech_config reused (built once in connect()).
#         """
#         # FIX 2 — clear stale partials and any echo transcriptions queued so far
#         self.partial_text = ""
#         self._flush_final_queue()

#         try:
#             # FIX 7 — reuse the SpeechConfig built in connect()
#             synthesizer = speechsdk.SpeechSynthesizer(
#                 speech_config=self._speech_config,
#                 audio_config=None,
#             )

#             ssml = build_ssml(text, self.TTS_VOICE)
#             loop = asyncio.get_running_loop()   # FIX 6

#             # ── Synthesis phase ────────────────────────────────────────
#             # is_bot_speaking is still FALSE here.
#             # User speech is being accepted and forwarded to STT normally.  FIX 4
#             log.debug("TTS synthesising: %d chars", len(text))
#             result = await asyncio.wait_for(
#                 loop.run_in_executor(
#                     None,
#                     lambda: synthesizer.speak_ssml_async(ssml).get(),
#                 ),
#                 timeout=self.TTS_SYNTHESIS_TIMEOUT,
#             )

#             if result.reason == speechsdk.ResultReason.Canceled:
#                 details = result.cancellation_details
#                 log.error(
#                     "TTS canceled: %s — %s", details.reason, details.error_details
#                 )
#                 return

#             pcm = result.audio_data

#             # Strip WAV header if Azure prepended one
#             if pcm[:4] == b"RIFF":
#                 pcm = pcm[44:]
#             if len(pcm) % 2 != 0:
#                 pcm = pcm[:-1]

#             ulaw = encode_g711(pcm)

#             # ── FIX 4: set flag HERE — synthesis done, streaming begins ─
#             self.is_bot_speaking = True
#             # FIX 3 — drain anything that piled up during the synthesis wait
#             self._flush_final_queue()

#             log.debug("TTS streaming %d G.711 bytes", len(ulaw))

#             for i in range(0, len(ulaw), self.TTS_CHUNK_BYTES):
#                 if not self.is_bot_speaking:
#                     log.info("TTS streaming stopped mid-stream (interrupted)")
#                     break

#                 chunk   = ulaw[i : i + self.TTS_CHUNK_BYTES]
#                 payload = base64.b64encode(chunk).decode()
#                 await self.send(text_data=json.dumps({
#                     "event": "media",
#                     "media": {"payload": payload},
#                 }))
#                 await asyncio.sleep(self.TTS_CHUNK_SLEEP)

#         except asyncio.CancelledError:
#             log.info("TTS task cancelled")
#             raise  # must re-raise so asyncio can clean up the task

#         except asyncio.TimeoutError:
#             log.error(
#                 "TTS synthesis timed out after %.0fs", self.TTS_SYNTHESIS_TIMEOUT
#             )

#         except Exception:
#             log.exception("TTS error")

#         finally:
#             self.is_bot_speaking = False

#     def _flush_final_queue(self) -> None:
#         """Drain all pending items from final_text_queue (discard echo residue)."""
#         flushed = 0
#         while not self.final_text_queue.empty():
#             try:
#                 self.final_text_queue.get_nowait()
#                 flushed += 1
#             except asyncio.QueueEmpty:
#                 break
#         if flushed:
#             log.debug("Flushed %d stale item(s) from final_text_queue", flushed)

#     # ─────────────────────────────────────────────────────────────────────
#     # disconnect
#     # ─────────────────────────────────────────────────────────────────────

#     async def disconnect(self, close_code: int) -> None:
#         log.info(
#             "VoiceBot disconnecting | code=%s session=%s",
#             close_code, self.session_id,
#         )
#         self.is_connected = False

#         # Cancel all background tasks and wait for them to finish cleanly
#         tasks: list[asyncio.Task] = []
#         for attr in ("_final_consumer_task", "tts_task"):
#             task: asyncio.Task | None = getattr(self, attr, None)
#             if task and not task.done():
#                 task.cancel()
#                 tasks.append(task)

#         if tasks:
#             await asyncio.gather(*tasks, return_exceptions=True)

#         # Stop STT recognizer and close push stream
#         for attr, method in [
#             ("recognizer", "stop_continuous_recognition_async"),
#             ("push_stream", "close"),
#         ]:
#             obj = getattr(self, attr, None)
#             if obj:
#                 try:
#                     getattr(obj, method)()
#                 except Exception:
#                     pass

#         # Mark conversation as ended in the database
#         if hasattr(self, "conversation"):
#             try:
#                 await db_close_conversation(self.conversation)
#             except Exception:
#                 log.exception("Failed to close conversation in DB")

#         log.info("VoiceBot disconnected cleanly | session=%s", self.session_id)



