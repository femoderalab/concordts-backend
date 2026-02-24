"""
Serializers for the Student model and related operations.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Student, StudentEnrollment
from users.serializers import UserProfileSerializer
from users.models import User
from academic.models import ClassLevel
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
import os
import logging
from django.db import transaction, IntegrityError
import random
import string
from parents.models import Parent
from results.serializers import StudentResultListSerializer  # import from results app
from decimal import Decimal 

logger = logging.getLogger(__name__)



class StudentFeeUpdateSerializer(serializers.Serializer):
    """Serializer for updating student fees"""

    amount_paid = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=Decimal('0.01'),  # FIXED: Use Decimal instead of 0.01
        help_text="Amount paid by student"
    )
    payment_date = serializers.DateField(
        required=False,
        default=timezone.now().date,
        help_text="Date of payment"
    )
    fee_payment_evidence = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text="Receipt or evidence of payment"
    )
    payment_method = serializers.CharField(
        required=False,
        max_length=50,
        help_text="Payment method (cash, bank transfer, etc.)"
    )
    transaction_reference = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Transaction reference number"
    )

    def validate_amount_paid(self, value):
        """Validate amount paid"""
        if value <= Decimal('0'):  # FIXED: Use Decimal for comparison
            raise serializers.ValidationError("Amount paid must be greater than 0")
        return value

# =====================
# PARENT MINI SERIALIZER
# =====================
class ParentMiniSerializer(serializers.Serializer):
    """Lightweight parent serializer"""
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    parent_id = serializers.CharField(read_only=True)
    parent_type = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)




class StudentSerializer(serializers.ModelSerializer):
    """Main serializer for Student model - UPDATED WITH USER FIELDS"""
    
    # User info - MAKE SURE THESE ARE INCLUDED
    user = UserProfileSerializer(read_only=True)
    
    # User fields for response
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    user_gender = serializers.CharField(source='user.gender', read_only=True)
    
    # File URLs
    student_image_url = serializers.SerializerMethodField()
    birth_certificate_url = serializers.SerializerMethodField()
    immunization_record_url = serializers.SerializerMethodField()
    previous_school_report_url = serializers.SerializerMethodField()
    parent_id_copy_url = serializers.SerializerMethodField()
    fee_payment_evidence_url = serializers.SerializerMethodField()
    
    # Other fields
    class_level_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = '__all__'
        # Add URL fields and user fields to read_only_fields
        read_only_fields = [
            'id', 'user', 'admission_number', 'student_id', 'balance_due',
            'days_present', 'days_absent', 'days_late', 'created_at', 'updated_at',
            'student_image_url', 'birth_certificate_url', 'immunization_record_url',
            'previous_school_report_url', 'parent_id_copy_url', 'fee_payment_evidence_url',
            'class_level_info', 'user_first_name', 'user_last_name', 'user_email',
            'user_phone', 'user_gender'
        ]
    
    def get_student_image_url(self, obj):
        """Get absolute URL for student image"""
        if obj.student_image and hasattr(obj.student_image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.student_image.url)
            return obj.student_image.url
        return None
    
    def get_birth_certificate_url(self, obj):
        if obj.birth_certificate and hasattr(obj.birth_certificate, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.birth_certificate.url)
            return obj.birth_certificate.url
        return None
    
    def get_immunization_record_url(self, obj):
        if obj.immunization_record and hasattr(obj.immunization_record, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.immunization_record.url)
            return obj.immunization_record.url
        return None
    
    def get_previous_school_report_url(self, obj):
        if obj.previous_school_report and hasattr(obj.previous_school_report, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.previous_school_report.url)
            return obj.previous_school_report.url
        return None
    
    def get_parent_id_copy_url(self, obj):
        if obj.parent_id_copy and hasattr(obj.parent_id_copy, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.parent_id_copy.url)
            return obj.parent_id_copy.url
        return None
    
    def get_fee_payment_evidence_url(self, obj):
        if obj.fee_payment_evidence and hasattr(obj.fee_payment_evidence, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.fee_payment_evidence.url)
            return obj.fee_payment_evidence.url
        return None
    
    def get_class_level_info(self, obj):
        if obj.class_level:
            return {
                'id': obj.class_level.id,
                'name': obj.class_level.name,
                'code': obj.class_level.code,
                'level': obj.class_level.level,
            }
        return None

# =====================
# STUDENT CREATE SERIALIZER
# =====================
class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating students"""

    user_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Student
        fields = [
            'user_id', 'class_level', 'stream', 'admission_date',
            'house', 'student_category', 'father', 'mother',
            'place_of_birth', 'home_language',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'total_fee_amount',
            'transportation_mode', 'bus_route', 'blood_group',
            'genotype', 'has_allergies', 'allergy_details',
            'has_received_vaccinations', 'family_doctor_name',
            'family_doctor_phone', 'medical_conditions',
            'has_learning_difficulties', 'learning_difficulties_details',
            'previous_school', 'previous_class'
        ]

    def validate_user_id(self, value):
        """Validate user exists and is not already a student"""
        from users.models import User

        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        # Check if user is already a student
        if hasattr(user, 'student_profile'):
            raise serializers.ValidationError("User is already a student")

        return value

    def validate(self, data):
        """Validate student data"""
        # Validate father and mother are parent users
        father = data.get('father')
        mother = data.get('mother')

        if father and father.user.role != 'parent':
            raise serializers.ValidationError({
                'father': 'Father must be a parent user'
            })

        if mother and mother.user.role != 'parent':
            raise serializers.ValidationError({
                'mother': 'Mother must be a parent user'
            })

        # Validate total fee amount
        total_fee = data.get('total_fee_amount', 0)
        if total_fee < 0:
            raise serializers.ValidationError({
                'total_fee_amount': 'Total fee amount cannot be negative'
            })

        # Validate allergy details if has_allergies is True
        if data.get('has_allergies') and not data.get('allergy_details'):
            raise serializers.ValidationError({
                'allergy_details': 'Please specify allergy details when allergies are present'
            })

        # Validate learning difficulties details
        if data.get('has_learning_difficulties') and not data.get('learning_difficulties_details'):
            raise serializers.ValidationError({
                'learning_difficulties_details': 'Please elaborate on learning difficulties'
            })

        return data

    def create(self, validated_data):
        """Create student profile for user"""
        from users.models import User

        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)

        # Ensure user has student role
        if user.role != 'student':
            user.role = 'student'
            user.save()

        # Create student profile
        student = Student.objects.create(user=user, **validated_data)
        return student



class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for student lists - FIXED"""

    # User fields - MAKE SURE THESE ARE CORRECTLY MAPPED
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    registration_number = serializers.CharField(source='user.registration_number', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone_number', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)
    
    # Academic fields
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    stream_display = serializers.CharField(source='get_stream_display', read_only=True)
    fee_status_display = serializers.CharField(source='get_fee_status_display', read_only=True)
    
    # File URLs
    student_image_url = serializers.SerializerMethodField()
    class_level_info = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            # Student fields
            'id', 'admission_number', 'student_id', 
            'class_level', 'class_level_name', 'class_level_info',
            'stream', 'stream_display', 'house', 'student_category',
            'fee_status', 'fee_status_display', 'balance_due',
            'is_active', 'is_graduated', 'admission_date', 'created_at',
            
            # User fields - THESE ARE CRITICAL
            'first_name', 'last_name', 'full_name', 
            'registration_number', 'email', 'phone', 'gender',
            
            # File URLs
            'student_image_url'
        ]
        
    def get_student_image_url(self, obj):
        """Get absolute URL for student image"""
        if obj.student_image and hasattr(obj.student_image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.student_image.url)
            return obj.student_image.url
        return None
    
    def get_class_level_info(self, obj):
        if obj.class_level:
            return {
                'id': obj.class_level.id,
                'name': obj.class_level.name,
                'code': obj.class_level.code,
                'level': obj.class_level.level,
            }
        return None


# =====================
# STUDENT DETAIL SERIALIZER
# =====================
class StudentDetailSerializer(StudentSerializer):
    """Detailed serializer for student view"""

    parents = serializers.SerializerMethodField()
    enrollments = serializers.SerializerMethodField()

    class Meta(StudentSerializer.Meta):
        model = Student
        fields = '__all__'

    def get_parents(self, obj):
        """Get both parents if available"""
        parents = []
        if obj.father:
            parents.append(ParentMiniSerializer(obj.father).data)
        if obj.mother:
            parents.append(ParentMiniSerializer(obj.mother).data)
        return parents

    def get_enrollments(self, obj):
        """Get student enrollments"""
        enrollments = obj.enrollments.all().order_by('-enrollment_date')[:5]
        return StudentEnrollmentSerializer(enrollments, many=True).data


# =====================
# STUDENT DASHBOARD SERIALIZER
# =====================
class StudentDashboardSerializer(serializers.Serializer):
    """Serializer for student dashboard data"""

    student = StudentSerializer(read_only=True)
    attendance_summary = serializers.SerializerMethodField(read_only=True)
    fee_information = serializers.SerializerMethodField(read_only=True)
    recent_activities = serializers.SerializerMethodField(read_only=True)
    document_status = serializers.SerializerMethodField(read_only=True)

    def get_attendance_summary(self, obj):
        """Get attendance summary"""
        total_days = obj.days_present + obj.days_absent
        attendance_rate = (obj.days_present / total_days * 100) if total_days > 0 else 0

        return {
            'days_present': obj.days_present,
            'days_absent': obj.days_absent,
            'days_late': obj.days_late,
            'total_days': total_days,
            'attendance_rate': round(attendance_rate, 2),
            'attendance_status': 'Good' if attendance_rate >= 80 else 'Needs Improvement'
        }

    def get_fee_information(self, obj):
        """Get fee information"""
        fee_summary = obj.get_fee_summary()

        return {
            **fee_summary,
            'last_payment_date': obj.last_payment_date,
            'payment_evidence_available': bool(obj.fee_payment_evidence)
        }

    def get_document_status(self, obj):
        """Get document upload status"""
        checklist = obj.get_document_checklist_summary()
        uploaded_count = sum([
            checklist['birth_certificate'],
            checklist['student_image'],
            checklist['immunization_record'],
            checklist['previous_school_report'],
            checklist['parent_id_copy']
        ])
        
        return {
            'uploaded': uploaded_count,
            'total': 5,
            'completion_percentage': (uploaded_count / 5) * 100,
            'all_uploaded': checklist['all_documents_uploaded']
        }

    def get_recent_activities(self, obj):
        """Get recent activities"""
        activities = []
        
        if obj.last_payment_date:
            activities.append({
                'date': obj.last_payment_date,
                'activity': 'Fee payment',
                'details': f'Balance: ₦{obj.balance_due:,.2f}'
            })
        
        # Add admission date activity
        if obj.admission_date:
            activities.append({
                'date': obj.admission_date,
                'activity': 'Admission',
                'details': f'Admitted with number: {obj.admission_number}'
            })
        
        return activities


# =====================
# STUDENT ENROLLMENT SERIALIZER
# =====================
class StudentEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for StudentEnrollment model"""

    student_info = serializers.SerializerMethodField(read_only=True)
    class_info = serializers.SerializerMethodField(read_only=True)
    session_info = serializers.SerializerMethodField(read_only=True)
    term_info = serializers.SerializerMethodField(read_only=True)
    enrolled_by_info = serializers.SerializerMethodField(read_only=True)
    approved_by_info = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = StudentEnrollment
        fields = '__all__'
        read_only_fields = [
            'id', 'enrollment_number', 'created_at', 'updated_at',
            'status_display', 'student_info', 'class_info', 'session_info',
            'term_info', 'enrolled_by_info', 'approved_by_info'
        ]

    def get_student_info(self, obj):
        return {
            'id': obj.student.id,
            'name': obj.student.user.get_full_name(),
            'admission_number': obj.student.admission_number,
            'registration_number': obj.student.user.registration_number,
        }

    def get_class_info(self, obj):
        if obj.class_obj:
            return {
                'id': obj.class_obj.id,
                'name': obj.class_obj.name,
                'code': obj.class_obj.code,
            }
        return None

    def get_session_info(self, obj):
        return {
            'id': obj.session.id,
            'name': obj.session.name,
            'start_date': obj.session.start_date,
            'end_date': obj.session.end_date,
        }

    def get_term_info(self, obj):
        return {
            'id': obj.term.id,
            'name': obj.term.name,
            'term': obj.term.term,
            'start_date': obj.term.start_date,
            'end_date': obj.term.end_date,
        }

    def get_enrolled_by_info(self, obj):
        if obj.enrolled_by:
            return {
                'id': obj.enrolled_by.id,
                'name': obj.enrolled_by.get_full_name(),
                'registration_number': obj.enrolled_by.registration_number,
            }
        return None

    def get_approved_by_info(self, obj):
        if obj.approved_by:
            return {
                'id': obj.approved_by.id,
                'name': obj.approved_by.get_full_name(),
                'registration_number': obj.approved_by.registration_number,
            }
        return None

    def validate(self, data):
        """Validate enrollment data"""
        student = data.get('student')
        class_obj = data.get('class_obj')
        session = data.get('session')
        term = data.get('term')

        # Check if student is already enrolled in this session/term/class
        if student and class_obj and session and term:
            existing = StudentEnrollment.objects.filter(
                student=student,
                class_obj=class_obj,
                session=session,
                term=term
            )
            
            # Exclude current instance if updating
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError(
                    "Student is already enrolled in this class for the specified session/term"
                )

        return data


# =====================
# STUDENT FEE UPDATE SERIALIZER
# =====================
# class StudentFeeUpdateSerializer(serializers.Serializer):
#     """Serializer for updating student fees"""

#     amount_paid = serializers.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         required=True,
#         min_value=0.01,
#         help_text="Amount paid by student"
#     )
#     payment_date = serializers.DateField(
#         required=False,
#         default=timezone.now().date,
#         help_text="Date of payment"
#     )
#     fee_payment_evidence = serializers.ImageField(
#         required=False,
#         allow_null=True,
#         help_text="Receipt or evidence of payment"
#     )
#     payment_method = serializers.CharField(
#         required=False,
#         max_length=50,
#         help_text="Payment method (cash, bank transfer, etc.)"
#     )
#     transaction_reference = serializers.CharField(
#         required=False,
#         max_length=100,
#         help_text="Transaction reference number"
#     )

#     def validate_amount_paid(self, value):
#         """Validate amount paid"""
#         if value <= 0:
#             raise serializers.ValidationError("Amount paid must be greater than 0")
#         return value


# =====================
# STUDENT PROMOTION SERIALIZER
# =====================
class StudentPromotionSerializer(serializers.Serializer):
    """Serializer for promoting students"""

    new_class_level_id = serializers.IntegerField(
        required=True,
        help_text="ID of the new class level"
    )
    promotion_date = serializers.DateField(
        required=False,
        default=timezone.now().date,
        help_text="Date of promotion"
    )
    remarks = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Promotion remarks"
    )

    def validate_new_class_level_id(self, value):
        """Validate new class level exists"""
        from academic.models import ClassLevel
        try:
            ClassLevel.objects.get(id=value)
        except ClassLevel.DoesNotExist:
            raise serializers.ValidationError("Class level does not exist")
        return value


# =====================
# STUDENT ATTENDANCE UPDATE SERIALIZER
# =====================
class StudentAttendanceUpdateSerializer(serializers.Serializer):
    """Serializer for updating student attendance"""

    date = serializers.DateField(
        required=True,
        help_text="Attendance date"
    )
    status = serializers.ChoiceField(
        choices=['present', 'absent', 'late', 'half_day', 'excused'],
        required=True,
        help_text="Attendance status"
    )
    remarks = serializers.CharField(
        required=False,
        max_length=500,
        help_text="Attendance remarks"
    )
    check_in_time = serializers.TimeField(
        required=False,
        help_text="Check-in time (for late arrivals)"
    )
    check_out_time = serializers.TimeField(
        required=False,
        help_text="Check-out time (for early departures)"
    )

    def validate_date(self, value):
        """Validate date is not in the future"""
        if value > timezone.now().date():
            raise serializers.ValidationError("Attendance date cannot be in the future")
        return value


# =====================
# DOCUMENT UPLOAD SERIALIZER
# =====================
class StudentDocumentUploadSerializer(serializers.Serializer):
    """Serializer for uploading student documents"""

    document_type = serializers.ChoiceField(
        choices=[
            'birth_certificate',
            'student_image',
            'immunization_record',
            'previous_school_report',
            'parent_id_copy'
        ],
        required=True,
        help_text="Type of document to upload"
    )
    document = serializers.FileField(
        required=True,
        help_text="Document file to upload"
    )

    def validate_document(self, value):
        """Validate document file"""
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Document size must not exceed 5MB")
        
        return value


# =====================
# DECLARATION SERIALIZER
# =====================
class ParentDeclarationSerializer(serializers.Serializer):
    """Serializer for parent declaration during student registration"""

    declaration_accepted = serializers.BooleanField(
        required=True,
        help_text="I hereby declare that the information provided is true and correct"
    )
    parent_signature = serializers.CharField(
        required=False,
        max_length=200,
        help_text="Digital signature (parent name)"
    )
    declaration_date = serializers.DateField(
        required=False,
        default=timezone.now().date,
        help_text="Date of declaration"
    )

    def validate_declaration_accepted(self, value):
        """Validate declaration is accepted"""
        if not value:
            raise serializers.ValidationError(
                "You must accept the declaration to proceed"
            )
        return value


class SimpleStudentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating student profile"""
    
    user_id = serializers.IntegerField(required=True, write_only=True)
    
    class Meta:
        model = Student
        fields = [
            'user_id', 'class_level', 'stream', 'admission_date',
            'student_category', 'house', 'admission_number', 'student_id',
            'transportation_mode', 'bus_route', 'fee_status',
            'total_fee_amount', 'amount_paid'
        ]
        read_only_fields = ['balance_due']
    
    def validate_user_id(self, value):
        """Validate user exists and is not already a student"""
        try:
            user = User.objects.get(id=value)
            if user.role != 'student':
                raise serializers.ValidationError("User role must be 'student'")
            if hasattr(user, 'student_profile'):
                raise serializers.ValidationError("User already has a student profile")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
    
    def create(self, validated_data):
        """Create student profile for existing user"""
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        
        # Create student profile
        student = Student.objects.create(user=user, **validated_data)
        return student
    
    
class AdminDirectPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for admin to directly reset any user's password without email verification.
    """
    registration_number = serializers.CharField(
        required=True,
        help_text="User's registration number"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Enter new password (min 8 characters)"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm new password"
    )

    def validate(self, attrs):
        """
        Validate admin reset password data.
        """
        registration_number = attrs.get('registration_number')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        # Check passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"new_password": "Passwords don't match"}
            )

        # Check registration number exists
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"registration_number": "No user found with this registration number"}
            )

        attrs['user'] = user
        return attrs
    
# In serializers.py - Add these imports at the top if missing

class StudentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating students - ALL FIELDS OPTIONAL
    This prevents validation errors for nullable ForeignKeys
    """
    
    # Make parent fields explicitly optional
    father = serializers.PrimaryKeyRelatedField(
        queryset=Parent.objects.all(),
        required=False,
        allow_null=True
    )
    
    mother = serializers.PrimaryKeyRelatedField(
        queryset=Parent.objects.all(),
        required=False,
        allow_null=True
    )
    
    # Make class_level optional too
    class_level = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        required=False,
        allow_null=True
    )
    
    # User fields
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state_of_origin = serializers.CharField(required=False, allow_blank=True)
    lga = serializers.CharField(required=False, allow_blank=True)
    nationality = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Student
        fields = '__all__'
        # Make ALL fields optional during updates
        extra_kwargs = {
            'father': {'required': False, 'allow_null': True},
            'mother': {'required': False, 'allow_null': True},
            'class_level': {'required': False, 'allow_null': True},
            'stream': {'required': False},
            'admission_date': {'required': False},
            'student_category': {'required': False},
            'house': {'required': False},
            'place_of_birth': {'required': False, 'allow_blank': True},
            'home_language': {'required': False, 'allow_blank': True},
            'previous_class': {'required': False, 'allow_blank': True},
            'previous_school': {'required': False, 'allow_blank': True},
            'transfer_certificate_no': {'required': False, 'allow_blank': True},
            'is_prefect': {'required': False},
            'prefect_role': {'required': False, 'allow_blank': True},
            'emergency_contact_name': {'required': False, 'allow_blank': True},
            'emergency_contact_phone': {'required': False, 'allow_blank': True},
            'emergency_contact_relationship': {'required': False, 'allow_blank': True},
            'fee_status': {'required': False},
            'total_fee_amount': {'required': False},
            'amount_paid': {'required': False},
            'blood_group': {'required': False, 'allow_blank': True},
            'genotype': {'required': False, 'allow_blank': True},
            'has_allergies': {'required': False},
            'allergy_details': {'required': False, 'allow_blank': True},
            'has_received_vaccinations': {'required': False},
            'family_doctor_name': {'required': False, 'allow_blank': True},
            'family_doctor_phone': {'required': False, 'allow_blank': True},
            'medical_conditions': {'required': False, 'allow_blank': True},
            'has_learning_difficulties': {'required': False},
            'learning_difficulties_details': {'required': False, 'allow_blank': True},
            'transportation_mode': {'required': False},
            'bus_route': {'required': False, 'allow_blank': True},
            'is_active': {'required': False},
            'is_graduated': {'required': False},
            'graduation_date': {'required': False, 'allow_null': True},
        }



class StudentDashboardCombinedSerializer(serializers.Serializer):
    student = StudentDetailSerializer()
    results = StudentResultListSerializer(many=True)
    statistics = serializers.DictField()

    class Meta:
        fields = ['student', 'results', 'statistics']


# =====================
# UPDATED STUDENT CREATE WITH USER SERIALIZER
# =====================
class StudentCreateWithUserSerializer(serializers.ModelSerializer):
    """Complete serializer for creating student with user - FIXED VERSION"""
    
    # User fields
    first_name = serializers.CharField(max_length=100, required=True, write_only=True)
    last_name = serializers.CharField(max_length=100, required=True, write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True, write_only=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(max_length=128, required=False, default='Student@2024', write_only=True)
    gender = serializers.ChoiceField(choices=User.GENDER_CHOICES, default='male', required=False, write_only=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True, write_only=True)
    address = serializers.CharField(required=False, allow_blank=True, write_only=True)
    city = serializers.CharField(required=False, allow_blank=True, write_only=True)
    state_of_origin = serializers.ChoiceField(choices=User.NIGERIAN_STATES, required=False, write_only=True)
    lga = serializers.CharField(required=False, allow_blank=True, write_only=True)
    nationality = serializers.CharField(default='Nigerian', required=False, write_only=True)
    
    # Student fields
    class_level = serializers.PrimaryKeyRelatedField(queryset=ClassLevel.objects.all(), required=True)
    
    # All other student fields...
    # (Keep all your existing field definitions here)
    
    # FILE FIELDS - Make them write_only for creation
    birth_certificate = serializers.FileField(required=False, allow_null=True, write_only=True)
    student_image = serializers.ImageField(required=False, allow_null=True, write_only=True)
    immunization_record = serializers.FileField(required=False, allow_null=True, write_only=True)
    previous_school_report = serializers.FileField(required=False, allow_null=True, write_only=True)
    parent_id_copy = serializers.FileField(required=False, allow_null=True, write_only=True)
    fee_payment_evidence = serializers.ImageField(required=False, allow_null=True, write_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'  # Or list all fields explicitly
    
    def validate(self, attrs):
        """Enhanced validation"""
        errors = {}
        
        # Required fields
        if not attrs.get('first_name'):
            errors['first_name'] = ['First name is required']
        if not attrs.get('last_name'):
            errors['last_name'] = ['Last name is required']
        if not attrs.get('class_level'):
            errors['class_level'] = ['Class level is required']
        
        # Email uniqueness check
        email = attrs.get('email', '').strip()
        if email:
            if User.objects.filter(email=email).exists():
                errors['email'] = ['A user with this email already exists.']
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Fixed create method - properly handles files"""
        logger.info("Starting comprehensive student creation...")
        
        # =====================
        # EXTRACT DATA
        # =====================
        # Extract user data
        user_fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'password',
            'gender', 'date_of_birth', 'address', 'city', 'state_of_origin',
            'lga', 'nationality'
        ]
        
        user_data = {}
        for field in user_fields:
            if field in validated_data:
                user_data[field] = validated_data.pop(field)
        
        # Extract file data
        file_fields = [
            'birth_certificate', 'student_image', 'immunization_record',
            'previous_school_report', 'parent_id_copy', 'fee_payment_evidence'
        ]
        
        file_data = {}
        for field in file_fields:
            if field in validated_data:
                file_data[field] = validated_data.pop(field)
        
        # =====================
        # CREATE USER
        # =====================
        password = user_data.pop('password', 'Student@2024')
        email = user_data.get('email', '').strip()
        
        if email == '':
            user_data['email'] = None
        
        # Set role
        user_data['role'] = 'student'
        
        try:
            user = User.objects.create_user(
                password=password,
                **user_data
            )
            logger.info(f"✅ User created: {user.registration_number}")
        except Exception as e:
            logger.error(f"❌ User creation failed: {str(e)}")
            raise serializers.ValidationError({'user': f'Failed to create user: {str(e)}'})
        
        # =====================
        # CREATE STUDENT
        # =====================
        try:
            # Generate unique IDs if not provided
            if not validated_data.get('admission_number'):
                validated_data['admission_number'] = self.generate_unique_admission_number()
            
            if not validated_data.get('student_id'):
                validated_data['student_id'] = self.generate_unique_student_id()
            
            # Add user to student data
            validated_data['user'] = user
            
            # Add file data
            for field, file in file_data.items():
                if file:
                    validated_data[field] = file
            
            # Create student
            student = Student.objects.create(**validated_data)
            
            logger.info(f"✅ Student created: {student.admission_number}")
            
            # Return complete data
            return {
                'id': student.id,
                'admission_number': student.admission_number,
                'student_id': student.student_id,
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'registration_number': user.registration_number,
                },
                'files_uploaded': list(file_data.keys()),
                'created_at': student.created_at,
            }
            
        except Exception as e:
            # Rollback user creation if student creation fails
            logger.error(f"❌ Student creation failed, rolling back user: {str(e)}")
            user.delete()
            raise serializers.ValidationError({'student': f'Failed to create student: {str(e)}'})