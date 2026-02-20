from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from agents.models import VoiceAgent
from .models import ConversationLog
from knowledge.services.retriever import retrieve_relevant_chunks
from .services.azure_openai_service import generate_response

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
        
        # 🔎 Retrieve knowledge
        context = retrieve_relevant_chunks(agent, message)
        print("MESSAGE:", message)
        print("RETRIEVED CONTEXT:", context)
        enhanced_prompt = f"""
{agent.resolved_prompt}

Use the following knowledge context to answer the user's question.
If the answer is not in the context, say you don't have that information.

Knowledge Context:
{context}
"""

        # 🤖 Call Azure OpenAI
        reply = generate_response(enhanced_prompt, message)

        ConversationLog.objects.create(
            agent=agent,
            user_message=message,
            agent_reply=reply
        )

        return Response({
            "agent": agent.name,
            "reply": reply
        })