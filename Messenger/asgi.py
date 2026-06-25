"""
ASGI config for Messenger project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from chat_app.routing import websocket_urlpatterns
from .routing import websocket_urlpatterns as messenger_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Messenger.settings')

# application = get_asgi_application()
application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns + messenger_urlpatterns))
})

# uvicorn та gunicorn