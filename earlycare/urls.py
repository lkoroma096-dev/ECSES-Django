from django.urls import path
from . import views

app_name = 'earlycare'

urlpatterns = [
    path('', views.child_list, name='child_list'),
    path('children/', views.child_list, name='child_list'),
    path('child/<int:child_id>/', views.child_detail, name='child_detail'),
    path('child/new/', views.child_new, name='child_new'),
    path('assessment/new/', views.assessment_new, name='assessment_new'),
    path('assessments/', views.assessments, name='assessments'),
    path('support-plan/<int:child_id>/', views.support_plan, name='support_plan'),
    path('support-plans/', views.support_plans, name='support_plans'),
    path('reports/', views.reports, name='reports'),
]

