from django.urls import path
from .views import ShowAllPost

from post_app.views import PostCreateView

urlpatterns = [
    path(route= '', view= ShowAllPost.as_view(), name= 'home'),
    path(route= 'create/', view= PostCreateView.as_view(), name= 'post_create'),
]