from django.urls import path
from . import views

app_name = 'posting'
urlpatterns = [
    path("posts/<int:post_id>", views.post_detail, name="post_detail"),
    path("posts/", views.index, name="post_list"),
    path("posts/<int:post_id>/edit", views.edit_post, name="edit_post"),
    path("posts/<int:post_id>/delete", views.delete_post, name="delete_post"),
    path("posts/create", views.create_post, name="create_post"),
    path("post/<int:post_id>/report/", views.report_post, name="report_post"),
    path("posts/history/", views.event_history, name="event_history"),
    path("posts/export-data", views.export_data, name="export_data"),

]