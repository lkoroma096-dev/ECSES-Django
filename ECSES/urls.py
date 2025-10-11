"""
URL configuration for ECSES project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from connecthub import views as connecthub_views

def redirect_to_dashboard(request):
    """Redirect root URL to appropriate dashboard based on user role"""
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
    return redirect('connecthub:home')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_dashboard, name='home'),
    path('connecthub/', include('connecthub.urls')),
    path('earlycare/', include('earlycare.urls')),
    path('learnlytics/', include('learnlytics.urls')),
    # Dashboard URLs for backward compatibility
    path('dashboard/admin/', connecthub_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', connecthub_views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/parent/', connecthub_views.parent_dashboard, name='parent_dashboard'),
    path('dashboard/child/', connecthub_views.child_dashboard, name='child_dashboard'),
]
