from django.urls import path
from . import views

urlpatterns = [
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/", views.index, name="post_list"),
    path("posts/<int: post_id>", views.edit_post, name="edit_post"),

]