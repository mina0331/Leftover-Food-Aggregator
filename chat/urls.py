from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.messages_index, name="index"),
    path('conversations/<int:user_id>/', views.conversation_detail, name="conversations"),
    path('start/', views.start_conversation, name="start_conversation"),
]
