from django.shortcuts import render

# Create your knowledge views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import KnowledgeFile
from .serializers import KnowledgeUploadSerializer
from .services.text_extractor import extract_text
from agents.models import VoiceAgent
from .services.chunker import chunk_text
from .models import KnowledgeChunk


class KnowledgeUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, agent_id):
        agent = VoiceAgent.objects.filter(
            id=agent_id,
            owner=request.user
        ).first()

        if not agent:
            return Response({"error": "Agent not found"}, status=404)

        serializer = KnowledgeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        knowledge = serializer.save(agent=agent)

        # Extract text
        extracted = extract_text(knowledge.file.path)
        knowledge.extracted_text = extracted
        knowledge.save()



        chunks = chunk_text(extracted)

        for chunk in chunks:
            KnowledgeChunk.objects.create(
                knowledge_file=knowledge,
                content=chunk
            )

        return Response({
            "message": "File uploaded successfully",
            "text_length": len(extracted)
        })