from django.urls import path

from .views import ChatAPIView, BotListAPIView, DemoChatAPIView, demo_page, get_conversations, get_conversation_messages 

urlpatterns = [
    path("agents/<uuid:agent_id>/chat/", ChatAPIView.as_view()),
    path("v1/bots/", BotListAPIView.as_view()),
    path("v1/bots/<uuid:agent_id>/chat/", ChatAPIView.as_view()),
    path("demo/chat/", DemoChatAPIView.as_view()),
    path("", demo_page, name="demo-page"),
    path("conversations/", get_conversations),
    path("conversations/<str:session_id>/", get_conversation_messages),

]