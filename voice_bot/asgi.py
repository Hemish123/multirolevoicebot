"""
ASGI config for voice_bot project.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voice_bot.settings")

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

django_asgi_app = get_asgi_application()

import conversations.routing  # import AFTER Django setup

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": AuthMiddlewareStack(
        URLRouter(
            conversations.routing.websocket_urlpatterns
        )
    ),
})