# import os
# import azure.cognitiveservices.speech as speechsdk

# def create_speech_recognizer():
#     speech_config = speechsdk.SpeechConfig(
#         subscription=os.getenv("AZURE_SPEECH_KEY"),
#         region=os.getenv("AZURE_SPEECH_REGION")
#     )

#     # OPTIONAL but safe
#     speech_config.speech_recognition_language = "en-IN"

#     audio_stream = speechsdk.audio.PushAudioInputStream()
#     audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

#     recognizer = speechsdk.SpeechRecognizer(
#         speech_config=speech_config,
#         audio_config=audio_config
#     )

#     return recognizer, audio_stream



import azure.cognitiveservices.speech as speechsdk
import os

def create_speech_recognizer():
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION")
    )

    speech_config.speech_recognition_language = "en-IN"

    stream_format = speechsdk.audio.AudioStreamFormat(
        samples_per_second=8000,
        bits_per_sample=16,
        channels=1
    )

    push_stream = speechsdk.audio.PushAudioInputStream(stream_format)

    audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    return recognizer, push_stream