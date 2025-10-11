from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Child, Assessment, SupportPlan, ProgressReport

@login_required
def child_list(request):
    """List all children with filtering and search"""
    children = Child.objects.all()
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        children = children.filter(
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search)
        )
    
    # Age range filtering
    age_range = request.GET.get('age_range')
    if age_range:
        if age_range == '0-12':
            children = children.filter(age_in_months__lte=12)
        elif age_range == '13-24':
            children = children.filter(age_in_months__gte=13, age_in_months__lte=24)
        elif age_range == '25-36':
            children = children.filter(age_in_months__gte=25, age_in_months__lte=36)
        elif age_range == '37+':
            children = children.filter(age_in_months__gte=37)
    
    # Status filtering
    status = request.GET.get('status')
    if status:
        children = children.filter(is_active=(status == 'active'))
    
    # Pagination
    paginator = Paginator(children, 12)
    page_number = request.GET.get('page')
    children_page = paginator.get_page(page_number)
    
    context = {
        'children': children_page,
    }
    return render(request, 'earlycare/child_list.html', context)

@login_required
def child_detail(request, child_id):
    """Detail view for a specific child"""
    child = get_object_or_404(Child, id=child_id)
    
    # Get recent assessments
    recent_assessments = Assessment.objects.filter(child=child).order_by('-assessment_date')[:5]
    
    # Get support plan if exists
    try:
        support_plan = child.support_plan
    except SupportPlan.DoesNotExist:
        support_plan = None
    
    # Get recent progress reports
    recent_reports = ProgressReport.objects.filter(child=child).order_by('-report_date')[:5]
    
    context = {
        'child': child,
        'recent_assessments': recent_assessments,
        'support_plan': support_plan,
        'recent_reports': recent_reports,
    }
    return render(request, 'earlycare/child_detail.html', context)

@login_required
def child_new(request):
    """Create a new child profile"""
    if request.method == 'POST':
        # Simple form handling
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        medical_conditions = request.POST.get('medical_conditions', '')
        emergency_contact = request.POST.get('emergency_contact', '')
        emergency_phone = request.POST.get('emergency_phone', '')
        
        if first_name and last_name and date_of_birth and gender:
            child = Child.objects.create(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                gender=gender,
                parent=request.user,
                medical_conditions=medical_conditions,
                emergency_contact=emergency_contact,
                emergency_phone=emergency_phone
            )
            return redirect('earlycare:child_detail', child.id)
    
    return render(request, 'earlycare/child_form.html')

@login_required
def assessment_new(request):
    """Create a new assessment"""
    if request.method == 'POST':
        # Simple form handling
        child_id = request.POST.get('child')
        assessment_type = request.POST.get('assessment_type')
        assessment_date = request.POST.get('assessment_date')
        motor_score = request.POST.get('motor_score')
        cognitive_score = request.POST.get('cognitive_score')
        language_score = request.POST.get('language_score')
        social_score = request.POST.get('social_score')
        adaptive_score = request.POST.get('adaptive_score')
        notes = request.POST.get('notes', '')
        recommendations = request.POST.get('recommendations', '')
        
        if child_id and assessment_type and assessment_date:
            child = get_object_or_404(Child, id=child_id)
            assessment = Assessment.objects.create(
                child=child,
                assessor=request.user,
                assessment_type=assessment_type,
                assessment_date=assessment_date,
                motor_score=int(motor_score) if motor_score else None,
                cognitive_score=int(cognitive_score) if cognitive_score else None,
                language_score=int(language_score) if language_score else None,
                social_score=int(social_score) if social_score else None,
                adaptive_score=int(adaptive_score) if adaptive_score else None,
                notes=notes,
                recommendations=recommendations
            )
            return redirect('earlycare:child_detail', child.id)
    
    # Get children for dropdown
    children = Child.objects.all()
    context = {
        'children': children,
    }
    return render(request, 'earlycare/assessment_form.html', context)

@login_required
def support_plan(request, child_id):
    """View or create support plan for a child"""
    child = get_object_or_404(Child, id=child_id)
    
    try:
        support_plan = child.support_plan
    except SupportPlan.DoesNotExist:
        support_plan = None
    
    if request.method == 'POST':
        goals = request.POST.get('goals')
        strategies = request.POST.get('strategies')
        resources_needed = request.POST.get('resources_needed', '')
        timeline = request.POST.get('timeline', '')
        
        if goals and strategies:
            if support_plan:
                support_plan.goals = goals
                support_plan.strategies = strategies
                support_plan.resources_needed = resources_needed
                support_plan.timeline = timeline
                support_plan.save()
            else:
                support_plan = SupportPlan.objects.create(
                    child=child,
                    created_by=request.user,
                    goals=goals,
                    strategies=strategies,
                    resources_needed=resources_needed,
                    timeline=timeline
                )
            return redirect('earlycare:child_detail', child.id)
    
    context = {
        'child': child,
        'support_plan': support_plan,
    }
    return render(request, 'earlycare/support_plan.html', context)

@login_required
def assessments(request):
    """List all assessments"""
    assessments = Assessment.objects.all().order_by('-assessment_date')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        assessments = assessments.filter(
            Q(child__first_name__icontains=search) | 
            Q(child__last_name__icontains=search) |
            Q(assessment_type__icontains=search)
        )
    
    # Assessment type filtering
    assessment_type = request.GET.get('assessment_type')
    if assessment_type:
        assessments = assessments.filter(assessment_type=assessment_type)
    
    # Pagination
    paginator = Paginator(assessments, 12)
    page_number = request.GET.get('page')
    assessments_page = paginator.get_page(page_number)
    
    context = {
        'assessments': assessments_page,
    }
    return render(request, 'earlycare/assessments.html', context)

@login_required
def support_plans(request):
    """List all support plans"""
    support_plans = SupportPlan.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        support_plans = support_plans.filter(
            Q(child__first_name__icontains=search) | 
            Q(child__last_name__icontains=search) |
            Q(goals__icontains=search)
        )
    
    # Status filtering
    status = request.GET.get('status')
    if status:
        support_plans = support_plans.filter(status=status)
    
    # Pagination
    paginator = Paginator(support_plans, 12)
    page_number = request.GET.get('page')
    support_plans_page = paginator.get_page(page_number)
    
    context = {
        'support_plans': support_plans_page,
    }
    return render(request, 'earlycare/support_plans.html', context)

@login_required
def reports(request):
    """Reports overview"""
    # Get basic statistics
    total_children = Child.objects.count()
    total_assessments = Assessment.objects.count()
    total_support_plans = SupportPlan.objects.count()
    total_reports = ProgressReport.objects.count()
    
    context = {
        'total_children': total_children,
        'total_assessments': total_assessments,
        'total_support_plans': total_support_plans,
        'total_reports': total_reports,
    }
    return render(request, 'earlycare/report_overview.html', context)
