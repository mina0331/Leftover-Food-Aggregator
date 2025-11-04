# userprivileges/urls.py
from django.urls import path
from . import views
from posting import views as posting_views

app_name = "userprivileges"

urlpatterns = [
    path("after-login/", views.post_login_router, name="post_login_router"),
    path("student/", posting_views.index, name="student_home"),
    path("provider/", posting_views.index, name="provider_home"),
    path("moderator/", views.moderator_home, name="moderator_home"),
]