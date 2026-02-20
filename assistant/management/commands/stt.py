from pathlib import Path
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load .env from project root
ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
    raise RuntimeError("AZURE_SPEECH_KEY / AZURE_SPEECH_REGION not set")

def listen() -> str:
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION,
    )
    speech_config.speech_recognition_language = "en-US"

    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    print("🎧 Listening...")
    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("🗣 You:", result.text)
        return result.text.strip()

    print("⏳ No speech recognized")
    return ""