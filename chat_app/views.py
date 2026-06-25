# Імпортуємо міксин, який пускає на сторінку тільки авторизованих користувачів.
from django.contrib.auth.mixins import LoginRequiredMixin

# Імпортуємо Paginator для порційного завантаження історії.
from django.core.paginator import Paginator

# Імпортуємо JSON-відповідь для POST-запиту створення чату.
from django.http import JsonResponse

# Імпортуємо базовий клас простого view.
from django.views import View

# Імпортуємо базовий клас сторінки з HTML-шаблоном.
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpRequest
# Імпортуємо модель користувача.
from user_app.models import User

# Імпортуємо функцію отримання друзів.
from user_app.utils.friend_queries import get_users_by_section

# Імпортуємо моделі чату та повідомлення.
from .models import Chat, Message, MessageImage

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

# Показуємо сторінку чатів.
class ChatView(LoginRequiredMixin, TemplateView):
    # Вказуємо URL входу для неавторизованих користувачів.
    login_url = "auth"
    # Вказуємо HTML-шаблон сторінки.
    template_name = "chat_app/chat.html"

    # Готуємо дані для шаблону.
    def get_context_data(self, **kwargs):
        # Беремо стандартний context від TemplateView.
        context = super().get_context_data(**kwargs)
        # Передаємо у шаблон друзів поточного користувача.
        context["friends"] = get_users_by_section(self.request.user, "friends")
        # Передаємо у шаблон вже створені особисті чати для правого блоку.
        context["personal_chats"] = Chat.objects.filter(users=self.request.user, is_group=False).order_by("id")
        # Передаємо у шаблон групові чати, де поточний користувач є учасником.
        context["group_chats"] = Chat.objects.filter(users=self.request.user, is_group=True).order_by("id")
        # Повертаємо context у шаблон.
        return context


# Створюємо або знаходимо чат із конкретним користувачем.
class ChatWithView(LoginRequiredMixin, View):
    # Вказуємо URL входу для неавторизованих користувачів.
    login_url = "auth"

    # Обробляємо POST-запит із браузера.
    def post(self, request, user_id):
        # Знаходимо користувача, з яким відкривають чат.
        other_user = User.objects.get(id=user_id)
        # Беремо друзів поточного користувача.
        friends = get_users_by_section(request.user, "friends")
        # Забороняємо чат, якщо користувач не є другом.
        if other_user not in friends:
            # Повертаємо помилку доступу.
            return JsonResponse({"success": False}, status=403)
        # Беремо id особистих чатів поточного користувача.
        chat_ids = Chat.objects.filter(users=request.user, is_group=False).values_list("id", flat=True)
        # Шукаємо вже існуючий чат між цими двома користувачами.
        chat = Chat.objects.filter(id__in=chat_ids, users=other_user, is_group=False).first()
        # Створюємо новий чат, якщо його ще немає.
        if chat is None:
            # Створюємо порожній особистий чат.
            chat = Chat.objects.create(is_group=False)
            # Додаємо до чату обох користувачів.
            chat.users.add(request.user, other_user)
        # Повертаємо id чату для WebSocket.
        return JsonResponse({"success": True, "chat_id": chat.id, "username": other_user.email})


# Віддаємо історію чату сторінками по 10 повідомлень.
class MessageHistoryView(LoginRequiredMixin, View):
    # Вказуємо URL входу для неавторизованих користувачів.
    login_url = "auth"

    # Обробляємо GET-запит на чергову сторінку історії.
    def get(self, request, chat_id):
        # Перевіряємо, що користувач є учасником цього чату.
        if not Chat.objects.filter(id=chat_id, users=request.user).exists():
            # Забороняємо читати чужі повідомлення.
            return JsonResponse({"success": False}, status=403)

        # Новіші повідомлення йдуть першими, щоб page=1 була останньою історією.
        query = Message.objects.filter(chat_id=chat_id).select_related("sender").order_by("-created_at", "-id")
        page_obj = Paginator(query, 10).get_page(request.GET.get("page", 1))
        # Розвертаємо сторінку назад, щоб у чаті повідомлення йшли зверху вниз за часом.
        messages = list(page_obj.object_list)[::-1]

        return JsonResponse(
            {
                "messages": [
                    {
                        "id": message.id, 
                        "text": message.text, 
                        "sender": message.sender.username,
                        "images": [image.image.url for image in message.images.all()]
                    } for message in messages],
                "has_next": page_obj.has_next(),
            }
        )


# Створюємо груповий чат із друзями, яких користувач вибрав у модальному вікні.
class CreateGroupView(LoginRequiredMixin, View):
    # Пускаємо до створення групи тільки авторизованих користувачів.
    login_url = "auth"

    # Обробляємо POST-запит із назвою групи та списком вибраних учасників.
    def post(self, request):
        # Беремо назву групи з форми й прибираємо зайві пробіли.
        name = request.POST.get("name", "").strip()
        # Беремо id друзів, яких користувач відмітив у модальному вікні.
        user_ids = request.POST.getlist("users")

        # Не створюємо групу без назви, щоб у правому блоці не з'являвся порожній чат.
        if not name:
            return JsonResponse({"success": False, "error": "name_required"}, status=400)

        # Дозволяємо додавати в групу тільки друзів поточного користувача.
        friend_ids = get_users_by_section(request.user, "friends").filter(id__in=user_ids).values_list("id", flat=True)
        # Створюємо сам груповий чат і призначаємо автора адміністратором.
        chat = Chat.objects.create(name= name, is_group= True, admin= request.user)
        # Додаємо автора групи до учасників, щоб він одразу бачив чат у списку.
        chat.users.add(request.user)
        # Додаємо вибраних друзів до учасників групового чату.
        chat.users.add(*User.objects.filter(id__in= friend_ids))

        # Повертаємо дані нової групи, щоб frontend одразу додав її в правий блок.
        return JsonResponse({"success": True, "chat_id": chat.id, "name": chat.name})
    
class MessageUploadView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, chat_id: int, *args, **kwargs):

        if not Chat.objects.filter(id = chat_id, users = request.user).exists():
            return JsonResponse({'success': False}, status= 403)
        
        text = request.POST.get("text", "").strip()
        images = request.FILES.getlist("images")
        
        if not images and not text:
            return JsonResponse({'success': False, "error": "required message"}, status= 400)
        
        message = Message.objects.create(chat_id= chat_id, sender= request.user, text= text)
        
        for image in images:
            MessageImage.objects.create(message= message, image= image)
        
        image_urls= [image.image.url for image in message.images.all()] 
        
        channel_layer= get_channel_layer()

        
        async_to_sync(channel_layer.group_send)(
            f"chat_{chat_id}",
            {
                "type": "chat_message",
                "id": message.id,
                "text": message.text,
                "sender": message.sender.username,
                "created_at": timezone.localtime(message.created_at).isoformat(),
                "images": image_urls
            }
        )
        return JsonResponse({"success": True })