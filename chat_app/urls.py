# Імпортуємо path для опису маршрутів.
from django.urls import path

# Імпортуємо клас сторінки чатів.
from .views import ChatView

# Імпортуємо класи створення або пошуку чату, історії повідомлень і створення групи.
from .views import ChatWithView, CreateGroupView, MessageHistoryView,MessageUploadView


# Описуємо HTTP-маршрути chat_app.
urlpatterns = [
    # Відкриваємо сторінку чатів через клас-відображення.
    path("", ChatView.as_view(), name="chat"),
    # Створюємо або знаходимо чат із користувачем через клас-відображення.
    path("chat_with/<int:user_id>/", ChatWithView.as_view(), name="chat_with"),
    # Завантажуємо історію повідомлень чату сторінками.
    path("<int:chat_id>/messages/", MessageHistoryView.as_view(), name="message_history"),
    # Створюємо новий груповий чат із даних модального вікна.
    path("create_group/", CreateGroupView.as_view(), name="create_group"),
    path("<int:chat_id>/messages/upload/", MessageUploadView.as_view(), name= "message_upload"),
]
