from django.urls import path
from .views import ChatAPIView, BotListAPIView, DemoChatAPIView, demo_page

urlpatterns = [
    path("agents/<uuid:agent_id>/chat/", ChatAPIView.as_view()),
    path("v1/bots/", BotListAPIView.as_view()),
    path("v1/bots/<uuid:agent_id>/chat/", ChatAPIView.as_view()),
    path("demo/chat/", DemoChatAPIView.as_view()),
    path("", demo_page, name="demo-page")
]