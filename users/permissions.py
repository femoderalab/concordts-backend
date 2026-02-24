"""
Custom permissions for the School Management System.
"""

from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """
    Only Head of School, Head Master, and Superuser.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        super_admin_roles = ['head', 'hm']
        return request.user.role in super_admin_roles or request.user.is_superuser


class IsAdminOrPrincipal(permissions.BasePermission):
    """
    Allow admin, principal, vice principal, head master, and head of school.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        admin_roles = ['head', 'hm', 'principal', 'vice_principal']
        return request.user.role in admin_roles or request.user.is_staff


class IsTeacherOrAbove(permissions.BasePermission):
    """
    Allow teachers and administrators.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        allowed_roles = [
            'head', 'hm', 'principal', 'vice_principal',
            'teacher', 'form_teacher', 'subject_teacher'
        ]
        return request.user.role in allowed_roles


class IsStudent(permissions.BasePermission):
    """
    Only students.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 'student'


class IsParent(permissions.BasePermission):
    """
    Only parents.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 'parent'


class CanAddStaff(permissions.BasePermission):
    """
    Only super admin can add staff.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        super_admin_roles = ['head', 'hm']
        return request.user.role in super_admin_roles or request.user.is_superuser


class CanAddStudentParent(permissions.BasePermission):
    """
    Super admin, principal, and secretary can add students and parents.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        allowed_roles = ['head', 'hm', 'principal', 'secretary']
        return request.user.role in allowed_roles or request.user.is_superuser


class CanResetPassword(permissions.BasePermission):
    """
    Only admin can reset passwords for others.
    Users must use email-based password reset for themselves.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        admin_roles = ['head', 'hm', 'principal', 'vice_principal']
        return request.user.role in admin_roles or request.user.is_staff


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Allow users to edit their own profile or admin to edit any.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Users can view/update their own profile
        if obj == request.user:
            return True
        
        # Admin can edit anyone
        admin_roles = ['head', 'hm', 'principal', 'vice_principal']
        return request.user.role in admin_roles or request.user.is_staff


class IsAccountant(permissions.BasePermission):
    """
    Only accountants and administrators.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal', 'accountant']
        return request.user.role in allowed_roles


class IsSecretary(permissions.BasePermission):
    """
    Only secretaries and administrators.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal', 'secretary']
        return request.user.role in allowed_roles