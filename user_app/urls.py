
from django.urls import path
from .views import (
    AuthTemplateView, 
    RegisterView, 
    LoginView, 
    FriendsView, 
    FriendActionView, 
    FriendsSectionView
)

urlpatterns = [
    path(route= '', view= AuthTemplateView.as_view(), name= 'auth'),
    path(route= 'register/', view= RegisterView.as_view(), name= 'register'),
    path(route= 'login/', view= LoginView.as_view(), name= 'login'),
    path(route= 'friends/', view= FriendsView.as_view(), name= 'friends'),
    path("friends/<str:section>/", FriendsSectionView.as_view(), name="friends_section"),  # Віддаємо вкладку друзів через fetch.
    path("friends/action/<int:user_id>/<str:action>/", FriendActionView.as_view(), name="friend_action"),  # Обробляємо дії з картками друзів.
]

