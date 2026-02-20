from django.core.management.base import BaseCommand
from agents.models import Industry, AgentRoleTemplate

TEMPLATES = [
    {
        "industry": {"name": "Healthcare", "slug": "healthcare"},
        "roles": [
            {
                "role_name": "Patient Support Agent",
                "description": "Handles patient queries and appointments",
                "system_prompt_template": "You are {agent_name} working for {company_name}. Assist patients politely.",
                "default_tone": "empathetic",
                "default_voice": "en-US-JennyNeural",
            }
        ]
    }
]


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for block in TEMPLATES:
            industry, _ = Industry.objects.get_or_create(**block["industry"])
            for role in block["roles"]:
                AgentRoleTemplate.objects.get_or_create(
                    industry=industry,
                    role_name=role["role_name"],
                    defaults=role
                )
        self.stdout.write("Roles seeded successfully")