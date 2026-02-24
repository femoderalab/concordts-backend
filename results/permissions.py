# results/permissions.py
"""
Custom permissions for the Results App - COMPLETE VERSION
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class CanViewResults(BasePermission):
    """Permission to view results"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Everyone can view results if authenticated (for GET requests)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only specific roles can modify results
        allowed_roles = [
            'head', 'hm', 'principal', 'vice_principal',
            'teacher', 'form_teacher', 'subject_teacher',
            'accountant', 'secretary'
        ]
        
        return user.role in allowed_roles


class CanManageResults(BasePermission):
    """Permission to manage (create, update, delete) results"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Admin roles can manage results
        if user.role in ['head', 'hm', 'principal', 'vice_principal']:
            return True
        
        # Teachers can manage results for their classes
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            # For GET requests, teachers can view
            if request.method in permissions.SAFE_METHODS:
                return True
            
            # For POST/PUT/DELETE, check if they're managing their own class results
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                # Check if they're a class teacher
                try:
                    # Import inside method to avoid circular imports
                    from staff.models import TeacherProfile
                    from academic.models import Class
                    
                    teacher_profile = user.staff_profile.teacher_profile
                    
                    # Check if they're managing results for their assigned classes
                    if 'class_obj' in request.data:
                        class_id = request.data['class_obj']
                        try:
                            class_obj = Class.objects.get(pk=class_id)
                            return class_obj in teacher_profile.assigned_classes.all()
                        except (Class.DoesNotExist, ValueError):
                            return False
                    
                    # If no specific class in request, allow access
                    return True
                except:
                    # If teacher profile doesn't exist, check if they're a class teacher
                    try:
                        # Check if user is assigned as class teacher to any class
                        from academic.models import Class
                        return Class.objects.filter(class_teacher=user).exists()
                    except:
                        return False
        
        # Accountants and secretaries can view but not modify
        if user.role in ['accountant', 'secretary']:
            return request.method in permissions.SAFE_METHODS
        
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage specific result object"""
        user = request.user
        
        if user.role in ['head', 'hm', 'principal', 'vice_principal']:
            return True
        
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            # Teachers can manage results for their classes
            try:
                from staff.models import TeacherProfile
                teacher_profile = user.staff_profile.teacher_profile
                return obj.class_obj in teacher_profile.assigned_classes.all()
            except:
                # Check if user is the class teacher
                return obj.class_teacher == user
        
        return False


class CanPublishResults(BasePermission):
    """Permission to publish results"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Only admin roles can publish results
        return user.role in ['head', 'hm', 'principal', 'vice_principal']


class CanApproveResults(BasePermission):
    """Permission to approve results"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Teachers can approve results as class teachers
        # Admins can approve as headmaster
        return user.role in ['head', 'hm', 'principal', 'vice_principal', 'teacher', 'form_teacher']


class StudentResultPermission(BasePermission):
    """Special permission for student result access"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Users can view their own results if published
        if request.method in permissions.SAFE_METHODS:
            if user.role == 'student':
                # Check if result belongs to student
                try:
                    student_profile = user.student_profile
                    return obj.student == student_profile and obj.is_published
                except:
                    return False
            
            if user.role == 'parent':
                # Check if result belongs to parent's child
                try:
                    parent_profile = user.parent_profile
                    children = parent_profile.children.all()
                    return obj.student in children and obj.is_published
                except:
                    return False
        
        # For modifications, check if user can manage results
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return CanManageResults().has_permission(request, view)
        
        return False


# ADDED: Missing permission class that was causing the import error
class IsResultOwnerOrAdmin(BasePermission):
    """Permission to check if user owns the result or is admin"""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Admin roles have full access
        if user.role in ['head', 'hm', 'principal', 'vice_principal']:
            return True
        
        # Check if user is the student
        if user.role == 'student':
            try:
                return obj.student.user == user
            except:
                return False
        
        # Check if user is parent of the student
        if user.role == 'parent':
            try:
                parent_profile = user.parent_profile
                return obj.student in parent_profile.children.all()
            except:
                return False
        
        # Check if user is the class teacher
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            return obj.class_teacher == user or obj.headmaster == user
        
        return False


# ADDED: Missing permission class
class CanAccessResultStatistics(BasePermission):
    """Permission to access result statistics"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Admin, teachers, and staff can access statistics
        allowed_roles = [
            'head', 'hm', 'principal', 'vice_principal',
            'teacher', 'form_teacher', 'subject_teacher',
            'accountant', 'secretary'
        ]
        
        return user.role in allowed_roles


# ADDED: Missing permission class
class CanBulkUploadResults(BasePermission):
    """Permission to bulk upload results"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        # Only admin and teachers can bulk upload
        allowed_roles = [
            'head', 'hm', 'principal', 'vice_principal',
            'teacher', 'form_teacher'
        ]
        
        return user.role in allowed_roles


# ADDED: Teacher-specific permissions
class IsTeacher(BasePermission):
    """Check if user is a teacher"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        return user.role in ['teacher', 'form_teacher', 'subject_teacher']


# ADDED: Staff permission
class IsStaff(BasePermission):
    """Check if user is staff (non-student, non-parent)"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        return user.role in [
            'head', 'hm', 'principal', 'vice_principal',
            'teacher', 'form_teacher', 'subject_teacher',
            'accountant', 'secretary'
        ]


# ADDED: Head/Principal permission
class IsHeadOrPrincipal(BasePermission):
    """Check if user is head or principal"""
    
    def has_permission(self, request, view):
        user = request.user
        
        if not user.is_authenticated:
            return False
        
        return user.role in ['head', 'hm', 'principal']