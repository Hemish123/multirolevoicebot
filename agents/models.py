
# Create your models here.
import uuid
from django.db import models
from django.contrib.auth.models import User


class Industry(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class AgentRoleTemplate(models.Model):
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name="roles")
    role_name = models.CharField(max_length=100)
    description = models.TextField()
    system_prompt_template = models.TextField()
    default_tone = models.CharField(max_length=50)
    default_voice = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.industry.name} - {self.role_name}"


class VoiceAgent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agents")
    template = models.ForeignKey(AgentRoleTemplate, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100, blank=True)
    resolved_prompt = models.TextField()
    api_key = models.UUIDField(default=uuid.uuid4, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name