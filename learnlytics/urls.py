from django.urls import path
from . import views

app_name = 'learnlytics'

urlpatterns = [
    path('', views.activity_list, name='activity_list'),
    path('activities/', views.activity_list, name='activities'),
    path('activity/<int:activity_id>/', views.activity_detail, name='activity_detail'),
    path('activity/new/', views.activity_new, name='activity_new'),
    path('assign/', views.assign_activity, name='assign_activity'),
    path('assign/<int:activity_id>/', views.assign_activity, name='assign_activity'),
    path('start-activity/<int:assignment_id>/', views.start_activity, name='start_activity'),
    path('continue-activity/<int:assignment_id>/', views.continue_activity, name='continue_activity'),
    path('badges/', views.badges, name='badges'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
]

