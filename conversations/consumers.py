# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from conversations.services.core.dialogue_engine import process_message


# class VoiceBotConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         await self.accept()

#         await self.send(json.dumps({
#             "message": "Connected to Voice Bot"
#         }))


#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         agent_id = data.get("agent_id")
#         message = data.get("message")
#         session_id = data.get("session_id")

#         # Call your existing bot engine
#         response = process_message(
#             agent_id=agent_id,
#             message=message,
#             session_id=session_id
#         )

#         await self.send(json.dumps(response))


from urllib.parse import parse_qs
import audioop
from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
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


# ==============================
# ✅ STEP 1 — PUT HERE (ABOVE CLASS)
# ==============================

# @sync_to_async
# def get_agent_summary(agent_id):
#     try:
#         agent = VoiceAgent.objects.get(id=agent_id)

#         return (
#             agent.summary
#             or f"Hello, I am {agent.name} from {agent.company_name or 'our company'}. How can I assist you?"
#         )

#     except VoiceAgent.DoesNotExist:
#         return "Hello, how can I help you?"

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




# def create_rtp_packet(payload, seq, ts, ssrc=12345):
#     header = struct.pack(
#         "!BBHII",
#         0x80,   # Version
#         0,      # Payload type (PCMU)
#         seq,    # Sequence number
#         ts,     # Timestamp
#         ssrc    # Sync source
#     )
#     return header + payload



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



def is_silence(chunk, threshold=150):
    import audioop
    rms = audioop.rms(chunk, 2)  # PCM energy
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

    # async def connect(self):
    #     await self.accept()

    #     await self.send(json.dumps({
    #         "message": "Connected to Voice Bot"
    #     }))


    async def connect(self):
        query_string = self.scope["query_string"].decode()
        params = parse_qs(query_string)

        self.agent_id = params.get("agent_id", [None])[0]

        if not self.agent_id:
            await self.close()
            return

        open("debug_stream_ulaw.raw", "wb").close()
        open("debug_full_ulaw.raw", "wb").close()

        # ✅ Create Azure STT
        self.recognizer, self.audio_stream = create_speech_recognizer()
        self.audio_buffer = b""

        # ✅ Handle speech result
        # def handle_result(evt):
        #     print("STT EVENT TRIGGERED")
        #     if evt.result.text:
        #         print("REAL STT:", evt.result.text)

        #         # Call AI
        #         reply, session_id = process_message(
        #             self.agent_id,
        #             evt.result.text,
        #             None
        #         )

        #         # Send TTS async
        #         asyncio.create_task(self.send_tts(reply))

        def handle_result(evt):
            if evt.result.text:
                asyncio.create_task(self.handle_ai_reply(evt.result.text))



        # Attach event
        self.recognizer.recognized.connect(handle_result)

        # Start continuous STT
        self.recognizer.start_continuous_recognition()
        await self.accept()

        # 🔥 STEP 2.1 — SEND GREETING TO TELECOM
        summary_text = await get_agent_summary(self.agent_id)

        print("📢 Sending summary:", summary_text)

        # small delay for socket readiness
        await asyncio.sleep(0.2)

        # asyncio.create_task(self.send_tts(summary_text))
        # asyncio.create_task(self.safe_tts_stream(summary_text))
        await self.send_tts(summary_text)
        # optional debug message
        await self.send(text_data=json.dumps({
            "message": f"Connected to agent {self.agent_id}"
        }))

    async def receive(self, text_data=None, bytes_data=None):

        # Ignore text
        if text_data:
            return

        # AUDIO (RTP)
        if bytes_data:
            try:
                print("🔥 Received RTP packet")

                # Remove RTP header
                audio_payload = bytes_data[12:]
                print("Audio payload length:", len(audio_payload))

                # Assign PCM
                # pcm_audio = audio_payload
                pcm_audio = decode_g711(audio_payload)

                # Normalize (safe)
                if len(pcm_audio) % 2 != 0:
                    pcm_audio = pcm_audio[:-1]

                print("PCM audio length:", len(pcm_audio))

                # ✅ 🔥 CRITICAL FIX — BUFFERING
                self.audio_buffer += pcm_audio

                # Send only when enough data collected
                if len(self.audio_buffer) > 3200:
                    print("📦 Sending buffered audio:", len(self.audio_buffer))

                    self.audio_stream.write(self.audio_buffer)

                    # Clear buffer
                    self.audio_buffer = b""

            except Exception as e:
                print("❌ Error in receive:", e)


    async def handle_ai_reply(self, text):
            reply, session_id = process_message(
                self.agent_id,
                text,
                None
            )

            await self.send_tts(reply)

    async def send_tts(self, text):
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"),
            region=os.getenv("AZURE_SPEECH_REGION")
        )

        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Raw8Khz16BitMonoPcm
        )

        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None
        )

        print("Converting text to audio...")

        result = synthesizer.speak_text_async(text).get()
        pcm_audio = result.audio_data

        # 🔥 DEBUG START (ADD HERE)
        print("========== TTS DEBUG ==========")
        print("TTS TEXT:", text)
        print("PCM LENGTH:", len(pcm_audio))
        print("================================")
        # 🔥 DEBUG END

        # pcm_audio = pcm_audio[44:]
        if pcm_audio[:4] == b'RIFF':
            pcm_audio = pcm_audio[44:]
        print("PCM reply length:", len(pcm_audio))

        # 🔥 ADD THIS HERE
        if len(pcm_audio) % 2 != 0:
            pcm_audio = pcm_audio[:-1]

        # ulaw_audio = encode_g711(pcm_audio)

        FRAME_PCM = 320  # 20ms PCM (160 samples * 2 bytes)

        processed_pcm = b""

        for i in range(0, len(pcm_audio), FRAME_PCM):
            frame = pcm_audio[i:i+FRAME_PCM]

            if len(frame) < FRAME_PCM:
                frame = frame.ljust(FRAME_PCM, b'\x00')

            if is_silence(frame):
                # 🔥 replace with pure silence
                # frame = b'\x00' * FRAME_PCM
                # μ-law silence = 0xFF
                silence_ulaw = b'\xFF' * 160
                processed_pcm += audioop.ulaw2lin(silence_ulaw, 2)
                continue

            processed_pcm += frame
        # processed_pcm = audioop.mul(processed_pcm, 2, 0.95)

        ulaw_audio = encode_g711(processed_pcm)

        # BEFORE loop
        with open("debug_full_ulaw.raw", "wb") as f:
            f.write(ulaw_audio)
        seq = 0
        timestamp = 0

        # start_time = time.time()
        packet_duration = 0.02
        next_send_time = time.time()

        for i in range(0, len(ulaw_audio), 160):
            chunk = ulaw_audio[i:i+160]

            if len(chunk) < 160:
                chunk = chunk.ljust(160, b'\x00')

            with open("debug_stream_ulaw.raw", "ab") as f:
                f.write(chunk)

            rtp_packet = create_rtp_packet(
                chunk,
                seq=seq,
                ts=timestamp
            )

            try:
                await self.send(bytes_data=rtp_packet)
            except Exception as e:
                print("Send failed:", e)
                break

            seq += 1
            timestamp += 160

            # # 🔥 CRITICAL FIX
            await asyncio.sleep(0)   # yield control to event loop

            # # pacing (keep this)
            # await asyncio.sleep(0.02)

            # 🔥 precise timing
            # expected_time = seq * 0.02
            # actual_time = time.time() - start_time

            # if expected_time > actual_time:
            #     await asyncio.sleep(expected_time - actual_time)


            # 🔥 NEW TIMING LOGIC (replace your old one)
            next_send_time += packet_duration
            sleep_time = next_send_time - time.time()

            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            else:
                # 🔥 resync if drift happens
                next_send_time = time.time()
    
    # ✅ PUT IT HERE (same level)
    async def safe_tts_stream(self, text):
        try:
            await self.send_tts(text)
        except Exception as e:
            print("TTS stream error:", e)
    
    async def disconnect(self, close_code):
        print("🔌 WebSocket disconnected")

        if hasattr(self, "tts_task"):
            self.tts_task.cancel()

    