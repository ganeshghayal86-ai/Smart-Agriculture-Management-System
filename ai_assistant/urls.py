from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbot, name='chatbot'),
    path('clear-chat/', views.clear_chat, name='clear_chat'),
    path('voice-transcribe/', views.voice_transcribe, name='voice_transcribe'),
]