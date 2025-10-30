from django.urls import path
from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.messages_index, name="index"),
    path('conversations/<int:user_id>/', views.conversation_detail, name="conversation"),
    path('start/', views.start_conversation, name="start_conversation"),
    path("find-friends/", views.find_friends, name="find_friends"),
    path("send-friend-request/<int:user_id>/", views.send_friend_request, name="send_friend_request"),


]
