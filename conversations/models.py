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