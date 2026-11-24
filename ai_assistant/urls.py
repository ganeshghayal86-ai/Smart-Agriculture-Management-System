
from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbot, name='chatbot'),
    path('clear-chat/', views.clear_chat, name='clear_chat'),
]
