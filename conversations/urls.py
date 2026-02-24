from django.urls import path
from .views import ChatAPIView, BotListAPIView

urlpatterns = [
    path("agents/<uuid:agent_id>/chat/", ChatAPIView.as_view()),
    path("v1/bots/", BotListAPIView.as_view()),
    path("v1/bots/<uuid:agent_id>/chat/", ChatAPIView.as_view()),
]