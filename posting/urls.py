from django.urls import path
from . import views

app_name = 'posting'
urlpatterns = [
    path("", views.index, name="post_list"),
    path("posts/<int:post_id>", views.post_detail, name="post_detail"),
    path("posts/", views.index, name="post_list"),
    path("posts/<int:post_id>/edit", views.edit_post, name="edit_post"),
    path("posts/<int:post_id>/delete", views.delete_post, name="delete_post"),
    path("posts/create", views.create_post, name="create_post"),
    path("map/", views.post_map, name="post_map"),
    path('thank-organizer/', views.thank_organizer, name='thank_organizer'),
    path("posts/history/", views.event_history, name="event_history"),
    path("posts/export-data", views.export_data, name="export_data"),
    path("posts/<int:post_id>/rsvp/", views.create_rsvp, name="create_rsvp"),
    path("posts/<int:post_id>/rsvps/", views.view_post_rsvps, name="view_post_rsvps"),
    path("rsvp/<int:rsvp_id>/cancel/", views.cancel_rsvp, name="cancel_rsvp"),

]