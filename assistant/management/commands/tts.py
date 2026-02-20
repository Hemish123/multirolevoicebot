from pathlib import Path
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    raise RuntimeError("AZURE_SPEECH_KEY / AZURE_SPEECH_REGION not set")

_synthesizer = None

def _get_synthesizer():
    global _synthesizer
    if _synthesizer is None:
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION,
        )
        speech_config.speech_synthesis_voice_name = "en-IN-NeerjaNeural"
        _synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config
        )
    return _synthesizer

def speak(text: str):
    if not text:
        return
    print("🤖 Agent:", text)
    synthesizer = _get_synthesizer()
    synthesizer.speak_text_async(text).get()