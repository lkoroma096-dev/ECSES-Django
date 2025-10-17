from django.contrib import admin
from django.utils.html import format_html
from .models import Activity, ActivityAssignment, Badge, ChildBadge, PerformanceMetric, Report

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    """Activity admin for learning activity management"""
    list_display = ('title', 'activity_type', 'difficulty_level', 'age_range', 'estimated_duration', 'is_active', 'created_by')
    list_filter = ('activity_type', 'difficulty_level', 'is_active', 'created_at', 'created_by__userprofile__role')
    search_fields = ('title', 'description', 'learning_objectives', 'skills_developed', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'activity_type', 'difficulty_level', 'is_active')
        }),
        ('Age and Duration', {
            'fields': ('age_range_min', 'age_range_max', 'estimated_duration')
        }),
        ('Content', {
            'fields': ('instructions', 'materials_needed', 'learning_objectives', 'skills_developed')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def age_range(self, obj):
        return f"{obj.age_range_min}-{obj.age_range_max} months"
    age_range.short_description = 'Age Range'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(ActivityAssignment)
class ActivityAssignmentAdmin(admin.ModelAdmin):
    """Activity Assignment admin for tracking assignments"""
    list_display = ('activity', 'child', 'assigned_by', 'status', 'assigned_date', 'due_date', 'completed_at')
    list_filter = ('status', 'assigned_date', 'due_date', 'assigned_by__userprofile__role')
    search_fields = ('activity__title', 'child__first_name', 'child__last_name', 'assigned_by__username')
    readonly_fields = ('assigned_date', 'started_at', 'completed_at')
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('activity', 'child', 'assigned_by', 'status')
        }),
        ('Dates', {
            'fields': ('assigned_date', 'due_date', 'started_at', 'completed_at')
        }),
        ('Progress', {
            'fields': ('progress_percentage', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('activity', 'child', 'assigned_by')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Badge admin for achievement management"""
    list_display = ('name', 'category', 'points_value', 'icon_display', 'color_display', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'criteria')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Badge Information', {
            'fields': ('name', 'description', 'category', 'is_active')
        }),
        ('Visual Design', {
            'fields': ('icon', 'color')
        }),
        ('Reward System', {
            'fields': ('points_value', 'criteria')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def icon_display(self, obj):
        return format_html('<i class="fas fa-{}"></i>', obj.icon)
    icon_display.short_description = 'Icon'
    
    def color_display(self, obj):
        return format_html('<span style="color: {};">●</span> {}', obj.color, obj.color)
    color_display.short_description = 'Color'

@admin.register(ChildBadge)
class ChildBadgeAdmin(admin.ModelAdmin):
    """Child Badge admin for tracking earned achievements"""
    list_display = ('child', 'badge', 'earned_date', 'awarded_by')
    list_filter = ('earned_date', 'badge__category', 'awarded_by__userprofile__role')
    search_fields = ('child__first_name', 'child__last_name', 'badge__name', 'awarded_by__username')
    readonly_fields = ('earned_date',)
    
    fieldsets = (
        ('Achievement Information', {
            'fields': ('child', 'badge', 'awarded_by', 'earned_date')
        }),
        ('Additional Details', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('child', 'badge', 'awarded_by')

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    """Performance Metric admin for analytics"""
    list_display = ('child', 'activity', 'score', 'time_spent', 'attempts', 'recorded_at')
    list_filter = ('recorded_at', 'activity__activity_type', 'activity__difficulty_level')
    search_fields = ('child__first_name', 'child__last_name', 'activity__title')
    readonly_fields = ('recorded_at',)
    
    fieldsets = (
        ('Performance Data', {
            'fields': ('child', 'activity', 'score', 'time_spent', 'attempts')
        }),
        ('Additional Metrics', {
            'fields': ('accuracy', 'completion_rate', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('recorded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('child', 'activity')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Report admin for analytics and reporting"""
    list_display = ('title', 'report_type', 'generated_by', 'generated_at', 'date_range')
    list_filter = ('report_type', 'generated_at', 'generated_by__userprofile__role')
    search_fields = ('title', 'description', 'generated_by__username')
    readonly_fields = ('generated_at',)
    
    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'description', 'report_type', 'generated_by')
        }),
        ('Data Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Report Data', {
            'fields': ('data', 'summary'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('generated_at',),
            'classes': ('collapse',)
        }),
    )
    
    def date_range(self, obj):
        if obj.start_date and obj.end_date:
            return f"{obj.start_date} to {obj.end_date}"
        return 'N/A'
    date_range.short_description = 'Date Range'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('generated_by')