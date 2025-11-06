"""
Unit tests for permission functions in earlycare.permissions module.
Tests comprehensive RBAC functionality for all CRUD operations.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.db import models
from earlycare.models import Child, Assessment, SupportPlan, ProgressReport
from earlycare.permissions import (
    can_view_child, can_edit_child, can_delete_child,
    can_create_assessment, can_edit_assessment, can_delete_assessment,
    can_view_support_plan, can_edit_support_plan, can_create_support_plan,
    can_view_progress_report, can_edit_progress_report, can_create_progress_report,
    get_user_accessible_children
)
from datetime import date
from connecthub.models import UserProfile


class PermissionTests(TestCase):
    """Test suite for RBAC permission functions"""
    
    def setUp(self):
        """Set up test users and children"""
        # Create users with profiles
        self.admin_user = User.objects.create_user(username='admin', password='test123')
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='admin'
        )
        
        self.teacher_user = User.objects.create_user(username='teacher', password='test123')
        self.teacher_profile = UserProfile.objects.create(
            user=self.teacher_user,
            role='teacher'
        )
        
        self.parent_user = User.objects.create_user(username='parent', password='test123')
        self.parent_profile = UserProfile.objects.create(
            user=self.parent_user,
            role='parent'
        )
        
        self.other_parent_user = User.objects.create_user(username='otherparent', password='test123')
        self.other_parent_profile = UserProfile.objects.create(
            user=self.other_parent_user,
            role='parent'
        )
        
        # Create test children
        self.parents_child = Child.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2020, 1, 1),
            gender='M',
            parent=self.parent_user,
            teacher=self.teacher_user
        )
        
        self.other_parents_child = Child.objects.create(
            first_name='Jane',
            last_name='Smith',
            date_of_birth=date(2020, 1, 2),
            gender='F',
            parent=self.other_parent_user
        )
        
        # Create assessment
        self.assessment = Assessment.objects.create(
            child=self.parents_child,
            assessor=self.teacher_user,
            assessment_type='comprehensive',
            assessment_date=date.today()
        )
        
        # Create support plan
        self.support_plan = SupportPlan.objects.create(
            child=self.parents_child,
            created_by=self.teacher_user,
            status='active'
        )
        
        # Create progress report
        self.progress_report = ProgressReport.objects.create(
            child=self.parents_child,
            created_by=self.teacher_user,
            title='Test Report',
            report_type='monthly',
            report_date=date.today()
        )

    # ========== CHILD PERMISSION TESTS ==========
    
    def test_admin_can_view_all_children(self):
        """Admin should be able to view all children"""
        self.assertTrue(can_view_child(self.admin_user, self.parents_child))
        self.assertTrue(can_view_child(self.admin_user, self.other_parents_child))
    
    def test_teacher_can_view_assigned_children(self):
        """Teacher should be able to view their assigned children"""
        self.assertTrue(can_view_child(self.teacher_user, self.parents_child))
        self.assertFalse(can_view_child(self.teacher_user, self.other_parents_child))
    
    def test_parent_can_view_own_children(self):
        """Parent should be able to view their own children"""
        self.assertTrue(can_view_child(self.parent_user, self.parents_child))
        self.assertFalse(can_view_child(self.parent_user, self.other_parents_child))
    
    def test_admin_can_edit_all_children(self):
        """Admin should be able to edit all children"""
        self.assertTrue(can_edit_child(self.admin_user, self.parents_child))
        self.assertTrue(can_edit_child(self.admin_user, self.other_parents_child))
    
    def test_teacher_can_edit_assigned_children(self):
        """Teacher should be able to edit their assigned children"""
        self.assertTrue(can_edit_child(self.teacher_user, self.parents_child))
        self.assertFalse(can_edit_child(self.teacher_user, self.other_parents_child))
    
    def test_parent_can_edit_own_children(self):
        """Parent should be able to edit their own children"""
        self.assertTrue(can_edit_child(self.parent_user, self.parents_child))
        self.assertFalse(can_edit_child(self.parent_user, self.other_parents_child))
    
    def test_admin_can_delete_all_children(self):
        """Admin should be able to delete all children"""
        self.assertTrue(can_delete_child(self.admin_user, self.parents_child))
        self.assertTrue(can_delete_child(self.admin_user, self.other_parents_child))
    
    def test_parent_can_delete_own_children(self):
        """Parent should be able to delete their own children"""
        self.assertTrue(can_delete_child(self.parent_user, self.parents_child))
        self.assertFalse(can_delete_child(self.parent_user, self.other_parents_child))
    
    def test_teacher_cannot_delete_children(self):
        """Teacher should not be able to delete children"""
        self.assertFalse(can_delete_child(self.teacher_user, self.parents_child))
        self.assertFalse(can_delete_child(self.teacher_user, self.other_parents_child))
    
    # ========== ASSESSMENT PERMISSION TESTS ==========
    
    def test_admin_can_create_assessment_for_any_child(self):
        """Admin should be able to create assessments for any child"""
        self.assertTrue(can_create_assessment(self.admin_user, self.parents_child))
        self.assertTrue(can_create_assessment(self.admin_user, self.other_parents_child))
    
    def test_teacher_can_create_assessment_for_assigned_children(self):
        """Teacher should be able to create assessments for their assigned children"""
        self.assertTrue(can_create_assessment(self.teacher_user, self.parents_child))
        self.assertFalse(can_create_assessment(self.teacher_user, self.other_parents_child))
    
    def test_parent_cannot_create_assessment(self):
        """Parent should not be able to create assessments"""
        self.assertFalse(can_create_assessment(self.parent_user, self.parents_child))
    
    def test_teacher_can_edit_own_assessment(self):
        """Teacher should be able to edit their own assessments"""
        self.assertTrue(can_edit_assessment(self.teacher_user, self.assessment))
        self.assertFalse(can_edit_assessment(self.parent_user, self.assessment))
    
    def test_admin_can_delete_assessment(self):
        """Admin should be able to delete assessments"""
        self.assertTrue(can_delete_assessment(self.admin_user, self.assessment))
        self.assertFalse(can_delete_assessment(self.teacher_user, self.assessment))
        self.assertFalse(can_delete_assessment(self.parent_user, self.assessment))
    
    # ========== SUPPORT PLAN PERMISSION TESTS ==========
    
    def test_admin_can_view_all_support_plans(self):
        """Admin should be able to view all support plans"""
        self.assertTrue(can_view_support_plan(self.admin_user, self.support_plan))
    
    def test_teacher_can_view_support_plan_for_assigned_child(self):
        """Teacher should be able to view support plans for their assigned children"""
        self.assertTrue(can_view_support_plan(self.teacher_user, self.support_plan))
    
    def test_parent_can_view_support_plan_for_own_child(self):
        """Parent should be able to view support plans for their own children"""
        self.assertTrue(can_view_support_plan(self.parent_user, self.support_plan))
    
    def test_admin_can_edit_support_plan(self):
        """Admin should be able to edit all support plans"""
        self.assertTrue(can_edit_support_plan(self.admin_user, self.support_plan))
    
    def test_teacher_can_edit_own_support_plan(self):
        """Teacher should be able to edit their own support plans"""
        self.assertTrue(can_edit_support_plan(self.teacher_user, self.support_plan))
        self.assertFalse(can_edit_support_plan(self.parent_user, self.support_plan))
    
    # ========== PROGRESS REPORT PERMISSION TESTS ==========
    
    def test_admin_can_view_all_progress_reports(self):
        """Admin should be able to view all progress reports"""
        self.assertTrue(can_view_progress_report(self.admin_user, self.progress_report))
    
    def test_teacher_can_view_progress_reports_for_assigned_children(self):
        """Teacher should be able to view progress reports for their assigned children"""
        self.assertTrue(can_view_progress_report(self.teacher_user, self.progress_report))
    
    def test_parent_can_view_progress_reports_for_own_child(self):
        """Parent should be able to view progress reports for their own children"""
        self.assertTrue(can_view_progress_report(self.parent_user, self.progress_report))
    
    def test_teacher_can_edit_own_progress_report(self):
        """Teacher should be able to edit their own progress reports"""
        self.assertTrue(can_edit_progress_report(self.teacher_user, self.progress_report))
        self.assertFalse(can_edit_progress_report(self.parent_user, self.progress_report))
    
    # ========== ACCESSIBLE CHILDREN QUERY TESTS ==========
    
    def test_admin_gets_all_children(self):
        """Admin should get all children"""
        children = get_user_accessible_children(self.admin_user)
        self.assertEqual(children.count(), 2)
        self.assertIn(self.parents_child, children)
        self.assertIn(self.other_parents_child, children)
    
    def test_teacher_gets_only_assigned_children(self):
        """Teacher should get only their assigned children"""
        children = get_user_accessible_children(self.teacher_user)
        self.assertEqual(children.count(), 1)
        self.assertIn(self.parents_child, children)
        self.assertNotIn(self.other_parents_child, children)
    
    def test_parent_gets_only_own_children(self):
        """Parent should get only their own children"""
        children = get_user_accessible_children(self.parent_user)
        self.assertEqual(children.count(), 1)
        self.assertIn(self.parents_child, children)
        self.assertNotIn(self.other_parents_child, children)
    
    def test_unauthenticated_user_gets_no_children(self):
        """Unauthenticated user should get no children"""
        unauthenticated_user = User.objects.create_user(username='unauthenticated', password='test123')
        children = get_user_accessible_children(unauthenticated_user)
        self.assertEqual(children.count(), 0)
    
    def test_user_without_profile_gets_no_children(self):
        """User without profile should get no children"""
        no_profile_user = User.objects.create_user(username='noprofile', password='test123')
        children = get_user_accessible_children(no_profile_user)
        self.assertEqual(children.count(), 0)

