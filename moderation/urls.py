from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('flag/', views.flag_content, name='flag_content'),
    path('review/', views.review_flagged_content, name='review_flagged'),
    path('approve/<int:flag_id>/', views.approve_flag, name='approve_flag'),
    path('dismiss/<int:flag_id>/', views.dismiss_flag, name='dismiss_flag'),
    path('delete/<int:flag_id>/', views.delete_flagged_content, name='delete_flagged'),
]


