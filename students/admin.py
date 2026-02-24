"""
Admin configuration for Student models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Student, StudentEnrollment


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model"""
    
    list_display = [
        'admission_number', 'get_full_name', 'class_level', 'stream', 
        'fee_status', 'balance_due', 'is_active', 'is_graduated'
    ]
    
    list_filter = [
        'class_level', 'stream', 'fee_status', 'student_category',
        'is_active', 'is_graduated', 'house', 'created_at'
    ]
    
    search_fields = [
        'admission_number', 'student_id',
        'user__first_name', 'user__last_name', 'user__registration_number',
        'user__email', 'user__phone_number'
    ]
    
    readonly_fields = [
        'admission_number', 'student_id', 'age_at_admission',
        'balance_due', 'created_at', 'updated_at',
        'birth_certificate_uploaded', 'student_image_uploaded',
        'immunization_record_uploaded', 'previous_school_report_uploaded',
        'parent_id_copy_uploaded'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user', 'admission_number', 'student_id',
                'class_level', 'stream', 'student_category'
            )
        }),
        ('Admission Details', {
            'fields': (
                'admission_date', 'age_at_admission',
                'place_of_birth', 'home_language',
                'previous_school', 'previous_class', 'transfer_certificate_no'
            )
        }),
        ('Family Information', {
            'fields': (
                'father', 'mother',
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship'
            )
        }),
        ('Fee Information', {
            'fields': (
                'total_fee_amount', 'amount_paid', 'balance_due',
                'fee_status', 'fee_payment_evidence', 'last_payment_date'
            )
        }),
        ('Health Information', {
            'fields': (
                'blood_group', 'genotype',
                'has_allergies', 'allergy_details',
                'has_received_vaccinations', 'family_doctor_name',
                'family_doctor_phone', 'medical_conditions',
                'has_learning_difficulties', 'learning_difficulties_details'
            )
        }),
        ('Documents', {
            'fields': (
                'birth_certificate', 'student_image',
                'immunization_record', 'previous_school_report',
                'parent_id_copy'
            )
        }),
        ('Additional Information', {
            'fields': (
                'house', 'is_prefect', 'prefect_role',
                'transportation_mode', 'bus_route'
            )
        }),
        ('Status & Tracking', {
            'fields': (
                'is_active', 'is_graduated', 'graduation_date',
                'days_present', 'days_absent', 'days_late',
                'created_at', 'updated_at'
            )
        }),
    )
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'class_level', 'father', 'mother'
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-calculate balance on save"""
        obj.balance_due = obj.total_fee_amount - obj.amount_paid
        super().save_model(request, obj, form, change)


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    """Admin interface for StudentEnrollment model"""
    
    list_display = [
        'enrollment_number', 'student_name', 'class_obj', 
        'session', 'term', 'status', 'enrollment_date'
    ]
    
    list_filter = [
        'session', 'term', 'class_obj', 'status',
        'is_repeating', 'is_promoted', 'enrollment_date'
    ]
    
    search_fields = [
        'enrollment_number', 'student__user__first_name',
        'student__user__last_name', 'student__admission_number',
        'class_obj__name', 'session__name', 'term__name'
    ]
    
    readonly_fields = [
        'enrollment_number', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': (
                'student', 'class_obj', 'session', 'term',
                'enrollment_number', 'enrollment_date'
            )
        }),
        ('Enrollment Status', {
            'fields': (
                'status', 'is_repeating', 'is_promoted', 'promotion_date',
                'days_present', 'days_absent', 'remarks'
            )
        }),
        ('Approval Information', {
            'fields': (
                'enrolled_by', 'approved_by', 'approved_date'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def student_name(self, obj):
        return obj.student.user.get_full_name()
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'student__user__first_name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'student__user', 'class_obj', 'session', 'term',
            'enrolled_by', 'approved_by'
    )