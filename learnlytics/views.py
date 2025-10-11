from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from .models import Activity, ActivityAssignment, Badge, ChildBadge, PerformanceMetric, Report

@login_required
def activity_list(request):
    """List all activities with filtering and search"""
    activities = Activity.objects.filter(is_active=True)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        activities = activities.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(learning_objectives__icontains=search)
        )
    
    # Activity type filtering
    activity_type = request.GET.get('activity_type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    # Difficulty filtering
    difficulty = request.GET.get('difficulty')
    if difficulty:
        activities = activities.filter(difficulty_level=difficulty)
    
    # Age range filtering
    age_range = request.GET.get('age_range')
    if age_range:
        if age_range == '0-12':
            activities = activities.filter(age_range_max__lte=12)
        elif age_range == '13-24':
            activities = activities.filter(age_range_min__gte=13, age_range_max__lte=24)
        elif age_range == '25-36':
            activities = activities.filter(age_range_min__gte=25, age_range_max__lte=36)
        elif age_range == '37+':
            activities = activities.filter(age_range_min__gte=37)
    
    # Pagination
    paginator = Paginator(activities, 12)
    page_number = request.GET.get('page')
    activities_page = paginator.get_page(page_number)
    
    context = {
        'activities': activities_page,
    }
    return render(request, 'learnlytics/activity_list.html', context)

@login_required
def activity_detail(request, activity_id):
    """Detail view for a specific activity"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Get assignments for this activity
    assignments = ActivityAssignment.objects.filter(activity=activity)
    
    context = {
        'activity': activity,
        'assignments': assignments,
    }
    return render(request, 'learnlytics/activity_detail.html', context)

@login_required
def activity_new(request):
    """Create a new activity"""
    if request.method == 'POST':
        # Simple form handling
        title = request.POST.get('title')
        description = request.POST.get('description')
        activity_type = request.POST.get('activity_type')
        difficulty_level = request.POST.get('difficulty_level')
        instructions = request.POST.get('instructions')
        materials_needed = request.POST.get('materials_needed', '')
        estimated_duration = request.POST.get('estimated_duration')
        age_range_min = request.POST.get('age_range_min')
        age_range_max = request.POST.get('age_range_max')
        learning_objectives = request.POST.get('learning_objectives')
        skills_developed = request.POST.get('skills_developed')
        
        if title and description and activity_type and difficulty_level and instructions:
            activity = Activity.objects.create(
                title=title,
                description=description,
                activity_type=activity_type,
                difficulty_level=int(difficulty_level),
                instructions=instructions,
                materials_needed=materials_needed,
                estimated_duration=int(estimated_duration) if estimated_duration else 30,
                age_range_min=int(age_range_min) if age_range_min else 0,
                age_range_max=int(age_range_max) if age_range_max else 60,
                learning_objectives=learning_objectives,
                skills_developed=skills_developed,
                created_by=request.user
            )
            return redirect('learnlytics:activity_detail', activity.id)
    
    return render(request, 'learnlytics/activity_form.html')

@login_required
def dashboard(request):
    """Analytics dashboard"""
    # Get basic statistics
    total_activities = Activity.objects.count()
    completed_activities = ActivityAssignment.objects.filter(status='completed').count()
    total_badges_earned = ChildBadge.objects.count()
    
    # Calculate average score (placeholder)
    average_score = 3.5
    
    # Get activity completion by type
    completion_labels = ['Reading', 'Math', 'Art', 'Science', 'Physical', 'Social']
    completion_data = [15, 12, 8, 10, 6, 9]  # Placeholder data
    
    # Get performance trends (placeholder)
    trends_labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6']
    trends_data = [3.2, 3.5, 3.8, 4.0, 3.9, 4.2]
    
    # Get badge distribution (placeholder)
    badge_labels = ['Achievement', 'Participation', 'Improvement', 'Milestone', 'Special']
    badge_data = [25, 18, 12, 8, 5]
    
    # Get top performers (placeholder)
    top_performers = []  # Would be populated from actual data
    
    # Get activity statistics
    activity_stats = []  # Would be populated from actual data
    
    context = {
        'total_activities': total_activities,
        'completed_activities': completed_activities,
        'total_badges_earned': total_badges_earned,
        'average_score': average_score,
        'completion_labels': completion_labels,
        'completion_data': completion_data,
        'trends_labels': trends_labels,
        'trends_data': trends_data,
        'badge_labels': badge_labels,
        'badge_data': badge_data,
        'top_performers': top_performers,
        'activity_stats': activity_stats,
    }
    return render(request, 'learnlytics/dashboard.html', context)

@login_required
def assign_activity(request, activity_id=None):
    """Assign activity to children"""
    if request.method == 'POST':
        activity_id = request.POST.get('activity_id')
        child_ids = request.POST.getlist('children')
        due_date = request.POST.get('due_date')
        
        if activity_id and child_ids:
            activity = get_object_or_404(Activity, id=activity_id)
            for child_id in child_ids:
                ActivityAssignment.objects.create(
                    child_id=child_id,
                    activity=activity,
                    assigned_by=request.user,
                    due_date=due_date if due_date else None
                )
            return redirect('learnlytics:activity_list')
    
    # Get activities and children for selection
    activities = Activity.objects.filter(is_active=True)
    children = []  # Would be populated based on user role
    
    context = {
        'activities': activities,
        'children': children,
        'selected_activity_id': activity_id,
    }
    return render(request, 'learnlytics/assign_activity.html', context)

@login_required
def start_activity(request, assignment_id):
    """Start an activity assignment"""
    assignment = get_object_or_404(ActivityAssignment, id=assignment_id, child__user=request.user)
    
    if assignment.status == 'assigned':
        assignment.status = 'in_progress'
        assignment.started_at = timezone.now()
        assignment.save()
        messages.success(request, f'Started activity: {assignment.activity.title}')
        return redirect('learnlytics:activity_detail', assignment.activity.id)
    else:
        messages.error(request, 'This activity cannot be started.')
        return redirect('connecthub:child_dashboard')

@login_required
def continue_activity(request, assignment_id):
    """Continue an activity assignment"""
    assignment = get_object_or_404(ActivityAssignment, id=assignment_id, child__user=request.user)
    
    if assignment.status == 'in_progress':
        messages.info(request, f'Continuing activity: {assignment.activity.title}')
        return redirect('learnlytics:activity_detail', assignment.activity.id)
    else:
        messages.error(request, 'This activity cannot be continued.')
        return redirect('connecthub:child_dashboard')

@login_required
def badges(request):
    """List all badges"""
    badges = Badge.objects.all()
    
    # Get user's earned badges if user is a child
    user_badges = []
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'child':
        user_badges = ChildBadge.objects.filter(child__user=request.user).select_related('badge')
    
    context = {
        'badges': badges,
        'user_badges': user_badges,
    }
    return render(request, 'learnlytics/badges.html', context)

@login_required
def reports(request):
    """Reports overview"""
    # Get basic statistics
    total_activities = Activity.objects.count()
    total_assignments = ActivityAssignment.objects.count()
    total_badges = Badge.objects.count()
    total_reports = Report.objects.count()
    
    context = {
        'total_activities': total_activities,
        'total_assignments': total_assignments,
        'total_badges': total_badges,
        'total_reports': total_reports,
    }
    return render(request, 'learnlytics/analytics_report.html', context)
