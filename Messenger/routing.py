from django.urls import path
from .consumers import StatusConsumer

websocket_urlpatterns = [
    path('status/', StatusConsumer.as_asgi())
]