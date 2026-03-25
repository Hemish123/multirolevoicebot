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

#=============================================================================
#=============================================================================

# import azure.cognitiveservices.speech as speechsdk
# import os

# def create_speech_recognizer():
#     speech_config = speechsdk.SpeechConfig(
#         subscription=os.getenv("AZURE_SPEECH_KEY"),
#         region=os.getenv("AZURE_SPEECH_REGION")
#     )

#     speech_config.speech_recognition_language = "en-IN"

#     stream_format = speechsdk.audio.AudioStreamFormat(
#         samples_per_second=8000,
#         bits_per_sample=16,
#         channels=1
#     )

#     push_stream = speechsdk.audio.PushAudioInputStream(stream_format)

#     audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

#     recognizer = speechsdk.SpeechRecognizer(
#         speech_config=speech_config,
#         audio_config=audio_config
#     )

#     return recognizer, push_stream


















#doneeeeeeeeeeeeeee for callllllllllllllllllllllllll 



import azure.cognitiveservices.speech as speechsdk
import os

def create_speech_recognizer():
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("AZURE_SPEECH_KEY"),
        region=os.getenv("AZURE_SPEECH_REGION")
    )

    # ✅ FIX 1: Match language to your TTS voice (en-IN-NeerjaNeural)
    speech_config.speech_recognition_language = "en-IN"

    # ✅ FIX 2: Tell Azure this is telephony/phone audio (8kHz compressed)
    speech_config.set_property_by_name("SPEECH-RecoModelKey", "telephony")

    # ✅ FIX 3: Give users more time before Azure cuts them off
    speech_config.set_property(
        speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "1500"
    )
    speech_config.set_property(
        speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "10000"
    )
    speech_config.set_property(
        speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, "800"
    )

    # ✅ FIX 4: Tell Azure exact audio format (8kHz, 16bit, mono = phone audio)
    audio_format = speechsdk.audio.AudioStreamFormat(
        samples_per_second=8000,
        bits_per_sample=16,
        channels=1
    )

    push_stream = speechsdk.audio.PushAudioInputStream(stream_format=audio_format)
    audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    return recognizer, push_stream














# import azure.cognitiveservices.speech as speechsdk
# import os

# def create_speech_recognizer(mode="telephony"):
#     """
#     mode = "telephony" → for Twilio/phone calls (8kHz)
#     mode = "web"       → for browser mic (16kHz)
#     """
#     speech_config = speechsdk.SpeechConfig(
#         subscription=os.getenv("AZURE_SPEECH_KEY"),
#         region=os.getenv("AZURE_SPEECH_REGION")
#     )

#     speech_config.speech_recognition_language = "en-IN"

#     speech_config.set_property(
#         speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "1500"
#     )
#     speech_config.set_property(
#         speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "10000"
#     )
#     speech_config.set_property(
#         speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, "800"
#     )

#     if mode == "telephony":
#         # ✅ Phone/Twilio — 8kHz compressed audio
#         audio_format = speechsdk.audio.AudioStreamFormat(
#             samples_per_second=8000,
#             bits_per_sample=16,
#             channels=1
#         )
#     else:
#         # ✅ Web browser mic — 16kHz standard audio
#         audio_format = speechsdk.audio.AudioStreamFormat(
#             samples_per_second=16000,
#             bits_per_sample=16,
#             channels=1
#         )

#     push_stream = speechsdk.audio.PushAudioInputStream(stream_format=audio_format)
#     audio_config = speechsdk.audio.AudioConfig(stream=push_stream)

#     recognizer = speechsdk.SpeechRecognizer(
#         speech_config=speech_config,
#         audio_config=audio_config
#     )

#     return recognizer, push_stream