from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('flag/', views.flag_content, name='flag_content'),
    path('review/', views.review_flagged_content, name='review_flagged'),
    path('edit/<int:flag_id>/', views.edit_flagged_content, name='edit_flagged'),
    path('approve/<int:flag_id>/', views.approve_flag, name='approve_flag'),
    path('dismiss/<int:flag_id>/', views.dismiss_flag, name='dismiss_flag'),
    path('delete/<int:flag_id>/', views.delete_flagged_content, name='delete_flagged'),
    path('suspend/<int:user_id>/', views.suspend_user, name='suspend_user'),
    path('reinstate/<int:suspension_id>/', views.reinstate_user, name='reinstate_user'),
    path('suspensions/', views.manage_suspensions, name='manage_suspensions'),
    path('user/<int:user_id>/suspensions/', views.user_suspension_history, name='user_suspension_history'),
    path('suspension-notice/<int:suspension_id>/', views.suspension_notice, name='suspension_notice'),
]


