from django.urls import path
from .views import ChatAPIView

urlpatterns = [
    path("agents/<uuid:agent_id>/chat/", ChatAPIView.as_view()),
]