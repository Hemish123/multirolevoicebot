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
    


class Conversation(models.Model):
    agent = models.ForeignKey(VoiceAgent, on_delete=models.CASCADE)

    session_id = models.CharField(max_length=100, unique=True)
    user_number = models.CharField(max_length=20)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_number} - {self.session_id}"


class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("bot", "Bot"),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)