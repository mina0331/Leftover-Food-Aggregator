from django.urls import path
from . import views

app_name = "profiles"   # <-- REQUIRED for namespaces

urlpatterns = [
    path("profile/<int:user_id>/", views.view_profile, name="view_profile"),
    path("account/<int:user_id>/delete/", views.delete_account, name="delete_account")

]