from django.urls import path
from . import views

urlpatterns = [
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("posts/", views.index, name="post_list"),
    path("posts/<int: post_id>/edit", views.edit_post, name="edit_post"),
    path("posts/<int: post_id>/delete", views.delete_post, name="delete_post"),

]