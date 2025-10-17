from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Child(models.Model):
    """Child profile for early care and development tracking"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_children')
    
    # Additional information
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions or special needs")
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Child"
        verbose_name_plural = "Children"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age_in_months(self):
        from datetime import date
        today = date.today()
        return (today.year - self.date_of_birth.year) * 12 + (today.month - self.date_of_birth.month)

class Assessment(models.Model):
    """Developmental assessments for children"""
    ASSESSMENT_TYPES = [
        ('motor', 'Motor Skills'),
        ('cognitive', 'Cognitive Development'),
        ('language', 'Language Development'),
        ('social', 'Social-Emotional'),
        ('adaptive', 'Adaptive Behavior'),
        ('comprehensive', 'Comprehensive Assessment'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='assessments')
    assessor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conducted_assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    assessment_date = models.DateField()
    
    # Assessment scores (1-5 scale)
    motor_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Motor skills score (1-5)"
    )
    cognitive_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Cognitive development score (1-5)"
    )
    language_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Language development score (1-5)"
    )
    social_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Social-emotional score (1-5)"
    )
    adaptive_score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="Adaptive behavior score (1-5)"
    )
    
    # Overall assessment
    overall_score = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assessment_date']
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
    
    def __str__(self):
        return f"{self.child} - {self.get_assessment_type_display()} ({self.assessment_date})"
    
    def save(self, *args, **kwargs):
        # Calculate overall score if individual scores are provided
        scores = [self.motor_score, self.cognitive_score, self.language_score, 
                 self.social_score, self.adaptive_score]
        valid_scores = [s for s in scores if s is not None]
        if valid_scores:
            self.overall_score = sum(valid_scores) / len(valid_scores)
        super().save(*args, **kwargs)

class SupportPlan(models.Model):
    """Individualized support plans for children"""
    PLAN_STATUS = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
    ]
    
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='support_plan')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_support_plans')
    status = models.CharField(max_length=20, choices=PLAN_STATUS, default='draft')
    
    # Plan details
    goals = models.TextField(help_text="Specific goals for the child", default="Goals will be defined here.")
    strategies = models.TextField(help_text="Strategies to achieve goals", default="Strategies will be outlined here.")
    resources_needed = models.TextField(blank=True, help_text="Resources and materials needed")
    timeline = models.CharField(max_length=200, blank=True, help_text="Expected timeline")
    
    # Review information
    review_date = models.DateField(null=True, blank=True)
    next_review = models.DateField(null=True, blank=True)
    progress_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Support Plan"
        verbose_name_plural = "Support Plans"
    
    def __str__(self):
        return f"Support Plan for {self.child}"

class ProgressReport(models.Model):
    """Progress tracking reports for children"""
    REPORT_TYPES = [
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('custom', 'Custom Report'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='progress_reports')
    title = models.CharField(max_length=200, default='Progress Report')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    report_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    
    # Progress metrics
    summary = models.TextField(help_text="Executive summary of progress", default="Progress report summary will be added here.")
    detailed_report = models.TextField(blank=True, help_text="Detailed progress report")
    academic_progress = models.TextField(blank=True)
    social_progress = models.TextField(blank=True)
    behavioral_progress = models.TextField(blank=True)
    physical_progress = models.TextField(blank=True)
    
    # Overall assessment
    strengths = models.TextField(help_text="Child's strengths and achievements", default="Strengths will be documented here.")
    areas_for_improvement = models.TextField(help_text="Areas needing attention", default="Areas for improvement will be noted here.")
    recommendations = models.TextField(help_text="Recommendations for continued support", default="Recommendations will be provided here.")
    
    # Additional notes
    teacher_notes = models.TextField(blank=True)
    parent_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-report_date']
        verbose_name = "Progress Report"
        verbose_name_plural = "Progress Reports"
    
    def __str__(self):
        return f"{self.child} - {self.get_report_type_display()} ({self.report_date})"
