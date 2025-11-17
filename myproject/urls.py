"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

import Friendslist
from landingpage.views import home
from profiles.views import select_role, my_profile, post_login_redirect, profile_redirect, profile_edit, welcome_screen

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/login/", RedirectView.as_view(url="/accounts/google/login/", permanent=False)),
    path('login/', include('loginpage.urls')),
    path('accounts/', include('allauth.urls')),
    path("", include("userprivileges.urls")),
    path("", home, name="landingpage"),
    path("profile/", my_profile, name="my_profile"),
    path("select-role/", select_role, name="select_role"),
    path("welcome/", welcome_screen, name="welcome_screen"),
    path("post-login/", post_login_redirect, name="post_login_redirect"),
    path("profile-page/" , profile_redirect, name="profile_redirect"),
    path('chat/', include("chat.urls")),
    path("friends/", include(("Friendslist.urls", "friends"), namespace="friends")),
    path("edit_profile/", profile_edit, name="profile_edit"),
    path("", include(("posting.urls", "posting"), namespace="posting")),
    path("moderation/", include(("moderation.urls", "moderation"), namespace="moderation")),

    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)