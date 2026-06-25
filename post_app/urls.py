from django.urls import path
from .views import PostListView, PostCreateView

urlpatterns = [
    path(route= '', view= PostListView.as_view(), name= 'post'),
    path(route= 'create/', view= PostCreateView.as_view(), name= 'post_create'),
]