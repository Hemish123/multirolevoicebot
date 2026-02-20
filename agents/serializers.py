from rest_framework import serializers
from .models import Industry, AgentRoleTemplate, VoiceAgent


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRoleTemplate
        fields = ["id", "role_name", "description"]


class IndustrySerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True)

    class Meta:
        model = Industry
        fields = ["id", "name", "slug", "roles"]


class CreateAgentSerializer(serializers.Serializer):
    template_id = serializers.IntegerField()
    agent_name = serializers.CharField()
    company_name = serializers.CharField(required=False)