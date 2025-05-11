from django.urls import path
from . import views

urlpatterns = [
    path('booky-chat/', views.booky_chat, name='booky_chat'),
] 