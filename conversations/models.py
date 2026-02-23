from django.db import models

# Create your models here.
from django.db import models
from agents.models import VoiceAgent


class ConversationLog(models.Model):
    agent = models.ForeignKey(VoiceAgent, on_delete=models.CASCADE)
    user_message = models.TextField()
    agent_reply = models.TextField()
    source = models.CharField(max_length=20, default="api")
    created_at = models.DateTimeField(auto_now_add=True)

class ConversationSession(models.Model):
    agent = models.ForeignKey(VoiceAgent, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255)
    current_intent = models.CharField(max_length=100, blank=True, null=True)
    stage = models.CharField(max_length=100, blank=True, null=True)
    state = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent.name} - {self.session_id}"