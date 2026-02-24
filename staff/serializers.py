# staff/serializers.py (Updated with all fixes)
"""
Serializers for the Staff model and related operations.
Converts between Python objects and JSON for API communication.
"""

from rest_framework import serializers
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .models import Staff, StaffPermission
from academic.models import TeacherProfile
from users.models import User  # Direct import from users app


# =====================
# MINI SERIALIZERS FOR RELATED MODELS
# =====================

class SubjectMiniSerializer(serializers.Serializer):
    """Lightweight subject serializer"""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    subject_type = serializers.CharField(read_only=True)


class ClassLevelMiniSerializer(serializers.Serializer):
    """Lightweight class level serializer"""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    level = serializers.CharField(read_only=True)


class ClassMiniSerializer(serializers.Serializer):
    """Lightweight class serializer"""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    class_level = ClassLevelMiniSerializer(read_only=True)


# =====================
# STAFF PERMISSION SERIALIZER
# =====================

class StaffPermissionSerializer(serializers.ModelSerializer):
    """Serializer for StaffPermission model"""
    
    class Meta:
        model = StaffPermission
        fields = '__all__'
        read_only_fields = ['id', 'staff', 'created_at', 'updated_at']


# =====================
# TEACHER PROFILE SERIALIZER
# =====================

class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer for TeacherProfile model"""
    
    subjects_info = SubjectMiniSerializer(source='subjects', many=True, read_only=True)
    primary_subject_info = SubjectMiniSerializer(source='primary_subject', read_only=True)
    class_levels_info = ClassLevelMiniSerializer(source='class_levels', many=True, read_only=True)
    assigned_classes_info = ClassMiniSerializer(source='assigned_classes', many=True, read_only=True)
    assistant_classes_info = ClassMiniSerializer(source='assistant_classes', many=True, read_only=True)
    hod_subjects_info = SubjectMiniSerializer(source='hod_subjects', many=True, read_only=True)
    
    workload_percentage = serializers.SerializerMethodField(read_only=True)
    workload_status = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = '__all__'
        read_only_fields = [
            'id', 'staff', 'created_at', 'updated_at',
            'workload_percentage', 'workload_status'
        ]
    
    def get_workload_percentage(self, obj):
        try:
            return obj.get_workload_percentage()
        except Exception:
            return 0
    
    def get_workload_status(self, obj):
        try:
            return obj.get_workload_status()
        except Exception:
            return "Unknown"


# =====================
# MAIN STAFF SERIALIZER
# =====================

# class StaffSerializer(serializers.ModelSerializer):
#     """Main serializer for Staff model"""
    
#     user = serializers.SerializerMethodField(read_only=True)
#     staff_type = serializers.SerializerMethodField(read_only=True)
#     employment_duration = serializers.SerializerMethodField(read_only=True)
    
#     # Nested profiles
#     teacher_profile = TeacherProfileSerializer(read_only=True)
#     permissions = StaffPermissionSerializer(read_only=True)
    
#     # Display fields for choices
#     employment_type_display = serializers.CharField(
#         source='get_employment_type_display',
#         read_only=True
#     )
#     department_display = serializers.CharField(
#         source='get_department_display',
#         read_only=True
#     )
    
#     class Meta:
#         model = Staff
#         fields = '__all__'
#         read_only_fields = [
#             'id', 'user', 'staff_id', 'created_at', 'updated_at',
#             'staff_type', 'employment_duration', 'employment_type_display',
#             'department_display', 'teacher_profile', 'permissions'
#         ]
    
#     def get_user(self, obj):
#         """Get user information"""
#         user_data = {
#             'id': obj.user.id,
#             'full_name': obj.user.get_full_name(),
#             'email': obj.user.email,
#             'phone_number': obj.user.phone_number,
#             'registration_number': obj.user.registration_number,
#             'date_of_birth': obj.user.date_of_birth,
#             'gender': obj.user.get_gender_display() if obj.user.gender else None,
#             'address': obj.user.address,
#             'city': obj.user.city,
#             'state_of_origin': obj.user.state_of_origin,
#             'lga': obj.user.lga,
#             'nationality': obj.user.nationality,
#             'role': obj.user.role,
#             'role_display': obj.user.get_role_display(),
#             'is_active': obj.user.is_active,
#             'is_verified': obj.user.is_verified,
#         }
        
#         # Handle profile picture safely
#         if obj.user.profile_picture and hasattr(obj.user.profile_picture, 'url'):
#             user_data['profile_picture'] = obj.user.profile_picture.url
#         else:
#             user_data['profile_picture'] = None
            
#         return user_data
    
#     def get_staff_type(self, obj):
#         try:
#             return obj.get_staff_type()
#         except Exception:
#             return 'unknown'
    
#     def get_employment_duration(self, obj):
#         try:
#             return obj.get_employment_duration()
#         except Exception:
#             return {'years': 0, 'months': 0, 'days': 0}

class StaffSerializer(serializers.ModelSerializer):
    """
    Staff serializer with complete user data
    """
    # CRITICAL: Add user data to response
    user = serializers.SerializerMethodField()
    
    # Display fields
    department_display = serializers.CharField(
        source='get_department_display', 
        read_only=True
    )
    employment_type_display = serializers.CharField(
        source='get_employment_type_display', 
        read_only=True
    )
    
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'staff_id', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        """
        Include user data in staff response
        This fixes the "Unknown Staff" and "No email" issues
        """
        if not obj.user:
            return None
        
        user = obj.user
        return {
            'id': user.id,
            'full_name': user.get_full_name(),
            'email': user.email,
            'phone_number': user.phone_number,
            'gender': user.get_gender_display() if user.gender else None,
            'date_of_birth': user.date_of_birth,
            'address': user.address,
            'city': user.city,
            'state_of_origin': user.state_of_origin,
            'lga': user.lga,
            'nationality': user.nationality,
            'registration_number': user.registration_number,
            'role': user.role,
            'role_display': user.get_role_display() if user.role else None,
            'is_active': user.is_active,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
        }

# =====================
# STAFF CREATE SERIALIZER
# =====================

class StaffCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating staff profiles"""
    
    user_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Staff
        fields = [
            'user_id',
            'employment_date',
            'employment_type',
            'department',
            'position_title',
            'highest_qualification',
            'qualification_institution',
            'year_of_graduation',
            'professional_certifications',
            'trcn_number',
            'trcn_expiry_date',
            'specialization',
            'basic_salary',
            'salary_scale',
            'salary_step',
            'bank_name',
            'account_name',
            'account_number',
            'annual_leave_days',
            'sick_leave_days',
            'next_of_kin_name',
            'next_of_kin_relationship',
            'next_of_kin_phone',
            'next_of_kin_address',
            'blood_group',
            'genotype',
            'medical_conditions',
            'allergies',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'years_of_experience',
            'previous_employers',
            'references',
            'resume',
            'certificates',
            'id_copy',
            'passport_photo'
        ]
    
    def validate_user_id(self, value):
        """Validate user exists and is not already staff"""
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        
        # Check if user is already a staff
        if Staff.objects.filter(user=user).exists():
            raise serializers.ValidationError("User is already a staff member")
        
        return value
    
    def validate_basic_salary(self, value):
        """Validate basic salary"""
        if value < 0:
            raise serializers.ValidationError("Basic salary cannot be negative")
        return value
    
    def validate_trcn_number(self, value):
        """Validate TRCN number if provided"""
        if value and Staff.objects.filter(trcn_number=value).exists():
            raise serializers.ValidationError("TRCN number already exists")
        return value
    
    def validate(self, data):
        """Validate staff data"""
        
        # Validate TRCN expiry date if TRCN number is provided
        if data.get('trcn_number') and not data.get('trcn_expiry_date'):
            raise serializers.ValidationError({
                'trcn_expiry_date': 'TRCN expiry date is required when TRCN number is provided'
            })
        
        # Validate bank details if any bank field is provided
        bank_fields = ['bank_name', 'account_name', 'account_number']
        bank_provided = any(data.get(field) for field in bank_fields)
        
        if bank_provided:
            for field in bank_fields:
                if not data.get(field):
                    raise serializers.ValidationError({
                        field: f'All bank details must be provided if any is provided'
                    })
        
        # Validate salary step
        salary_step = data.get('salary_step', 1)
        if salary_step < 1 or salary_step > 20:
            raise serializers.ValidationError({
                'salary_step': 'Salary step must be between 1 and 20'
            })
        
        # Validate year of graduation
        year_of_graduation = data.get('year_of_graduation')
        if year_of_graduation:
            current_year = timezone.now().year
            if year_of_graduation > current_year:
                raise serializers.ValidationError({
                    'year_of_graduation': 'Year of graduation cannot be in the future'
                })
            if year_of_graduation < 1900:
                raise serializers.ValidationError({
                    'year_of_graduation': 'Year of graduation must be after 1900'
                })
        
        return data
    
    def create(self, validated_data):
        """Create staff profile for user"""
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        
        # Ensure user has appropriate staff role
        staff_roles = ['head', 'hm', 'principal', 'vice_principal', 'teacher', 
                     'form_teacher', 'subject_teacher', 'accountant', 'secretary',
                     'librarian', 'laboratory', 'security', 'cleaner']
        
        if user.role not in staff_roles:
            # Determine role based on department
            department = validated_data.get('department', 'none')
            if department == 'academic':
                user.role = 'teacher'
            elif department == 'finance':
                user.role = 'accountant'
            elif department == 'administration':
                user.role = 'secretary'
            else:
                user.role = 'teacher'  # Default role
            
            user.save()
        
        # Create staff profile
        staff = Staff.objects.create(user=user, **validated_data)
        
        # Create default permissions based on role
        self._create_default_permissions(staff)
        
        # Create teacher profile if user is in teaching role
        if user.role in ['teacher', 'form_teacher', 'subject_teacher',
                        'head', 'hm', 'principal', 'vice_principal']:
            TeacherProfile.objects.create(staff=staff)
        
        return staff
    
    def _create_default_permissions(self, staff):
        """Create default permissions for staff"""
        permissions = StaffPermission.objects.create(staff=staff)
        
        # Apply role-based default permissions
        try:
            default_permissions = permissions.get_role_based_permissions()
            permissions.update_permissions(default_permissions)
        except Exception:
            pass


# =====================
# STAFF LIST SERIALIZER
# =====================

class StaffListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for staff lists"""
    
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone_number', read_only=True)
    registration_number = serializers.CharField(source='user.registration_number', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    role_display = serializers.CharField(source='user.get_role_display', read_only=True)
    
    employment_type_display = serializers.CharField(
        source='get_employment_type_display',
        read_only=True
    )
    department_display = serializers.CharField(
        source='get_department_display',
        read_only=True
    )
    staff_type = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Staff
        fields = [
            'id', 'full_name', 'email', 'phone', 'registration_number',
            'staff_id', 'role', 'role_display',
            'employment_type', 'employment_type_display',
            'department', 'department_display', 'position_title',
            'staff_type', 'is_active', 'is_on_leave',
            'employment_date', 'created_at'
        ]
    
    def get_staff_type(self, obj):
        try:
            return obj.get_staff_type()
        except Exception:
            return 'unknown'


# =====================
# STAFF DETAIL SERIALIZER
# =====================

class StaffDetailSerializer(StaffSerializer):
    students_count = serializers.SerializerMethodField()
    classes_count = serializers.SerializerMethodField()
    
    class Meta(StaffSerializer.Meta):
        fields = '__all__'  # Or explicitly list all fields you want
    
    def get_students_count(self, obj):
        """Get count of students this staff member teaches"""
        if hasattr(obj, 'teacher_profile'):
            return obj.teacher_profile.get_students().count()
        return 0
    
    def get_classes_count(self, obj):
        """Get count of classes this staff member teaches"""
        if hasattr(obj, 'teacher_profile'):
            return obj.teacher_profile.assigned_classes.count()
        return 0


# =====================
# STAFF DASHBOARD SERIALIZER
# =====================

class StaffDashboardSerializer(serializers.Serializer):
    """Serializer for staff dashboard data"""
    
    staff = StaffSerializer(read_only=True)
    quick_stats = serializers.DictField(read_only=True)
    recent_activities = serializers.ListField(read_only=True)
    upcoming_events = serializers.ListField(read_only=True)
    pending_tasks = serializers.ListField(read_only=True)


# =====================
# TEACHER PROFILE CREATE/UPDATE SERIALIZER
# =====================

class TeacherProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating teacher profiles"""
    
    staff_id = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = TeacherProfile
        fields = [
            'staff_id',
            'teacher_type',
            'subjects',
            # 'primary_subject',  # Keep commented if field doesn't exist
            'stream_specialization',
            'class_levels',
            'assigned_classes',
            'assistant_classes',
            'hod_subjects',
            'max_periods_per_week',
            'current_periods_per_week',  # Add this field from React component
            'preferred_periods',  # CHANGE THIS - from 'preferred_periods_per_week' to 'preferred_periods'
            'years_of_teaching_experience',
            'previous_schools',
            'workshops_attended',
            'training_certificates',
            'conferences_attended',
            'research_publications',
            'has_teaching_materials',
            'teaching_materials_description',
            'additional_responsibilities'
        ]
    
    def validate_staff_id(self, value):
        """Validate staff exists and is not already a teacher"""
        try:
            staff = Staff.objects.get(staff_id=value)
        except Staff.DoesNotExist:
            raise serializers.ValidationError("Staff not found")
        
        # Check if staff already has a teacher profile
        if hasattr(staff, 'teacher_profile'):
            raise serializers.ValidationError("Staff already has a teacher profile")
        
        # Check if staff user has appropriate role
        if staff.user.role not in ['teacher', 'form_teacher', 'subject_teacher',
                                  'head', 'hm', 'principal', 'vice_principal']:
            raise serializers.ValidationError(
                "Staff user must have a teaching role to create teacher profile"
            )
        
        return value
    
    def validate_max_periods_per_week(self, value):
        """Validate maximum periods per week"""
        if value < 0 or value > 60:
            raise serializers.ValidationError(
                "Maximum periods per week must be between 0 and 60"
            )
        return value
    
    def validate_preferred_periods(self, value):  # CHANGE METHOD NAME TOO
        """Validate preferred periods"""
        max_periods = self.initial_data.get('max_periods_per_week', 40)
        if value > max_periods:
            raise serializers.ValidationError(
                "Preferred periods cannot exceed maximum periods per week"
            )
        return value
    
    def create(self, validated_data):
        """Create teacher profile"""
        staff_id = validated_data.pop('staff_id')
        staff = Staff.objects.get(staff_id=staff_id)
        
        # Update staff user role if needed
        if staff.user.role not in ['teacher', 'form_teacher', 'subject_teacher',
                                  'head', 'hm', 'principal', 'vice_principal']:
            staff.user.role = 'teacher'
            staff.user.save()
        
        # Create teacher profile
        teacher_profile = TeacherProfile.objects.create(
            staff=staff,
            **validated_data
        )
        
        return teacher_profile

# =====================
# STAFF UPDATE SERIALIZER
# =====================

class StaffUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating staff profiles (with restrictions)"""
    
    class Meta:
        model = Staff
        fields = [
            'position_title',
            'highest_qualification',
            'qualification_institution',
            'year_of_graduation',
            'professional_certifications',
            'trcn_number',
            'trcn_expiry_date',
            'specialization',
            'bank_name',
            'account_name',
            'account_number',
            'next_of_kin_name',
            'next_of_kin_relationship',
            'next_of_kin_phone',
            'next_of_kin_address',
            'blood_group',
            'genotype',
            'medical_conditions',
            'allergies',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'years_of_experience',
            'previous_employers',
            'references',
            'resume',
            'certificates',
            'id_copy',
            'passport_photo'
        ]
    
    def validate(self, data):
        """Validate update data"""
        request = self.context.get('request')
        
        if request and request.user.role == 'parent':
            raise serializers.ValidationError(
                "Parents cannot update staff profiles"
            )
        
        return data


# =====================
# STAFF PERMISSION UPDATE SERIALIZER
# =====================

class StaffPermissionUpdateSerializer(serializers.Serializer):
    """Serializer for updating staff permissions"""
    
    permissions = serializers.DictField(
        required=True,
        help_text="Dictionary of permission names and boolean values"
    )
    
    def validate_permissions(self, value):
        """Validate permissions dictionary"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Permissions must be a dictionary")
        
        # Get all valid permission field names
        valid_fields = [
            field.name for field in StaffPermission._meta.get_fields()
            if isinstance(field, models.BooleanField) and 
            field.name not in ['id', 'staff', 'created_at', 'updated_at']
        ]
        
        # Check if all provided permissions are valid
        for permission_name in value.keys():
            if permission_name not in valid_fields:
                raise serializers.ValidationError(
                    f"Invalid permission name: {permission_name}"
                )
        
        return value


# =====================
# STAFF ACTIVATION/DEACTIVATION SERIALIZER
# =====================

class StaffActivationSerializer(serializers.Serializer):
    """Serializer for activating/deactivating staff"""
    
    is_active = serializers.BooleanField(required=True)
    activation_date = serializers.DateField(
        required=False,
        default=timezone.now().date
    )
    reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Reason for activation/deactivation"
    )


# =====================
# STAFF RETIREMENT SERIALIZER
# =====================

class StaffRetirementSerializer(serializers.Serializer):
    """Serializer for retiring staff"""
    
    retirement_date = serializers.DateField(
        required=True,
        help_text="Date of retirement"
    )
    retirement_reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Reason for retirement"
    )
    retirement_package = serializers.DecimalField(
        required=False,
        max_digits=12,
        decimal_places=2,
        help_text="Retirement package amount"
    )
    remarks = serializers.CharField(
        required=False,
        max_length=1000,
        help_text="Additional remarks"
    )


# =====================
# STAFF SALARY UPDATE SERIALIZER
# =====================

class StaffSalaryUpdateSerializer(serializers.Serializer):
    """Serializer for updating staff salary"""
    
    basic_salary = serializers.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        min_value=0.00,
        help_text="New basic salary"
    )
    
    salary_scale = serializers.CharField(
        required=False,
        max_length=50,
        help_text="Salary scale/grade level"
    )
    
    salary_step = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=20,
        help_text="Step within salary scale"
    )
    
    effective_date = serializers.DateField(
        required=False,
        default=timezone.now().date,
        help_text="Date when salary change takes effect"
    )
    
    reason = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Reason for salary change"
    )


# =====================
# STAFF SEARCH SERIALIZER
# =====================

class StaffSearchSerializer(serializers.Serializer):
    """Serializer for staff search parameters"""
    
    name = serializers.CharField(required=False, max_length=100)
    staff_id = serializers.CharField(required=False, max_length=20)
    registration_number = serializers.CharField(required=False, max_length=20)
    department = serializers.CharField(required=False, max_length=50)
    employment_type = serializers.CharField(required=False, max_length=20)
    role = serializers.CharField(required=False, max_length=20)
    is_active = serializers.BooleanField(required=False)
    is_on_leave = serializers.BooleanField(required=False)
    
    def validate(self, data):
        """Validate search parameters"""
        # Ensure at least one search parameter is provided
        if not any(data.values()):
            raise serializers.ValidationError(
                "At least one search parameter is required"
            )
        return data


class StaffFullUpdateSerializer(serializers.ModelSerializer):
    """Serializer for comprehensive staff updates"""
    
    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'staff_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate all fields for update"""
        # Add validation for all fields
        return data

class StaffPasswordUpdateSerializer(serializers.Serializer):
    """Serializer for updating staff password"""
    
    new_password = serializers.CharField(
        write_only=True, 
        required=True,
        min_length=8,
        help_text="New password (minimum 8 characters)"
    )
    
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Confirm new password"
    )
    
    def validate(self, data):
        """Validate password fields"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })
        
        if len(data['new_password']) < 8:
            raise serializers.ValidationError({
                'new_password': 'Password must be at least 8 characters'
            })
        
        return data
# =====================
# BULK STAFF CREATE SERIALIZER
# =====================

class BulkStaffCreateSerializer(serializers.Serializer):
    """Serializer for bulk staff creation"""
    
    staff_list = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text="List of staff objects to create"
    )
    
    def validate_staff_list(self, value):
        """Validate staff list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Staff list must be a list")
        
        if len(value) == 0:
            raise serializers.ValidationError("Staff list cannot be empty")
        
        if len(value) > 50:
            raise serializers.ValidationError(
                "Cannot create more than 50 staff at once"
            )
        
        # Validate each staff object
        for i, staff_data in enumerate(value):
            if not isinstance(staff_data, dict):
                raise serializers.ValidationError(
                    f"Staff at index {i} must be a dictionary"
                )
            
            # Check required fields
            required_fields = ['user', 'department']
            for field in required_fields:
                if field not in staff_data:
                    raise serializers.ValidationError(
                        f"Staff at index {i} missing required field: {field}"
                    )
            
            # Validate user data
            user_data = staff_data.get('user', {})
            if not isinstance(user_data, dict):
                raise serializers.ValidationError(
                    f"Staff at index {i} user data must be a dictionary"
                )
            
            user_required = ['first_name', 'last_name', 'email']
            for field in user_required:
                if field not in user_data:
                    raise serializers.ValidationError(
                        f"Staff at index {i} user data missing required field: {field}"
                    )
        
        return value

