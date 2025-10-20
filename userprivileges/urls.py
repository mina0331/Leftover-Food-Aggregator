# userprivileges/urls.py
from django.urls import path
from . import views

app_name = "userprivileges"

urlpatterns = [
    path("after-login/", views.post_login_router, name="post_login_router"),
    path("student/", views.student_home, name="student_home"),
    path("provider/", views.provider_home, name="provider_home"),
    
]