from django.contrib import admin
from django.utils.html import format_html
from .models import Child, Assessment, SupportPlan, ProgressReport

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    """Child admin with comprehensive management features"""
    list_display = ('full_name', 'age_display', 'gender', 'parent', 'teacher', 'is_active', 'created_at')
    list_filter = ('gender', 'is_active', 'created_at', 'parent__userprofile__role', 'teacher__userprofile__role')
    search_fields = ('first_name', 'last_name', 'parent__username', 'teacher__username', 'medical_conditions')
    readonly_fields = ('age_in_months', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'is_active')
        }),
        ('Family Information', {
            'fields': ('parent', 'teacher')
        }),
        ('Medical Information', {
            'fields': ('medical_conditions', 'emergency_contact', 'emergency_phone'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
    
    def age_display(self, obj):
        return f"{obj.age_in_months} months"
    age_display.short_description = 'Age'
    age_display.admin_order_field = 'age_in_months'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent', 'teacher')

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """Assessment admin for tracking child development"""
    list_display = ('child', 'assessment_type', 'assessor', 'assessment_date', 'overall_score')
    list_filter = ('assessment_type', 'assessment_date', 'assessor__userprofile__role')
    search_fields = ('child__first_name', 'child__last_name', 'assessor__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Assessment Information', {
            'fields': ('child', 'assessor', 'assessment_type', 'assessment_date')
        }),
        ('Scores', {
            'fields': ('motor_score', 'cognitive_score', 'language_score', 'social_score', 'adaptive_score')
        }),
        ('Details', {
            'fields': ('notes', 'recommendations')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def overall_score(self, obj):
        scores = [obj.motor_score, obj.cognitive_score, obj.language_score, obj.social_score, obj.adaptive_score]
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            avg = sum(valid_scores) / len(valid_scores)
            color = 'success' if avg >= 4 else 'warning' if avg >= 3 else 'danger'
            return format_html('<span class="badge bg-{}">{:.1f}</span>', color, avg)
        return 'N/A'
    overall_score.short_description = 'Overall Score'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('child', 'assessor')

@admin.register(SupportPlan)
class SupportPlanAdmin(admin.ModelAdmin):
    """Support Plan admin for individualized education plans"""
    list_display = ('child', 'created_by', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'created_by__userprofile__role')
    search_fields = ('child__first_name', 'child__last_name', 'goals', 'strategies', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('child', 'created_by', 'status')
        }),
        ('Plan Details', {
            'fields': ('goals', 'strategies', 'resources_needed', 'timeline')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('child', 'created_by')

@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    """Progress Report admin for tracking child progress"""
    list_display = ('title', 'child', 'created_by', 'report_date', 'created_at')
    list_filter = ('report_date', 'created_at', 'created_by__userprofile__role')
    search_fields = ('title', 'summary', 'child__first_name', 'child__last_name', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'child', 'created_by', 'report_date')
        }),
        ('Report Content', {
            'fields': ('summary', 'detailed_report', 'recommendations')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('child', 'created_by')