# # from django.shortcuts import render

# # # Create your conversations views here.
# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from agents.models import VoiceAgent
# # from .models import ConversationLog
# # from knowledge.services.retriever import retrieve_relevant_chunks
# # from .services.azure_openai_service import generate_response

# # class ChatAPIView(APIView):
# #     authentication_classes = []
# #     permission_classes = []

# #     def post(self, request, agent_id):
# #         api_key = request.headers.get("X-API-KEY")

# #         agent = VoiceAgent.objects.filter(
# #             id=agent_id,
# #             api_key=api_key,
# #             is_active=True
# #         ).first()

# #         if not agent:
# #             return Response({"error": "Unauthorized"}, status=401)

# #         message = request.data.get("message")
# #         if not message:
# #             return Response({"error": "Message required"}, status=400)
        
# #         # 🔎 Retrieve knowledge
# #         context = retrieve_relevant_chunks(agent, message)
# #         print("MESSAGE:", message)
# #         print("RETRIEVED CONTEXT:", context)
# #         enhanced_prompt = f"""
# # {agent.resolved_prompt}

# # Use the following knowledge context to answer the user's question.
# # If the answer is not in the context, say you don't have that information.

# # Knowledge Context:
# # {context}
# # """

# #         # 🤖 Call Azure OpenAI
# #         reply = generate_response(enhanced_prompt, message)

# #         ConversationLog.objects.create(
# #             agent=agent,
# #             user_message=message,
# #             agent_reply=reply
# #         )

# #         return Response({
# #             "agent": agent.name,
# #             "reply": reply
# #         })























# from rest_framework.views import APIView
# from rest_framework.response import Response
# from agents.models import VoiceAgent
# from .models import ConversationLog
# from knowledge.services.retriever import retrieve_relevant_chunks
# from .services.azure_openai_service import generate_response


# class ChatAPIView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def post(self, request, agent_id):
#         api_key = request.headers.get("X-API-KEY")

#         agent = VoiceAgent.objects.filter(
#             id=agent_id,
#             api_key=api_key,
#             is_active=True
#         ).first()

#         if not agent:
#             return Response({"error": "Unauthorized"}, status=401)

#         message = request.data.get("message")
#         if not message:
#             return Response({"error": "Message required"}, status=400)

#         # 🔎 Retrieve knowledge
#         context = retrieve_relevant_chunks(agent, message)

#         # 🚫 HARD GUARDRAIL: no context → no answer
#         if not context.strip():
#             reply = "This information is not mentioned in the uploaded document."
#         else:
#             system_prompt = f"""
# {agent.resolved_prompt}

# IMPORTANT RULES:
# - Answer ONLY using the Knowledge Context below
# - If the answer is not explicitly present, say:
#   "This information is not mentioned in the uploaded document."
# - Do NOT use outside knowledge
# - Do NOT guess or assume

# Knowledge Context:
# {context}
# """
#             reply = generate_response(system_prompt, message)

#         ConversationLog.objects.create(
#             agent=agent,
#             user_message=message,
#             agent_reply=reply
#         )

#         return Response({
#             "agent": agent.name,
#             "reply": reply
#         })







# from rest_framework.views import APIView
# from rest_framework.response import Response
# from agents.models import VoiceAgent
# from conversations.services.core.dialogue_engine import process_message
# from rest_framework.permissions import AllowAny
# from django.shortcuts import render



# def demo_page(request):
#     return render(request, "demo_chat.html")


# class ChatAPIView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def post(self, request, agent_id):
#         api_key = request.headers.get("X-API-KEY")

#         agent = VoiceAgent.objects.filter(
#             id=agent_id,
#             api_key=api_key,
#             is_active=True
#         ).first()

#         if not agent:
#             return Response({"error": "Unauthorized"}, status=401)

#         message = request.data.get("message")
#         if not message:
#             return Response({"error": "Message required"}, status=400)

#         # 🔹 Get session_id from request (if continuing conversation)
#         session_id = request.data.get("session_id")

#         # 🔹 Call conversation engine
#         reply, session_id = process_message(
#             agent=agent,
#             message=message,
#             session_id=session_id
#         )

#         return Response({
#             "agent": agent.name,
#             "reply": reply,
#             "session_id": session_id
#         })
    


# class BotListAPIView(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def get(self, request):
#         bots = VoiceAgent.objects.filter(
#             is_active=True
#         ).select_related("industry", "role_template")

#         data = []

#         for bot in bots:
#             data.append({
#                 "id": bot.id,
#                 "name": bot.name,
#                 "industry": bot.industry.name,
#                 "role": bot.role_template.role_name if bot.role_template else None,
#                 "company_name": bot.company_name,
#             })

#         return Response({"bots": data})


# class DemoChatAPIView(APIView):
#     permission_classes = [AllowAny]
#     authentication_classes = []

#     def post(self, request):
#         industry_id = request.data.get("industry_id")
#         role_id = request.data.get("role_id")
#         message = request.data.get("message")
#         session_id = request.data.get("session_id")

#         if not all([industry_id, role_id, message]):
#             return Response(
#                 {"error": "industry_id, role_id and message are required"},
#                 status=400
#             )

#         # 🔎 Resolve Demo Bot Internally
#         bot = VoiceAgent.objects.filter(
#             industry_id=industry_id,
#             role_template_id=role_id,
#             is_demo=True,
#             is_active=True
#         ).first()

#         if not bot:
#             return Response(
#                 {"error": "No demo bot found for selected role"},
#                 status=404
#             )

#         # 🧠 Call existing conversation engine
#         reply, session_id = process_message(
#             agent=bot,
#             message=message,
#             session_id=session_id
#         )

#         return Response({
#             "reply": reply,
#             "session_id": session_id
#         })








import tempfile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.shortcuts import render

from agents.models import VoiceAgent
from assistant.management.commands.stt import speech_to_text
from conversations.services.core.dialogue_engine import process_message
from assistant.management.commands.tts import synthesize_to_base64
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


# ======================================================
# DEMO PAGE
# ======================================================

def demo_page(request):
    return render(request, "demo_chat.html")


# ======================================================
# AUTHENTICATED AGENT CHAT (UNCHANGED)
# ======================================================

class ChatAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, agent_id):
        api_key = request.headers.get("X-API-KEY")

        agent = VoiceAgent.objects.filter(
            id=agent_id,
            api_key=api_key,
            is_active=True
        ).first()

        if not agent:
            return Response({"error": "Unauthorized"}, status=401)

        message = request.data.get("message")
        if not message:
            return Response({"error": "Message required"}, status=400)

        session_id = request.data.get("session_id")

        reply, session_id = process_message(
            agent=agent,
            message=message,
            session_id=session_id
        )

        return Response({
            "agent": agent.name,
            "reply": reply,
            "session_id": session_id
        })


# ======================================================
# BOT LIST (UNCHANGED)
# ======================================================

class BotListAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        bots = VoiceAgent.objects.filter(
            is_active=True
        ).select_related("industry", "role_template")

        data = []

        for bot in bots:
            data.append({
                "id": bot.id,
                "name": bot.name,
                "industry": bot.industry.name,
                "role": bot.role_template.role_name if bot.role_template else None,
                "company_name": bot.company_name,
            })

        return Response({"bots": data})


# ======================================================
# DEMO CHAT (FIXED + AZURE TTS)
# ======================================================

# class DemoChatAPIView(APIView):
#     permission_classes = [AllowAny]
#     authentication_classes = []

#     def post(self, request):
#         industry_id = request.data.get("industry_id")
#         role_id = request.data.get("role_id")
#         message = request.data.get("message")
#         session_id = request.data.get("session_id")

#         if not industry_id or not role_id:
#             return Response(
#                 {"error": "industry_id and role_id are required"},
#                 status=400
#             )

#         # 🔎 Resolve demo bot
#         bot = VoiceAgent.objects.filter(
#             industry_id=industry_id,
#             role_template_id=role_id,
#             is_demo=True,
#             is_active=True
#         ).first()

#         if not bot:
#             return Response(
#                 {"error": "No demo bot found for selected role"},
#                 status=404
#             )

#         # ==================================================
#         # 🟢 START CONVERSATION (BOT GREETS FIRST)
#         # ==================================================
#         if not session_id:
#             # 🔑 IMPORTANT: NEVER SEND None
#             start_message = "start conversation"

#             reply, session_id = process_message(
#                 agent=bot,
#                 message=start_message,
#                 session_id=None
#             )

#         # ==================================================
#         # 🔵 CONTINUE CONVERSATION
#         # ==================================================
#         else:
#             if not message:
#                 return Response(
#                     {"error": "message is required"},
#                     status=400
#                 )

#             reply, session_id = process_message(
#                 agent=bot,
#                 message=message,
#                 session_id=session_id
#             )

#         # ==================================================
#         # 🔊 AZURE TTS
#         # ==================================================
#         voice_name = (
#             bot.role_template.default_voice
#             if bot.role_template and bot.role_template.default_voice
#             else "en-IN-NeerjaNeural"
#         )

#         audio = synthesize_to_base64(reply)

#         return Response({
#             "reply": reply,
#             "audio": audio,
#             "voice": voice_name,
#             "session_id": session_id
#         })




# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import tempfile
from rest_framework.decorators import api_view
from agents.models import VoiceAgent
from conversations.services.core.dialogue_engine import process_message


import re

def clean_for_tts(text: str) -> str:
    if not text:
        return ""

    # Remove emojis
    text = re.sub(r"[\U00010000-\U0010ffff]", "", text)

    # Remove markdown **bold**
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)

    # Remove remaining markdown symbols
    text = re.sub(r"[*_`~>#]", "", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


class DemoChatAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        industry_id = request.data.get("industry_id")
        role_id = request.data.get("role_id")
        session_id = request.data.get("session_id")

        if not industry_id or not role_id:
            return Response({"error": "industry_id and role_id required"}, status=400)

        bot = VoiceAgent.objects.filter(
            industry_id=industry_id,
            role_template_id=role_id,
            is_demo=True,
            is_active=True
        ).first()

        if not bot:
            return Response({"error": "No demo bot found"}, status=404)

        audio_file = request.FILES.get("audio")
        message = request.data.get("message")

        # 🎧 AUDIO → STT
        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)
                audio_path = f.name

            message = speech_to_text(audio_path)

            if not message:
                fallback = "Sorry, I could not hear you clearly. Please try again."
                return Response({
                    "reply": fallback,
                    "audio": synthesize_to_base64(fallback),
                    "session_id": session_id
                })

        # 🟢 GREETING
        if not session_id and not message:
            message = "start conversation"

        if not message:
            return Response({"error": "message or audio required"}, status=400)

        reply, session_id = process_message(
            agent=bot,
            message=message,
            session_id=session_id
        )

        clean_reply = clean_for_tts(reply)

        return Response({
            "user_text": message,
            "reply": reply,
            "audio": synthesize_to_base64(clean_reply),
            "session_id": session_id
        })
    

# ✅ 1. Get all conversations (for dashboard)
@api_view(["GET"])
def get_conversations(request):
    conversations = Conversation.objects.all().order_by("-started_at")
    serializer = ConversationSerializer(conversations, many=True)
    return Response({
        "count": conversations.count(),   # ✅ NEW FIELD
        "data": serializer.data           # ✅ existing data
    })


# ✅ 2. Get full conversation (messages)
@api_view(["GET"])
def get_conversation_messages(request, session_id):
    try:
        conversation = Conversation.objects.get(session_id=session_id)
    except Conversation.DoesNotExist:
        return Response({"error": "Conversation not found"}, status=404)

    messages = Message.objects.filter(conversation=conversation).order_by("created_at")
    serializer = MessageSerializer(messages, many=True)

    return Response({
        "session_id": conversation.session_id,
        "user_number": conversation.user_number,
        "messages": serializer.data
    })