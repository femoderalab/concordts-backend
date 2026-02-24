# parents/permissions.py (Updated with HM role)
"""
Custom permissions for the Parents app.
Defines role-based permissions for parent management.
"""

from rest_framework import permissions


class IsParent(permissions.BasePermission):
    """
    Check if user is a parent
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 'parent'


class IsAdminOrPrincipal(permissions.BasePermission):
    """
    Allow only admin/principal/vice principal
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Add 'hm' to allowed roles
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal']
        return request.user.role in allowed_roles or request.user.is_staff


class CanEditParent(permissions.BasePermission):
    """
    Check if user can edit parent profile
    """

    def has_permission(self, request, view):
        """Allow authenticated users to access the view"""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Parent can view/update own profile
        if request.user == obj.user:
            # For updates, check restricted fields
            if request.method in ['PUT', 'PATCH']:
                restricted_fields = [
                    'parent_id', 'is_verified', 'user', 'parent_type',
                    'pta_position', 'declaration_accepted', 'annual_income_range',
                    'spouse', 'is_active'
                ]
                for field in request.data:
                    if field in restricted_fields:
                        return False
            return True

        # Admin/Principal can do anything
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal', 'secretary']
        return request.user.role in allowed_roles or request.user.is_staff


class CanViewParentInfo(permissions.BasePermission):
    """
    Permission to view parent information.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Admin/Principal can view all
        admin_roles = ['head', 'hm', 'principal', 'vice_principal']
        if request.user.role in admin_roles or request.user.is_staff:
            return True

        # Teachers can view parents of their students
        if request.user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            return True

        # Accountant/Secretary can view for administrative purposes
        if request.user.role in ['accountant', 'secretary']:
            return True

        # Parents can view their own info
        if request.user.role == 'parent':
            return True

        return False


class CanAddParent(permissions.BasePermission):
    """
    Permission to add new parents.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_roles = ['head', 'hm', 'principal', 'vice_principal',
                         'teacher', 'form_teacher', 'secretary']
        return request.user.role in allowed_roles or request.user.is_staff


class CanViewChildrenInfo(permissions.BasePermission):
    """
    Permission to view children information.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Parent can view their own children
        if request.user.role == 'parent':
            try:
                parent = request.user.parent_profile
                return obj.father == parent or obj.mother == parent
            except:
                return False

        # Admin/Principal can view all
        admin_roles = ['head', 'hm', 'principal', 'vice_principal']
        if request.user.role in admin_roles or request.user.is_staff:
            return True

        # Class teacher can view students in their class
        if request.user.role in ['teacher', 'form_teacher']:
            return True

        return False


class CanManagePTA(permissions.BasePermission):
    """
    Permission to manage PTA information.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Only admin/principal can manage PTA information
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            allowed_roles = ['head', 'hm', 'principal', 'vice_principal']
            return request.user.role in allowed_roles or request.user.is_staff

        return request.user.is_authenticated


class CanViewFeeInformation(permissions.BasePermission):
    """
    Permission to view fee information.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Parents can access fee endpoints
        if request.user.role == 'parent':
            return True

        # Staff with financial permissions can access
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal',
                         'accountant', 'secretary']
        return request.user.role in allowed_roles or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Parent can view their child's fee information
        if request.user.role == 'parent':
            try:
                parent = request.user.parent_profile
                return obj.father == parent or obj.mother == parent
            except:
                return False

        allowed_roles = ['head', 'hm', 'principal', 'vice_principal',
                         'accountant', 'secretary']
        return request.user.role in allowed_roles or request.user.is_staff


class CanCommunicateWithParents(permissions.BasePermission):
    """
    Permission to send communications to parents.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_roles = ['head', 'hm', 'principal', 'vice_principal',
                         'teacher', 'form_teacher', 'secretary']

        if request.method == 'POST':  # Sending communication
            return request.user.role in allowed_roles or request.user.is_staff

        return request.user.is_authenticated


class IsParentOfStudent(permissions.BasePermission):
    """
    Check if user is parent of a specific student.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.role == 'parent'

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if request.user.role != 'parent':
            return False

        try:
            parent = request.user.parent_profile
            # Check if obj is a Student and parent is father/mother
            if hasattr(obj, 'student'):
                student = obj.student
                return student.father == parent or student.mother == parent

            # Check if obj has a student relationship
            if hasattr(obj, 'father') and hasattr(obj, 'mother'):
                return obj.father == parent or obj.mother == parent

        except:
            return False

        return False


class CanLinkChild(permissions.BasePermission):
    """
    Permission to link children to parents.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Only admin/principal/secretary can link children to parents
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal', 'secretary']
        return request.user.role in allowed_roles or request.user.is_staff


class CanAcceptDeclaration(permissions.BasePermission):
    """
    Permission to accept declaration.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Parents and admin can accept declarations
        if request.user.role == 'parent':
            return True

        allowed_roles = ['head', 'hm', 'principal', 'vice_principal', 'secretary']
        return request.user.role in allowed_roles or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Parent can accept their own declaration
        if request.user == obj.user:
            return True

        allowed_roles = ['head', 'hm', 'principal', 'vice_principal', 'secretary']
        return request.user.role in allowed_roles or request.user.is_staff