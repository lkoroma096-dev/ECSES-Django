"""
Role-Based Access Control (RBAC) decorators and utilities for Early Care app.
This module provides comprehensive permission checking for all CRUD operations.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def role_required(*allowed_roles):
    """
    Decorator to check if user has one of the required roles.
    
    Usage:
        @role_required('admin', 'teacher')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please log in to access this page.')
                return redirect('connecthub:login')
            
            # Check if user has a profile
            if not hasattr(request.user, 'userprofile'):
                messages.error(request, 'User profile not found. Please contact administrator.')
                return redirect('home')
            
            # Check if user has admin privileges
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if user's role is in allowed roles
            user_role = request.user.userprofile.role
            if user_role in allowed_roles or 'admin' in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Access denied
            messages.error(request, f'Access denied. Required role(s): {", ".join(allowed_roles)}')
            return redirect('home')
        
        return wrapper
    return decorator


def can_view_child(user, child):
    """Check if user can view a specific child."""
    if not user.is_authenticated:
        return False
    
    # Admin can view all
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return True
    
    # Parent can view their own children
    if hasattr(user, 'userprofile') and user.userprofile.role == 'parent':
        return child.parent == user
    
    # Teacher can view their assigned children
    if hasattr(user, 'userprofile') and user.userprofile.role == 'teacher':
        return child.teacher == user
    
    return False


def can_edit_child(user, child):
    """Check if user can edit a specific child."""
    if not user.is_authenticated:
        return False
    
    # Admin can edit all
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return True
    
    # Parent can edit their own children
    if hasattr(user, 'userprofile') and user.userprofile.role == 'parent':
        return child.parent == user
    
    # Teacher can edit their assigned children
    if hasattr(user, 'userprofile') and user.userprofile.role == 'teacher':
        return child.teacher == user
    
    return False


def can_delete_child(user, child):
    """Check if user can delete a specific child."""
    if not user.is_authenticated:
        return False
    
    # Only admin and parents can delete (with restrictions)
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return True
    
    # Parents can delete their own children
    if hasattr(user, 'userprofile') and user.userprofile.role == 'parent':
        return child.parent == user
    
    return False


def can_create_assessment(user, child):
    """Check if user can create an assessment for a child."""
    if not user.is_authenticated:
        return False
    
    # Admin and teachers can create assessments
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'teacher']):
        # Ensure user has access to the child
        return can_view_child(user, child)
    
    return False


def can_edit_assessment(user, assessment):
    """Check if user can edit an assessment."""
    if not user.is_authenticated:
        return False
    
    # Admin can edit all
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return True
    
    # Assessor (teacher) can edit their own assessments
    if hasattr(user, 'userprofile') and user.userprofile.role == 'teacher':
        return assessment.assessor == user
    
    return False


def can_delete_assessment(user, assessment):
    """Check if user can delete an assessment."""
    if not user.is_authenticated:
        return False
    
    # Only admin can delete assessments
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin')


def can_view_support_plan(user, support_plan):
    """Check if user can view a support plan."""
    if not user.is_authenticated:
        return False
    
    # Admin can view all
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return True
    
    # Parent and teacher can view support plans for their children
    child = support_plan.child
    return can_view_child(user, child)


def can_edit_support_plan(user, support_plan):
    """Check if user can edit a support plan."""
    if not user.is_authenticated:
        return False
    
    # Admin and creator (teacher) can edit
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return True
    
    if hasattr(user, 'userprofile') and user.userprofile.role == 'teacher':
        return support_plan.created_by == user or support_plan.child.teacher == user
    
    return False


def can_create_support_plan(user, child):
    """Check if user can create a support plan for a child."""
    if not user.is_authenticated:
        return False
    
    # Admin and teachers can create support plans
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'teacher']):
        return can_view_child(user, child)
    
    return False


def can_view_progress_report(user, report):
    """Check if user can view a progress report."""
    if not user.is_authenticated:
        return False
    
    # Admin can view all
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return True
    
    # Parent, teacher, and creator can view
    child = report.child
    if can_view_child(user, child):
        return True
    
    if hasattr(user, 'userprofile') and user.userprofile.role == 'teacher':
        return report.created_by == user
    
    return False


def can_edit_progress_report(user, report):
    """Check if user can edit a progress report."""
    if not user.is_authenticated:
        return False
    
    # Admin and creator (teacher) can edit
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return True
    
    if hasattr(user, 'userprofile') and user.userprofile.role == 'teacher':
        return report.created_by == user
    
    return False


def can_create_progress_report(user, child):
    """Check if user can create a progress report for a child."""
    if not user.is_authenticated:
        return False
    
    # Admin and teachers can create reports
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role in ['admin', 'teacher']):
        return can_view_child(user, child)
    
    return False


def get_user_accessible_children(user):
    """Get all children that a user can access based on their role."""
    from .models import Child
    
    if not user.is_authenticated:
        return Child.objects.none()
    
    # Admin can see all
    if user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin'):
        return Child.objects.all()
    
    # Parent can see their children
    if hasattr(user, 'userprofile') and user.userprofile.role == 'parent':
        return Child.objects.filter(parent=user)
    
    # Teacher can see their assigned children
    if hasattr(user, 'userprofile') and user.userprofile.role == 'teacher':
        return Child.objects.filter(teacher=user)
    
    return Child.objects.none()
