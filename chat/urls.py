from django.urls import path
from . import views
from Friendslist import views as viewsFriends

app_name = 'chat'
urlpatterns = [
    path('', views.messages_index, name="index"),
    path("conversation/<int:convo_id>/", views.conversation_detail, name="conversation"),
    path("start-converstaion/", views.start_conversation, name="start_conversation"),
    path("dm/<int:user_id>/", views.dm_with_user, name="dm_with_user"),
    path("find-friends/", views.find_friends, name="find_friends"),
    path("send-friend-request/<int:user_id>/", viewsFriends.send_friend_request, name="send_friend_request"),
    path("chat/dm/<int:user_id>/", views.dm_with_user, name="dm_with_user"),


]
