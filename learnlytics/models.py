from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Activity(models.Model):
    """Educational activities for children"""
    ACTIVITY_TYPES = [
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('math', 'Mathematics'),
        ('science', 'Science'),
        ('art', 'Art & Creativity'),
        ('music', 'Music'),
        ('physical', 'Physical Activity'),
        ('social', 'Social Skills'),
        ('cognitive', 'Cognitive Development'),
        ('language', 'Language Development'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, 'Beginner'),
        (2, 'Easy'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    difficulty_level = models.IntegerField(choices=DIFFICULTY_LEVELS, default=1)
    
    # Activity details
    instructions = models.TextField(help_text="Step-by-step instructions")
    materials_needed = models.TextField(blank=True, help_text="Required materials")
    estimated_duration = models.IntegerField(help_text="Duration in minutes")
    age_range_min = models.IntegerField(help_text="Minimum age in months")
    age_range_max = models.IntegerField(help_text="Maximum age in months")
    
    # Learning objectives
    learning_objectives = models.TextField(help_text="What children will learn")
    skills_developed = models.TextField(help_text="Skills this activity develops")
    
    # System fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_activities')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} ({self.get_activity_type_display()})"

class ActivityAssignment(models.Model):
    """Assignment of activities to children"""
    child = models.ForeignKey('earlycare.Child', on_delete=models.CASCADE, related_name='assigned_activities')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    # Assignment status
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # Completion tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['child', 'activity']
        ordering = ['-assigned_date']
        verbose_name = "Activity Assignment"
        verbose_name_plural = "Activity Assignments"
    
    def __str__(self):
        return f"{self.child} - {self.activity.title}"

class Badge(models.Model):
    """Achievement badges for children"""
    BADGE_TYPES = [
        ('achievement', 'Achievement'),
        ('participation', 'Participation'),
        ('improvement', 'Improvement'),
        ('milestone', 'Milestone'),
        ('special', 'Special Recognition'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    icon = models.CharField(max_length=50, help_text="Icon class or image name")
    color = models.CharField(max_length=7, default='#FFD700', help_text="Hex color code")
    
    # Requirements
    points_required = models.IntegerField(default=0, help_text="Points needed to earn this badge")
    activities_required = models.IntegerField(default=0, help_text="Number of activities to complete")
    
    # System fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['points_required', 'name']
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
    
    def __str__(self):
        return self.name

class ChildBadge(models.Model):
    """Badges earned by children"""
    child = models.ForeignKey('earlycare.Child', on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='child_badges')
    earned_date = models.DateTimeField(auto_now_add=True)
    earned_for_activity = models.ForeignKey(ActivityAssignment, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['child', 'badge']
        ordering = ['-earned_date']
        verbose_name = "Child Badge"
        verbose_name_plural = "Child Badges"
    
    def __str__(self):
        return f"{self.child} earned {self.badge.name}"

class PerformanceMetric(models.Model):
    """Performance tracking metrics for children"""
    METRIC_TYPES = [
        ('completion_rate', 'Activity Completion Rate'),
        ('time_spent', 'Time Spent on Activities'),
        ('accuracy', 'Accuracy Score'),
        ('engagement', 'Engagement Level'),
        ('improvement', 'Improvement Rate'),
        ('consistency', 'Consistency Score'),
    ]
    
    child = models.ForeignKey('earlycare.Child', on_delete=models.CASCADE, related_name='performance_metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.FloatField(help_text="Metric value")
    max_value = models.FloatField(default=100, help_text="Maximum possible value")
    
    # Context
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)
    period_start = models.DateField(help_text="Start of measurement period")
    period_end = models.DateField(help_text="End of measurement period")
    
    # Additional data
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_metrics')
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name = "Performance Metric"
        verbose_name_plural = "Performance Metrics"
    
    def __str__(self):
        return f"{self.child} - {self.get_metric_type_display()}: {self.value}"
    
    @property
    def percentage(self):
        return (self.value / self.max_value) * 100 if self.max_value > 0 else 0

class Report(models.Model):
    """Analytics and performance reports"""
    REPORT_TYPES = [
        ('child_progress', 'Child Progress Report'),
        ('class_performance', 'Class Performance Report'),
        ('activity_analytics', 'Activity Analytics Report'),
        ('badge_earnings', 'Badge Earnings Report'),
        ('custom', 'Custom Report'),
    ]
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Report scope
    child = models.ForeignKey('earlycare.Child', on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    date_from = models.DateField()
    date_to = models.DateField()
    
    # Report content
    summary = models.TextField(help_text="Executive summary")
    key_findings = models.TextField(help_text="Key findings and insights")
    recommendations = models.TextField(help_text="Recommendations based on data")
    
    # Data visualization
    chart_data = models.JSONField(null=True, blank=True, help_text="Chart configuration and data")
    
    # Export options
    is_exported = models.BooleanField(default=False)
    export_format = models.CharField(max_length=10, choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV')], blank=True)
    export_file = models.FileField(upload_to='reports/', blank=True, null=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = "Report"
        verbose_name_plural = "Reports"
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
