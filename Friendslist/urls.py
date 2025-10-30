from django.urls import path
from . import views

app_name = "friends"

urlpatterns = [
    path("", views.FriendsList_index, name="friends_list"),
    path("send/<int:user_id>/", views.send_friend_request, name="send_friend_request"),
    path("accept/<int:req_id>/", views.accept_friend_request, name="accept_friend_request"),
    path("reject/<int:req_id>/", views.reject_friend_request, name="reject_friend_request"),
    path("cancel/<int:req_id>/", views.cancel_friend_request, name="cancel_friend_request"),  # ✅ must exist
    path("remove/<int:user_id>/", views.remove_friend, name="remove_friend"),
]