from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

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
    instructions = models.TextField(help_text="Step-by-step instructions", default="Instructions will be provided here.")
    materials_needed = models.TextField(blank=True, help_text="Required materials")
    estimated_duration = models.IntegerField(help_text="Duration in minutes", default=30)
    age_range_min = models.IntegerField(help_text="Minimum age in months", default=0)
    age_range_max = models.IntegerField(help_text="Maximum age in months", default=60)
    
    # Learning objectives
    learning_objectives = models.TextField(help_text="What children will learn", default="Learning objectives will be defined here.")
    skills_developed = models.TextField(help_text="Skills this activity develops", default="Skills developed will be listed here.")
    
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
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['child', 'activity']
        ordering = ['-assigned_date']
        verbose_name = "Activity Assignment"
        verbose_name_plural = "Activity Assignments"
    
    def __str__(self):
        return f"{self.child} - {self.activity.title}"

class Badge(models.Model):
    """Achievement badges for children"""
    CATEGORY_CHOICES = [
        ('achievement', 'Achievement'),
        ('participation', 'Participation'),
        ('improvement', 'Improvement'),
        ('milestone', 'Milestone'),
        ('special', 'Special Recognition'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='achievement')
    icon = models.CharField(max_length=50, help_text="Icon class or image name")
    color = models.CharField(max_length=7, default='#FFD700', help_text="Hex color code")
    
    # Requirements
    points_value = models.IntegerField(default=10, help_text="Points awarded for this badge")
    criteria = models.TextField(help_text="Description of how to earn this badge", default="Complete activities to earn this badge.")
    
    # System fields
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['points_value', 'name']
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
    
    def __str__(self):
        return self.name

class ChildBadge(models.Model):
    """Badges earned by children"""
    child = models.ForeignKey('earlycare.Child', on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='child_badges')
    earned_date = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='awarded_badges', null=True, blank=True)
    earned_for_activity = models.ForeignKey(ActivityAssignment, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
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
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.FloatField(help_text="Performance score", default=0.0)
    time_spent = models.IntegerField(help_text="Time spent in minutes", default=0)
    attempts = models.IntegerField(help_text="Number of attempts", default=1)
    accuracy = models.FloatField(help_text="Accuracy percentage", default=0.0)
    completion_rate = models.FloatField(help_text="Completion rate percentage", default=0.0)
    
    # Additional data
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
        verbose_name = "Performance Metric"
        verbose_name_plural = "Performance Metrics"
    
    def __str__(self):
        return f"{self.child} - {self.activity.title if self.activity else 'General'}: {self.score}"

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
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Report scope
    child = models.ForeignKey('earlycare.Child', on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    start_date = models.DateField(help_text="Start date for report data")
    end_date = models.DateField(help_text="End date for report data")
    
    # Report content
    summary = models.TextField(help_text="Executive summary", default="Report summary will be provided here.")
    data = models.JSONField(null=True, blank=True, help_text="Report data in JSON format")
    key_findings = models.TextField(help_text="Key findings and insights", default="Key findings will be documented here.")
    recommendations = models.TextField(help_text="Recommendations based on data", default="Recommendations will be provided here.")
    
    # Data visualization
    chart_data = models.JSONField(null=True, blank=True, help_text="Chart configuration and data")
    
    # Export options
    is_exported = models.BooleanField(default=False)
    export_format = models.CharField(max_length=10, choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV')], blank=True)
    export_file = models.FileField(upload_to='reports/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-generated_at']
        verbose_name = "Report"
        verbose_name_plural = "Reports"
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
