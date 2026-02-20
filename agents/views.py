from django.shortcuts import render

# Create your views here.
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Industry, AgentRoleTemplate, VoiceAgent
from .serializers import IndustrySerializer, CreateAgentSerializer
from .services.template_resolver import resolve_prompt


class ListIndustriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        industries = Industry.objects.prefetch_related("roles").all()
        return Response(IndustrySerializer(industries, many=True).data)


class CreateAgentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateAgentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template = AgentRoleTemplate.objects.filter(
            id=serializer.validated_data["template_id"]
        ).first()

        if not template:
            return Response({"error": "Template not found"}, status=404)

        resolved = resolve_prompt(
            template,
            serializer.validated_data["agent_name"],
            serializer.validated_data.get("company_name", "")
        )

        agent = VoiceAgent.objects.create(
            owner=request.user,
            template=template,
            name=serializer.validated_data["agent_name"],
            company_name=serializer.validated_data.get("company_name", ""),
            resolved_prompt=resolved
        )

        return Response({
            "agent_id": str(agent.id),
            "api_key": str(agent.api_key)
        })


class ListUserAgentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        agents = VoiceAgent.objects.filter(owner=request.user)
        return Response([
            {
                "id": str(a.id),
                "name": a.name,
                "is_active": a.is_active,
                "api_key": str(a.api_key)
            }
            for a in agents
        ])


class ToggleAgentView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, agent_id):
        agent = VoiceAgent.objects.filter(id=agent_id, owner=request.user).first()
        if not agent:
            return Response({"error": "Not found"}, status=404)

        agent.is_active = not agent.is_active
        agent.save()
        return Response({"is_active": agent.is_active})


class RegenerateAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, agent_id):
        agent = VoiceAgent.objects.filter(id=agent_id, owner=request.user).first()
        if not agent:
            return Response({"error": "Not found"}, status=404)

        agent.api_key = uuid.uuid4()
        agent.save()
        return Response({"api_key": str(agent.api_key)})