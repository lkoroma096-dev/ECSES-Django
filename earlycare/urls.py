from django.urls import path
from . import views

app_name = 'earlycare'

urlpatterns = [
    # Children CRUD
    path('', views.child_list, name='child_list'),
    path('children/', views.child_list, name='child_list'),
    path('child/<int:child_id>/', views.child_detail, name='child_detail'),
    path('child/new/', views.child_new, name='child_new'),
    path('child/<int:child_id>/edit/', views.child_edit, name='child_edit'),
    path('child/<int:child_id>/delete/', views.child_delete, name='child_delete'),
    # Admin assignment tools
    path('assignments/children/', views.child_assignments, name='child_assignments'),
    path('child/<int:child_id>/assign-teacher/', views.assign_teacher, name='assign_teacher'),
    path('child/<int:child_id>/assign-parent/', views.assign_parent, name='assign_parent'),
    
    # Assessments CRUD
    path('assessment/new/', views.assessment_new, name='assessment_new'),
    path('assessments/', views.assessments, name='assessments'),
    path('assessment/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    path('assessment/<int:assessment_id>/edit/', views.assessment_edit, name='assessment_edit'),
    path('assessment/<int:assessment_id>/delete/', views.assessment_delete, name='assessment_delete'),
    
    # Support Plans CRUD
    path('support-plan/<int:child_id>/', views.support_plan, name='support_plan'),
    path('support-plans/', views.support_plans, name='support_plans'),
    path('support-plan/<int:support_plan_id>/detail/', views.support_plan_detail, name='support_plan_detail'),
    path('support-plan/<int:support_plan_id>/edit/', views.support_plan_edit, name='support_plan_edit'),
    path('support-plan/<int:support_plan_id>/delete/', views.support_plan_delete, name='support_plan_delete'),
    
    # Progress Reports CRUD
    path('reports/', views.reports, name='reports'),
    path('progress-report/<int:report_id>/', views.progress_report_detail, name='progress_report_detail'),
    path('progress-report/<int:report_id>/edit/', views.progress_report_edit, name='progress_report_edit'),
    path('progress-report/<int:report_id>/delete/', views.progress_report_delete, name='progress_report_delete'),
]

