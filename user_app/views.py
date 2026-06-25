from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views.generic.base import TemplateView
from django.views import View
from django.http import JsonResponse, HttpRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.template.loader import render_to_string

from .models import User
from .forms import EmailUserCreationForm, EmailAuthenticatedForm
from .utils.friend_queries import get_users_by_section
from .utils.friend_actions import accept_friend_request, add_friend_request, delete_friendship, dismiss_recommendation

# Create your views here.
class AuthTemplateView(TemplateView):
    template_name = 'user_app/auth.html'
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["form_register"] = EmailUserCreationForm()
        context['form_login'] = EmailAuthenticatedForm()
        context['form_confirm_email'] = ''
        return context
    
    
class RegisterView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Користувача успішно зареєстровано'
            })
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data()
        }, status= 400)
        
class LoginView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        form = EmailAuthenticatedForm(request= request, data= request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request= request, user= user)
            return redirect('home')
        # 
        return JsonResponse({
            "success": True,
            'errors': form.errors.get_json_data()
        })
        
class FriendsView(LoginRequiredMixin, TemplateView):
    template_name = 'user_app/friends.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = {
            'requests': {'title': 'Запити', 'users': get_users_by_section(user = self.request.user, section= 'requests')[:3]},
            'recommendations': {'title': 'Рекомендації', 'users': get_users_by_section(user = self.request.user, section= 'recommendations')[:6]},
            'friends': {'title': 'Всі друзі', 'users': get_users_by_section(user = self.request.user, section= 'friends')[:6]},
        }
        return context    

# 
class FriendsSectionView(FriendsView):
    def get(self, request, section, *args, **kwargs):
        # Отримуємо потрібний список за назвою вкладки.
        users = get_users_by_section(request.user, section)
        # Розбиваємо людей на порції по 6 карток.
        page_obj = Paginator(users, 6).get_page(request.GET.get("page", 1))
        # Рендеримо тільки поточну порцію карток вибраної вкладки.
        html = render_to_string("user_app/particles/friends/friend_cards.html", 
                                {"users": page_obj.object_list, "section": section}, 
                                request=request
                                )
        # Повертаємо HTML поточної порції і ознаку наступної сторінки.
        return JsonResponse({"html": html, "has_next": page_obj.has_next()})
#  
class FriendActionView(LoginRequiredMixin, View):
    login_url = reverse_lazy('auth')
    
    def post(self, request, user_id, action, *args, **kwargs):
        other_user = User.objects.get(id= user_id)
        
        if action == 'add':
            return JsonResponse(add_friend_request(request.user, other_user))
        if action == 'dismiss':
            return JsonResponse(dismiss_recommendation(request.user, other_user))
        if action == 'accept':
            action_result = accept_friend_request(request.user, other_user)
            action_result['friend_html'] = render_to_string(
                'user_app/particles/friends/friend_cards.html',
                {'users': [action_result['friend']], 'section': 'friends'},
                request= request
            )
            del action_result['friend']
            
            return JsonResponse(action_result)
        # 
        return JsonResponse(delete_friendship(request.user, other_user))