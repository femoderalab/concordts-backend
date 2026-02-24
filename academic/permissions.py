# academic/permissions.py
"""
Simplified permissions for Academic app.
Removed complex dependencies for now - ERROR FREE VERSION
"""

from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    """Check if user is staff (not student or parent)"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # All non-student, non-parent users are considered staff
        return request.user.role not in ['student', 'parent']


class IsTeacher(permissions.BasePermission):
    """Check if user is a teacher"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        teaching_roles = [
            'teacher', 'form_teacher', 'subject_teacher',
            'head', 'hm', 'principal', 'vice_principal'
        ]
        return request.user.role in teaching_roles


class IsAcademicAdmin(permissions.BasePermission):
    """Check if user is academic admin"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        admin_roles = ['head', 'hm', 'principal', 'vice_principal', 'secretary']
        return request.user.role in admin_roles or request.user.is_staff


class CanManageAcademic(permissions.BasePermission):
    """Check if user can manage academic records"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # For safe methods (GET, HEAD, OPTIONS), allow all staff
        if request.method in permissions.SAFE_METHODS:
            return request.user.role not in ['student', 'parent']
        
        # For modifying methods, only allow admin/principal
        admin_roles = ['head', 'hm', 'principal', 'vice_principal']
        return request.user.role in admin_roles or request.user.is_staff