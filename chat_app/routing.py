"""
    Файл для налаштування маршрутизації WebSocket-з`єднань.
    Цей файл є аналогом urls.py і працює в асинхронному режимі. 
    В цьому файлі ми створюємо url-адреси для WebSocket-з`єднань.
"""
from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    # path(route='chat/', view= ChatConsumer.as_asgi()),
    path(route= "chat/<int:chat_id>/", view= ChatConsumer.as_asgi())
]