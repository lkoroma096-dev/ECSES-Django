

from django.urls import path
from . import views

app_name = 'connecthub'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('inbox/', views.inbox, name='inbox'),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notification/<int:notification_id>/edit/', views.edit_notification, name='edit_notification'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path('parent-view-children/', views.parent_view_children, name='parent_view_children'),
    path('child-dashboard/', views.child_dashboard, name='child_dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('create-user/', views.create_user, name='create_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('compose-message/', views.compose_message, name='compose_message'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('reply-message/<int:message_id>/', views.reply_message, name='reply_message'),
    path('edit-message/<int:message_id>/', views.edit_message, name='edit_message'),
    path('send-notification/', views.send_notification, name='send_notification'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
]
