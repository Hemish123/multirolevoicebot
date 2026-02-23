from django.contrib import admin
from .models import ConversationLog, ConversationSession


@admin.register(ConversationLog)
class ConversationLogAdmin(admin.ModelAdmin):
    list_display = ("agent", "user_message", "created_at")
    search_fields = ("agent__name", "user_message")


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    list_display = (
        "agent",
        "session_id",
        "current_intent",
        "stage",
        "created_at",
        "updated_at",
    )
    search_fields = ("session_id", "agent__name")
    list_filter = ("agent", "current_intent", "stage")
    readonly_fields = ("created_at", "updated_at")