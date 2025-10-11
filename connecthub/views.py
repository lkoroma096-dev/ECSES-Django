from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import UserProfile, Message, Notification
from earlycare.models import Child, Assessment, SupportPlan, ProgressReport
from learnlytics.models import Activity, ActivityAssignment, Badge, ChildBadge, PerformanceMetric, Report

def home(request):
    """Home page with role-based redirect"""
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif hasattr(request.user, 'userprofile'):
            role = request.user.userprofile.role
            if role == 'teacher':
                return redirect('teacher_dashboard')
            elif role == 'parent':
                return redirect('parent_dashboard')
            elif role == 'child':
                return redirect('child_dashboard')
    return render(request, 'connecthub/home.html')

def user_login(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'connecthub/login.html')

def user_register(request):
    """User registration view"""
    if request.method == 'POST':
        # Simple registration form handling
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                UserProfile.objects.create(
                    user=user,
                    role=role
                )
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('connecthub:login')
        else:
            messages.error(request, 'Passwords do not match.')
    
    return render(request, 'connecthub/register.html')

@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('connecthub:home')

@login_required
def inbox(request):
    """Message inbox view"""
    messages_list = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')
    
    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)
    
    context = {
        'messages': messages_page,
        'unread_count': Message.objects.filter(recipient=request.user, is_read=False).count()
    }
    return render(request, 'connecthub/inbox.html', context)

@login_required
def notifications(request):
    """Notifications view"""
    notifications_list = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(notifications_list, 10)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    context = {
        'notifications': notifications_page,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
def admin_dashboard(request):
    """Administrator dashboard view"""
    if not (request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Get dashboard statistics
    total_users = User.objects.count()
    total_children = Child.objects.count() if 'earlycare' in globals() else 0
    total_teachers = UserProfile.objects.filter(role='teacher').count()
    total_activities = Activity.objects.count() if 'learnlytics' in globals() else 0
    
    # User counts by role
    teacher_count = UserProfile.objects.filter(role='teacher').count()
    parent_count = UserProfile.objects.filter(role='parent').count()
    child_count = UserProfile.objects.filter(role='child').count()
    
    # Recent messages
    recent_messages = Message.objects.order_by('-created_at')[:5]
    
    # Recent notifications
    recent_notifications = Notification.objects.order_by('-created_at')[:5]
    
    # Chart data (placeholder)
    chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    chart_data = [12, 19, 3, 5, 2, 3]
    
    context = {
        'total_users': total_users,
        'total_children': total_children,
        'total_teachers': total_teachers,
        'total_activities': total_activities,
        'teacher_count': teacher_count,
        'parent_count': parent_count,
        'child_count': child_count,
        'active_assessments': 0,  # Placeholder
        'active_support_plans': 0,  # Placeholder
        'recent_messages': recent_messages,
        'recent_notifications': recent_notifications,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    """Teacher dashboard view"""
    if not (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'teacher'):
        messages.error(request, 'Access denied. Teacher privileges required.')
        return redirect('home')
    
    # Get teacher's assigned children
    if 'earlycare' in globals():
        assigned_children = Child.objects.filter(teacher=request.user)
        assigned_children_count = assigned_children.count()
    else:
        assigned_children = []
        assigned_children_count = 0
    
    # Get unread messages
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    # Recent messages
    recent_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')[:5]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get assessment data
    pending_assessments = 0
    assessments_due_this_week = 0
    completed_assessments = 0
    
    if assigned_children_count > 0 and 'earlycare' in globals():
        from earlycare.models import Assessment
        from datetime import datetime, timedelta
        
        pending_assessments = Assessment.objects.filter(
            child__in=assigned_children, 
            status='pending'
        ).count()
        
        week_from_now = datetime.now() + timedelta(days=7)
        assessments_due_this_week = Assessment.objects.filter(
            child__in=assigned_children,
            due_date__lte=week_from_now,
            status__in=['pending', 'in_progress']
        ).count()
        
        completed_assessments = Assessment.objects.filter(
            child__in=assigned_children,
            status='completed'
        ).count()
    
    # Get activity data
    active_activities = 0
    if assigned_children_count > 0 and 'learnlytics' in globals():
        from learnlytics.models import ActivityAssignment
        active_activities = ActivityAssignment.objects.filter(
            child__in=assigned_children,
            status='in_progress'
        ).count()
    
    # Progress data (mock calculation based on children)
    progress_labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    if assigned_children_count > 0:
        base_progress = 3.0 + (assigned_children_count * 0.1)
        progress_data = [
            base_progress,
            base_progress + 0.3,
            base_progress + 0.6,
            base_progress + 0.9
        ]
    else:
        progress_data = [3.0, 3.3, 3.6, 3.9]
    
    context = {
        'assigned_children': assigned_children[:5] if assigned_children else [],
        'assigned_children_count': assigned_children_count,
        'pending_assessments': pending_assessments,
        'unread_messages': unread_messages,
        'active_activities': active_activities,
        'assessments_due_this_week': assessments_due_this_week,
        'completed_assessments': completed_assessments,
        'recent_messages': recent_messages,
        'recent_notifications': recent_notifications,
        'progress_labels': progress_labels,
        'progress_data': progress_data,
    }
    return render(request, 'dashboards/teacher_dashboard.html', context)

@login_required
def parent_dashboard(request):
    """Parent dashboard view"""
    if not (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'parent'):
        messages.error(request, 'Access denied. Parent privileges required.')
        return redirect('home')
    
    # Get parent's children
    if 'earlycare' in globals():
        my_children = Child.objects.filter(parent=request.user)
        my_children_count = my_children.count()
    else:
        my_children = []
        my_children_count = 0
    
    # Get unread messages
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    # Recent messages
    recent_messages = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')[:5]
    
    # Recent notifications
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get support plans for parent's children
    support_plans = []
    if my_children_count > 0:
        from earlycare.models import SupportPlan
        support_plans = SupportPlan.objects.filter(child__in=my_children).order_by('-created_at')[:5]
    
    # Get recent progress reports
    recent_progress_reports = 0
    if my_children_count > 0:
        from earlycare.models import ProgressReport
        recent_progress_reports = ProgressReport.objects.filter(child__in=my_children).count()
    
    # Get total badges earned by children
    total_badges = 0
    if my_children_count > 0:
        from learnlytics.models import ChildBadge
        total_badges = ChildBadge.objects.filter(child__in=my_children).count()
    
    # Add progress data for children
    for child in my_children:
        # Calculate overall progress (mock calculation)
        child.overall_progress = min(100, (child.age_in_months * 2) + 20)
        
        # Calculate activity completion (mock calculation)
        child.activity_completion = min(100, (child.age_in_months * 3) + 10)
        
        # Get recent badges for this child
        if 'learnlytics' in globals():
            from learnlytics.models import ChildBadge
            child.recent_badges = ChildBadge.objects.filter(child=child).order_by('-earned_date')[:3]
        else:
            child.recent_badges = []
    
    context = {
        'my_children': my_children,
        'my_children_count': my_children_count,
        'recent_progress_reports': recent_progress_reports,
        'unread_messages': unread_messages,
        'total_badges': total_badges,
        'recent_messages': recent_messages,
        'recent_notifications': recent_notifications,
        'support_plans': support_plans,
    }
    return render(request, 'dashboards/parent_dashboard.html', context)

@login_required
def child_dashboard(request):
    """Child dashboard view"""
    if not (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'child'):
        messages.error(request, 'Access denied. Child privileges required.')
        return redirect('home')
    
    # Get child's activities
    my_activities = []
    my_activities_count = 0
    completed_activities = 0
    
    if 'learnlytics' in globals():
        from learnlytics.models import ActivityAssignment
        my_activities = ActivityAssignment.objects.filter(child__user=request.user).order_by('-assigned_date')[:6]
        my_activities_count = ActivityAssignment.objects.filter(child__user=request.user).count()
        completed_activities = ActivityAssignment.objects.filter(child__user=request.user, status='completed').count()
    
    # Get badges
    my_badges = []
    my_badges_count = 0
    
    if 'learnlytics' in globals():
        from learnlytics.models import ChildBadge
        my_badges = ChildBadge.objects.filter(child__user=request.user).order_by('-earned_date')[:6]
        my_badges_count = ChildBadge.objects.filter(child__user=request.user).count()
    
    # Calculate points (mock data based on activities and badges)
    my_points = (completed_activities * 10) + (my_badges_count * 25)
    
    # Calculate progress data
    overall_progress = min(100, (completed_activities * 10) + 20) if my_activities_count > 0 else 0
    activity_completion = min(100, (completed_activities / my_activities_count * 100)) if my_activities_count > 0 else 0
    
    # Mock learning streak and activity counts
    learning_streak = min(30, completed_activities + 2)
    activities_this_week = min(7, completed_activities // 4)
    activities_this_month = min(30, completed_activities)
    
    # Teacher feedback (mock data)
    teacher_feedback = []
    if my_activities.exists():
        # Create mock feedback for completed activities
        for activity in my_activities.filter(status='completed')[:3]:
            feedback_item = type('MockFeedback', (), {
                'activity': activity.activity,
                'notes': f"Great work on {activity.activity.title}! Keep up the excellent progress.",
                'created_at': activity.completed_at or activity.assigned_date,
                'teacher': activity.activity.created_by if hasattr(activity.activity, 'created_by') else request.user
            })()
            teacher_feedback.append(feedback_item)
    
    context = {
        'my_activities': my_activities,
        'my_activities_count': my_activities_count,
        'completed_activities': completed_activities,
        'my_badges': my_badges,
        'my_badges_count': my_badges_count,
        'my_points': my_points,
        'overall_progress': overall_progress,
        'activity_completion': activity_completion,
        'learning_streak': learning_streak,
        'activities_this_week': activities_this_week,
        'activities_this_month': activities_this_month,
        'teacher_feedback': teacher_feedback,
    }
    return render(request, 'dashboards/child_dashboard.html', context)

@login_required
def user_management(request):
    """User management view for administrators"""
    if not (request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Get search parameters
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    # Base queryset
    users = User.objects.select_related('userprofile').all()
    
    # Apply filters
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(userprofile__role=role_filter)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    # Get role counts for statistics
    role_counts = UserProfile.objects.values('role').annotate(count=Count('role'))
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'role_filter': role_filter,
        'role_counts': role_counts,
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'connecthub/user_management.html', context)

@login_required
def create_user(request):
    """Create new user view for administrators"""
    if not (request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        
        # Validation
        if not all([first_name, last_name, username, email, password1, password2, role]):
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name
                )
                UserProfile.objects.create(
                    user=user,
                    role=role,
                    phone=phone,
                    address=address
                )
                messages.success(request, f'User {username} created successfully!')
                return redirect('connecthub:user_management')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
    
    context = {
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'connecthub/create_user.html', context)

@login_required
def edit_user(request, user_id):
    """Edit user view for administrators"""
    if not (request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user_profile.role = request.POST.get('role')
        user_profile.phone = request.POST.get('phone', '')
        user_profile.address = request.POST.get('address', '')
        
        # Check if username is being changed
        new_username = request.POST.get('username')
        if new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'connecthub/edit_user.html', {
                    'user_obj': user,
                    'user_profile': user_profile,
                    'role_choices': UserProfile.ROLE_CHOICES,
                })
            user.username = new_username
        
        # Check if email is being changed
        if user.email != request.POST.get('email'):
            if User.objects.filter(email=request.POST.get('email')).exists():
                messages.error(request, 'Email already exists.')
                return render(request, 'connecthub/edit_user.html', {
                    'user_obj': user,
                    'user_profile': user_profile,
                    'role_choices': UserProfile.ROLE_CHOICES,
                })
        
        try:
            user.save()
            user_profile.save()
            messages.success(request, f'User {user.username} updated successfully!')
            return redirect('connecthub:user_management')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    context = {
        'user_obj': user,
        'user_profile': user_profile,
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'connecthub/edit_user.html', context)

@login_required
def delete_user(request, user_id):
    """Delete user view for administrators"""
    if not (request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent admin from deleting themselves
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('connecthub:user_management')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('connecthub:user_management')
    
    context = {
        'user_obj': user,
    }
    return render(request, 'connecthub/delete_user.html', context)

@login_required
def profile(request):
    """User profile view - view and edit own profile"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        # Update user basic information
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        
        # Update profile information
        user_profile.phone = request.POST.get('phone', '')
        user_profile.address = request.POST.get('address', '')
        user_profile.date_of_birth = request.POST.get('date_of_birth') or None
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user_profile.profile_picture = request.FILES['profile_picture']
        
        try:
            request.user.save()
            user_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('connecthub:profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'connecthub/profile.html', context)

@login_required
def settings(request):
    """User settings view - manage preferences and account settings"""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        # Handle password change
        if 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if request.user.check_password(current_password):
                if new_password1 == new_password2:
                    if len(new_password1) >= 8:
                        request.user.set_password(new_password1)
                        request.user.save()
                        messages.success(request, 'Password changed successfully!')
                    else:
                        messages.error(request, 'New password must be at least 8 characters long.')
                else:
                    messages.error(request, 'New passwords do not match.')
            else:
                messages.error(request, 'Current password is incorrect.')
        
        # Handle account deactivation
        elif 'deactivate_account' in request.POST:
            request.user.is_active = False
            request.user.save()
            messages.warning(request, 'Your account has been deactivated.')
            return redirect('connecthub:logout')
        
        # Handle notification preferences (placeholder for future implementation)
        elif 'update_notifications' in request.POST:
            messages.info(request, 'Notification preferences updated!')
        
        return redirect('connecthub:settings')
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'connecthub/settings.html', context)

@login_required
def compose_message(request):
    """Compose new message view"""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        if recipient_id and subject and content:
            try:
                recipient = User.objects.get(id=recipient_id)
                Message.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    subject=subject,
                    content=content
                )
                messages.success(request, 'Message sent successfully!')
                return redirect('connecthub:inbox')
            except User.DoesNotExist:
                messages.error(request, 'Recipient not found.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    # Get users for recipient selection (exclude current user)
    users = User.objects.exclude(id=request.user.id).select_related('userprofile')
    
    context = {
        'users': users,
    }
    return render(request, 'connecthub/compose_message.html', context)

@login_required
def message_detail(request, message_id):
    """View message detail and mark as read"""
    message = get_object_or_404(Message, id=message_id)
    
    # Mark as read if current user is recipient
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.save()
    
    context = {
        'message': message,
    }
    return render(request, 'connecthub/message_detail.html', context)

@login_required
def reply_message(request, message_id):
    """Reply to a message"""
    original_message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        subject = f"Re: {original_message.subject}"
        content = request.POST.get('content')
        
        if content:
            Message.objects.create(
                sender=request.user,
                recipient=original_message.sender,
                subject=subject,
                content=content
            )
            messages.success(request, 'Reply sent successfully!')
            return redirect('connecthub:inbox')
        else:
            messages.error(request, 'Please enter a message.')
    
    context = {
        'original_message': original_message,
    }
    return render(request, 'connecthub/reply_message.html', context)

@login_required
def send_notification(request):
    """Send system notification (admin only)"""
    if not (request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'admin')):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        notification_type = request.POST.get('notification_type', 'info')
        target_users = request.POST.getlist('target_users')
        
        if title and message:
            try:
                if target_users:
                    # Send to specific users
                    for user_id in target_users:
                        user = User.objects.get(id=user_id)
                        Notification.objects.create(
                            user=user,
                            title=title,
                            message=message,
                            notification_type=notification_type
                        )
                else:
                    # Send to all users
                    users = User.objects.all()
                    for user in users:
                        Notification.objects.create(
                            user=user,
                            title=title,
                            message=message,
                            notification_type=notification_type
                        )
                
                messages.success(request, 'Notification sent successfully!')
                return redirect('connecthub:notifications')
            except Exception as e:
                messages.error(request, f'Error sending notification: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get all users for targeting
    users = User.objects.select_related('userprofile').all()
    
    context = {
        'users': users,
    }
    return render(request, 'connecthub/send_notification.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, 'Notification marked as read.')
    return redirect('connecthub:notifications')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('connecthub:notifications')
