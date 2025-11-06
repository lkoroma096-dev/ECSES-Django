from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from .models import Child, Assessment, SupportPlan, ProgressReport
from .permissions import (
    role_required, can_view_child, can_edit_child, can_delete_child,
    can_create_assessment, can_edit_assessment, can_delete_assessment,
    can_view_support_plan, can_edit_support_plan, can_create_support_plan,
    can_view_progress_report, can_edit_progress_report, can_create_progress_report,
    get_user_accessible_children
)

@login_required
def child_list(request):
    """List all children with filtering and search - Filtered by user's access"""
    # Get only children the user has access to
    children = get_user_accessible_children(request.user)
    
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
    return render(request, 'earlycare/child/list.html', context)

@login_required
def child_detail(request, child_id):
    """Detail view for a specific child"""
    child = get_object_or_404(Child, id=child_id)
    
    # Check if user can view this child
    if not can_view_child(request.user, child):
        messages.error(request, 'You do not have permission to view this child.')
        return redirect('earlycare:child_list')
    
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
        'can_edit': can_edit_child(request.user, child),
        'can_delete': can_delete_child(request.user, child),
        'can_create_assessment': can_create_assessment(request.user, child),
        'can_create_support_plan': can_create_support_plan(request.user, child),
        'can_create_progress_report': can_create_progress_report(request.user, child),
    }
    return render(request, 'earlycare/child/detail.html', context)

@role_required('admin', 'parent')
def child_new(request):
    """Create a new child profile - Only admin and parents can create children"""
    if request.method == 'POST':
        # Simple form handling
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        medical_conditions = request.POST.get('medical_conditions', '')
        emergency_contact = request.POST.get('emergency_contact', '')
        emergency_phone = request.POST.get('emergency_phone', '')
        teacher_id = request.POST.get('teacher', None)  # Optional teacher assignment
        
        if first_name and last_name and date_of_birth and gender:
            from django.contrib.auth.models import User
            teacher = None
            if teacher_id:
                try:
                    teacher = User.objects.get(id=teacher_id)
                except User.DoesNotExist:
                    pass
            
            child = Child.objects.create(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                gender=gender,
                parent=request.user,
                teacher=teacher,
                medical_conditions=medical_conditions,
                emergency_contact=emergency_contact,
                emergency_phone=emergency_phone
            )
            messages.success(request, f'Child {child.full_name()} created successfully!')
            return redirect('earlycare:child_detail', child.id)
    
    # Get available teachers for assignment
    try:
        from django.contrib.auth.models import User
        teachers = User.objects.filter(userprofile__role='teacher')
    except:
        teachers = []
    
    context = {
        'teachers': teachers,
    }
    return render(request, 'earlycare/child/form.html', context)

@role_required('admin', 'teacher')
def assessment_new(request):
    """Create a new assessment - Only admin and teachers can create assessments"""
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
        status = request.POST.get('status', 'assigned')
        due_date = request.POST.get('due_date')
        
        if child_id and assessment_type and assessment_date:
            child = get_object_or_404(Child, id=child_id)
            
            # Check if user can create assessment for this child
            if not can_create_assessment(request.user, child):
                messages.error(request, 'You do not have permission to create assessments for this child.')
                return redirect('earlycare:child_list')
            
            assessment = Assessment.objects.create(
                child=child,
                assessor=request.user,
                assessment_type=assessment_type,
                assessment_date=assessment_date,
                due_date=due_date if due_date else None,
                status=status,
                motor_score=int(motor_score) if motor_score else None,
                cognitive_score=int(cognitive_score) if cognitive_score else None,
                language_score=int(language_score) if language_score else None,
                social_score=int(social_score) if social_score else None,
                adaptive_score=int(adaptive_score) if adaptive_score else None,
                notes=notes,
                recommendations=recommendations
            )
            messages.success(request, 'Assessment created successfully!')
            return redirect('earlycare:assessment_detail', assessment.id)
    
    # Get only children the user has access to
    children = get_user_accessible_children(request.user)
    context = {
        'children': children,
    }
    return render(request, 'earlycare/assessment/form.html', context)

@role_required('admin', 'teacher')
def support_plan(request, child_id):
    """View or create support plan for a child - Only admin and teachers"""
    child = get_object_or_404(Child, id=child_id)
    
    # Check if user can view/create support plan for this child
    if not can_view_child(request.user, child):
        messages.error(request, 'You do not have permission to access support plans for this child.')
        return redirect('earlycare:child_list')
    
    try:
        support_plan = child.support_plan
    except SupportPlan.DoesNotExist:
        support_plan = None
    
    if request.method == 'POST':
        goals = request.POST.get('goals')
        strategies = request.POST.get('strategies')
        resources_needed = request.POST.get('resources_needed', '')
        timeline = request.POST.get('timeline', '')
        
        # Check if user can create support plan for this child
        if not support_plan and not can_create_support_plan(request.user, child):
            messages.error(request, 'You do not have permission to create support plans for this child.')
            return redirect('earlycare:child_detail', child.id)
        
        if goals and strategies:
            if support_plan:
                # Check if user can edit
                if not can_edit_support_plan(request.user, support_plan):
                    messages.error(request, 'You do not have permission to edit this support plan.')
                    return redirect('earlycare:child_detail', child.id)
                
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
            messages.success(request, 'Support plan saved successfully!')
            return redirect('earlycare:child_detail', child.id)
    
    context = {
        'child': child,
        'support_plan': support_plan,
        'can_edit': can_edit_support_plan(request.user, support_plan) if support_plan else True,
    }
    return render(request, 'earlycare/support_plan/form.html', context)

@login_required
def assessments(request):
    """List all assessments - Filtered by user's access"""
    # Get only children the user has access to
    accessible_children = get_user_accessible_children(request.user)
    
    # Filter assessments for accessible children
    assessments = Assessment.objects.filter(child__in=accessible_children).order_by('-assessment_date')
    
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
    status = request.GET.get('status')
    if status:
        assessments = assessments.filter(status=status)
    
    # Pagination
    paginator = Paginator(assessments, 12)
    page_number = request.GET.get('page')
    assessments_page = paginator.get_page(page_number)
    
    context = {
        'assessments': assessments_page,
    }
    return render(request, 'earlycare/assessment/list.html', context)

@login_required
def support_plans(request):
    """List all support plans - Filtered by user's access"""
    # Get only children the user has access to
    accessible_children = get_user_accessible_children(request.user)
    
    # Filter support plans for accessible children
    support_plans = SupportPlan.objects.filter(child__in=accessible_children).order_by('-created_at')
    
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
    return render(request, 'earlycare/support_plan/list.html', context)

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
    return render(request, 'earlycare/report/overview.html', context)

@role_required('admin')
def child_assignments(request):
    """Admin view: list children and allow bulk assignment to teachers"""
    from django.contrib.auth.models import User
    children = Child.objects.select_related('parent', 'teacher').order_by('last_name', 'first_name')
    filter_unassigned = request.GET.get('unassigned') == '1'
    if filter_unassigned:
        children = children.filter(teacher__isnull=True)
    teachers = User.objects.filter(userprofile__role='teacher').order_by('first_name', 'last_name')

    if request.method == 'POST':
        child_id = request.POST.get('child_id')
        teacher_id = request.POST.get('teacher_id')
        if child_id and teacher_id:
            child = get_object_or_404(Child, id=child_id)
            previous = child.teacher
            teacher = get_object_or_404(User, id=teacher_id)
            child.teacher = teacher
            child.save()
            if previous and previous != teacher:
                messages.success(request, f"Reassigned {child.first_name} {child.last_name} from {previous.get_full_name() or previous.username} to {teacher.get_full_name() or teacher.username}.")
            else:
                messages.success(request, f"Assigned {child.first_name} {child.last_name} to {teacher.get_full_name() or teacher.username}.")
            # Track recent assignment in session for highlighting section
            recent = request.session.get('recent_assignments', [])
            recent.append({'child_id': child.id, 'child_name': f"{child.first_name} {child.last_name}", 'teacher': teacher.get_full_name() or teacher.username})
            request.session['recent_assignments'] = recent[-5:]
            return redirect('earlycare:child_assignments')

    context = {
        'children': children,
        'teachers': teachers,
        'filter_unassigned': filter_unassigned,
        'recent_assignments': request.session.pop('recent_assignments', []),
    }
    return render(request, 'earlycare/child/assign_list.html', context)

@role_required('admin')
def assign_teacher(request, child_id):
    """Admin view: assign/reassign a single child to a teacher"""
    from django.contrib.auth.models import User
    child = get_object_or_404(Child, id=child_id)
    teachers = User.objects.filter(userprofile__role='teacher').order_by('first_name', 'last_name')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        if teacher_id:
            teacher = get_object_or_404(User, id=teacher_id)
            child.teacher = teacher
            child.save()
            messages.success(request, 'Teacher assignment updated.')
            return redirect('earlycare:child_detail', child.id)

    context = {
        'child': child,
        'teachers': teachers,
    }
    return render(request, 'earlycare/child/assign_form.html', context)

@role_required('admin')
def assign_parent(request, child_id):
    """Admin view: assign/reassign a child's parent"""
    from django.contrib.auth.models import User
    child = get_object_or_404(Child, id=child_id)
    parents = User.objects.filter(userprofile__role='parent').order_by('first_name', 'last_name')

    if request.method == 'POST':
        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent = get_object_or_404(User, id=parent_id)
            prev = child.parent
            child.parent = parent
            child.save()
            if prev and prev != parent:
                messages.success(request, 'Parent reassigned successfully.')
            else:
                messages.success(request, 'Parent assigned successfully.')
            return redirect('earlycare:child_detail', child.id)

    context = {
        'child': child,
        'parents': parents,
    }
    return render(request, 'earlycare/child/assign_parent.html', context)


# ========== ASSESSMENT CRUD OPERATIONS ==========

@login_required
def assessment_detail(request, assessment_id):
    """Detail view for a specific assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Check if user can view this assessment (via child access check)
    if not can_view_child(request.user, assessment.child):
        messages.error(request, 'You do not have permission to view this assessment.')
        return redirect('earlycare:assessments')
    
    context = {
        'assessment': assessment,
        'child': assessment.child,
        'can_edit': can_edit_assessment(request.user, assessment),
        'can_delete': can_delete_assessment(request.user, assessment),
    }
    return render(request, 'earlycare/assessment/detail.html', context)

@login_required
def assessment_edit(request, assessment_id):
    """Edit an existing assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Check if user can edit this assessment
    if not can_edit_assessment(request.user, assessment):
        messages.error(request, 'You do not have permission to edit this assessment.')
        return redirect('earlycare:assessment_detail', assessment.id)
    
    if request.method == 'POST':
        # Update assessment information
        assessment.assessment_type = request.POST.get('assessment_type')
        assessment.assessment_date = request.POST.get('assessment_date')
        assessment.status = request.POST.get('status', assessment.status)
        assessment.due_date = request.POST.get('due_date') if request.POST.get('due_date') else None
        assessment.motor_score = int(request.POST.get('motor_score')) if request.POST.get('motor_score') else None
        assessment.cognitive_score = int(request.POST.get('cognitive_score')) if request.POST.get('cognitive_score') else None
        assessment.language_score = int(request.POST.get('language_score')) if request.POST.get('language_score') else None
        assessment.social_score = int(request.POST.get('social_score')) if request.POST.get('social_score') else None
        assessment.adaptive_score = int(request.POST.get('adaptive_score')) if request.POST.get('adaptive_score') else None
        assessment.notes = request.POST.get('notes', '')
        assessment.recommendations = request.POST.get('recommendations', '')
        
        assessment.save()
        messages.success(request, 'Assessment updated successfully!')
        return redirect('earlycare:assessment_detail', assessment.id)
    
    context = {
        'assessment': assessment,
        'child': assessment.child,
    }
    return render(request, 'earlycare/assessment/form.html', context)

@login_required
def assessment_delete(request, assessment_id):
    """Delete an assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Check if user can delete this assessment
    if not can_delete_assessment(request.user, assessment):
        messages.error(request, 'You do not have permission to delete this assessment.')
        return redirect('earlycare:assessment_detail', assessment.id)
    
    if request.method == 'POST':
        child_id = assessment.child.id
        assessment.delete()
        messages.success(request, 'Assessment has been deleted.')
        return redirect('earlycare:child_detail', child_id)
    
    context = {
        'assessment': assessment,
    }
    return render(request, 'earlycare/assessment/confirm_delete.html', context)

# ========== SUPPORT PLAN CRUD OPERATIONS ==========

@login_required
def support_plan_detail(request, support_plan_id):
    """Detail view for a specific support plan"""
    support_plan = get_object_or_404(SupportPlan, id=support_plan_id)
    
    # Check if user can view this support plan
    if not can_view_support_plan(request.user, support_plan):
        messages.error(request, 'You do not have permission to view this support plan.')
        return redirect('earlycare:support_plans')
    
    context = {
        'support_plan': support_plan,
        'child': support_plan.child,
        'can_edit': can_edit_support_plan(request.user, support_plan),
    }
    return render(request, 'earlycare/support_plan/detail.html', context)

@login_required
def support_plan_edit(request, support_plan_id):
    """Edit an existing support plan"""
    support_plan = get_object_or_404(SupportPlan, id=support_plan_id)
    
    # Check if user can edit this support plan
    if not can_edit_support_plan(request.user, support_plan):
        messages.error(request, 'You do not have permission to edit this support plan.')
        return redirect('earlycare:support_plan_detail', support_plan.id)
    
    if request.method == 'POST':
        # Update support plan
        support_plan.status = request.POST.get('status', support_plan.status)
        support_plan.goals = request.POST.get('goals', '')
        support_plan.strategies = request.POST.get('strategies', '')
        support_plan.resources_needed = request.POST.get('resources_needed', '')
        support_plan.timeline = request.POST.get('timeline', '')
        support_plan.review_date = request.POST.get('review_date') if request.POST.get('review_date') else None
        support_plan.next_review = request.POST.get('next_review') if request.POST.get('next_review') else None
        support_plan.progress_notes = request.POST.get('progress_notes', '')
        
        support_plan.save()
        messages.success(request, 'Support plan updated successfully!')
        return redirect('earlycare:support_plan_detail', support_plan.id)
    
    context = {
        'support_plan': support_plan,
        'child': support_plan.child,
    }
    return render(request, 'earlycare/support_plan/form.html', context)

@login_required
def support_plan_delete(request, support_plan_id):
    """Delete a support plan - Only admin can delete"""
    support_plan = get_object_or_404(SupportPlan, id=support_plan_id)
    
    # Only admin can delete support plans
    if not (request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')):
        messages.error(request, 'You do not have permission to delete support plans.')
        return redirect('earlycare:support_plan_detail', support_plan.id)
    
    if request.method == 'POST':
        child_id = support_plan.child.id
        support_plan.delete()
        messages.success(request, 'Support plan has been deleted.')
        return redirect('earlycare:child_detail', child_id)
    
    context = {
        'support_plan': support_plan,
        'child': support_plan.child,
    }
    return render(request, 'earlycare/support_plan/confirm_delete.html', context)

# ========== PROGRESS REPORT CRUD OPERATIONS ==========

@login_required
def progress_report_detail(request, report_id):
    """Detail view for a specific progress report"""
    report = get_object_or_404(ProgressReport, id=report_id)
    
    # Check if user can view this progress report
    if not can_view_progress_report(request.user, report):
        messages.error(request, 'You do not have permission to view this progress report.')
        return redirect('earlycare:child_list')
    
    context = {
        'report': report,
        'child': report.child,
        'can_edit': can_edit_progress_report(request.user, report),
    }
    return render(request, 'earlycare/report/progress_detail.html', context)

@login_required
def progress_report_edit(request, report_id):
    """Edit an existing progress report"""
    report = get_object_or_404(ProgressReport, id=report_id)
    
    # Check if user can edit this progress report
    if not can_edit_progress_report(request.user, report):
        messages.error(request, 'You do not have permission to edit this progress report.')
        return redirect('earlycare:progress_report_detail', report.id)
    
    if request.method == 'POST':
        # Update progress report
        report.title = request.POST.get('title', report.title)
        report.report_type = request.POST.get('report_type', report.report_type)
        report.report_date = request.POST.get('report_date', report.report_date)
        report.summary = request.POST.get('summary', '')
        report.detailed_report = request.POST.get('detailed_report', '')
        report.academic_progress = request.POST.get('academic_progress', '')
        report.social_progress = request.POST.get('social_progress', '')
        report.behavioral_progress = request.POST.get('behavioral_progress', '')
        report.physical_progress = request.POST.get('physical_progress', '')
        report.strengths = request.POST.get('strengths', '')
        report.areas_for_improvement = request.POST.get('areas_for_improvement', '')
        report.recommendations = request.POST.get('recommendations', '')
        report.teacher_notes = request.POST.get('teacher_notes', '')
        report.parent_feedback = request.POST.get('parent_feedback', '')
        
        report.save()
        messages.success(request, 'Progress report updated successfully!')
        return redirect('earlycare:progress_report_detail', report.id)
    
    context = {
        'report': report,
        'child': report.child,
    }
    return render(request, 'earlycare/report/progress_form.html', context)

@login_required
def progress_report_delete(request, report_id):
    """Delete a progress report - Only admin can delete"""
    report = get_object_or_404(ProgressReport, id=report_id)
    
    # Only admin can delete progress reports
    if not (request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')):
        messages.error(request, 'You do not have permission to delete progress reports.')
        return redirect('earlycare:progress_report_detail', report.id)
    
    if request.method == 'POST':
        child_id = report.child.id
        report.delete()
        messages.success(request, 'Progress report has been deleted.')
        return redirect('earlycare:child_detail', child_id)
    
    context = {
        'report': report,
        'child': report.child,
    }
    return render(request, 'earlycare/report/progress_confirm_delete.html', context)


@login_required
def child_edit(request, child_id):
    """Edit an existing child profile"""
    child = get_object_or_404(Child, id=child_id)
    
    # Check if user can edit this child
    if not can_edit_child(request.user, child):
        messages.error(request, 'You do not have permission to edit this child.')
        return redirect('earlycare:child_detail', child.id)
    
    if request.method == 'POST':
        # Update child information
        child.first_name = request.POST.get('first_name')
        child.last_name = request.POST.get('last_name')
        child.date_of_birth = request.POST.get('date_of_birth')
        child.gender = request.POST.get('gender')
        child.medical_conditions = request.POST.get('medical_conditions', '')
        child.emergency_contact = request.POST.get('emergency_contact', '')
        child.emergency_phone = request.POST.get('emergency_phone', '')
        
        # Update teacher assignment (if admin or parent)
        teacher_id = request.POST.get('teacher', None)
        if teacher_id:
            from django.contrib.auth.models import User
            try:
                teacher = User.objects.get(id=teacher_id)
                child.teacher = teacher
            except User.DoesNotExist:
                pass
        
        child.save()
        messages.success(request, f'Child {child.full_name()} updated successfully!')
        return redirect('earlycare:child_detail', child.id)
    
    # Get available teachers for assignment
    try:
        from django.contrib.auth.models import User
        teachers = User.objects.filter(userprofile__role='teacher')
    except:
        teachers = []
    
    context = {
        'child': child,
        'teachers': teachers,
    }
    return render(request, 'earlycare/child/form.html', context)


@login_required
def child_delete(request, child_id):
    """Delete a child profile"""
    child = get_object_or_404(Child, id=child_id)
    
    # Check if user can delete this child
    if not can_delete_child(request.user, child):
        messages.error(request, 'You do not have permission to delete this child.')
        return redirect('earlycare:child_detail', child.id)
    
    if request.method == 'POST':
        child_name = child.full_name()
        child.delete()
        messages.success(request, f'Child {child_name} has been deleted.')
        return redirect('earlycare:child_list')
    
    context = {
        'child': child,
    }
    return render(request, 'earlycare/child/confirm_delete.html', context)
