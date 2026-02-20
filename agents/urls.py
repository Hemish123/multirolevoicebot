from django.urls import path
from .views import (
    ListIndustriesView,
    CreateAgentView,
    ListUserAgentsView,
    ToggleAgentView,
    RegenerateAPIKeyView,
)

urlpatterns = [
    path("industries/", ListIndustriesView.as_view()),
    path("create/", CreateAgentView.as_view()),
    path("my/", ListUserAgentsView.as_view()),
    path("<uuid:agent_id>/toggle/", ToggleAgentView.as_view()),
    path("<uuid:agent_id>/regenerate-key/", RegenerateAPIKeyView.as_view()),
]