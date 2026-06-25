# Імпортуємо JSON для обміну даними з браузером.
import json

# Імпортуємо обгортку для роботи з БД в async-коді.
from channels.db import database_sync_to_async

# Імпортуємо базовий WebSocket-consumer.
from channels.generic.websocket import AsyncWebsocketConsumer

# Імпортуємо моделі чату та повідомлення.
from .models import Chat, Message


# Створюємо consumer для одного чату.
class ChatConsumer(AsyncWebsocketConsumer):
    # Обробляємо підключення до WebSocket.
    async def connect(self):
        # Беремо id чату з URL.
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        # Створюємо назву групи для цього чату.
        self.room_group_name = f"chat_{self.chat_id}"
        # Додаємо користувача до групи чату.
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        # Приймаємо WebSocket-з'єднання.
        await self.accept()

    # Обробляємо відключення від WebSocket.
    async def disconnect(self, close_code):
        # Видаляємо користувача з групи чату.
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Обробляємо повідомлення з браузера.
    async def receive(self, text_data):
        # Перетворюємо JSON у словник.
        data = json.loads(text_data)
        # Дістаємо текст повідомлення.
        text = data.get("text", "").strip()
        # Нічого не робимо без тексту.
        if not text:
            # Завершуємо обробку.
            return
        # Зберігаємо повідомлення в БД.
        message = await self.save_message(text)
        # Відправляємо повідомлення всім у цьому чаті.
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message", 
                "id": message["id"], 
                "text": message["text"], 
                "sender": message["sender"],
                # 
                "images": message["images"]
            },
        )

    # Відправляємо повідомлення з групи в браузер.
    async def chat_message(self, event):
        # Надсилаємо JSON з автором і текстом.
        await self.send(text_data=json.dumps(
            {
                "id": event["id"], 
                "text": event["text"], 
                "sender": event["sender"],
                # 
                "images": event.get("images", [])
            }
        ))


    # Дозволяємо async-коду створити повідомлення в БД.
    @database_sync_to_async
    # Зберігаємо нове повідомлення.
    def save_message(self, text):
        # Беремо поточного користувача.
        user = self.scope["user"]
        # Створюємо повідомлення.
        message = Message.objects.create(chat_id=self.chat_id, sender=user, text=text)
        # Повертаємо дані для браузера.
        return {
            "id": message.id, 
            "text": message.text, 
            "sender": user.username,
            "images": []
        }
