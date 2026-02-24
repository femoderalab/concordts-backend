# staff/admin.py
"""
Django Admin configuration for Staff models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Staff


class StaffAdmin(admin.ModelAdmin):
    """Admin interface for Staff model"""
    
    list_display = [
        'get_full_name', 'staff_id', 'get_role_display',
        'department_display', 'employment_type_display',
        'position_title', 'is_active', 'is_on_leave',
        'employment_date', 'basic_salary'
    ]
    
    list_filter = [
        'department', 'employment_type', 'is_active',
        'is_on_leave', 'is_on_probation', 'is_retired'
    ]
    
    search_fields = [
        'user__first_name', 'user__last_name',
        'user__email', 'staff_id', 'user__registration_number',
        'position_title', 'trcn_number'
    ]
    
    readonly_fields = [
        'staff_id', 'created_at', 'updated_at',
        'leave_days_remaining'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user', 'staff_id',
                'position_title', 'department', 'employment_type'
            )
        }),
        ('Employment Information', {
            'fields': (
                'employment_date',
                ('basic_salary', 'salary_scale', 'salary_step'),
                ('annual_leave_days', 'sick_leave_days'),
                ('leave_days_taken', 'leave_days_remaining')
            )
        }),
        ('Qualification & Certification', {
            'fields': (
                'highest_qualification', 'qualification_institution',
                'year_of_graduation', 'professional_certifications',
                'trcn_number', 'trcn_expiry_date', 'specialization'
            ),
            'classes': ('collapse',)
        }),
        ('Bank Information', {
            'fields': (
                'bank_name', 'account_name', 'account_number'
            ),
            'classes': ('collapse',)
        }),
        ('Emergency & Contact Information', {
            'fields': (
                'next_of_kin_name', 'next_of_kin_relationship',
                'next_of_kin_phone', 'next_of_kin_address',
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship'
            ),
            'classes': ('collapse',)
        }),
        ('Health Information', {
            'fields': (
                'blood_group', 'genotype',
                'medical_conditions', 'allergies'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Performance', {
            'fields': (
                'is_active', 'is_on_leave', 
                ('leave_start_date', 'leave_end_date'),
                'is_on_probation', 'probation_end_date', 
                'is_retired', 'retirement_date',
                'performance_rating', 'last_appraisal_date',
                'next_appraisal_date', 'appraisal_notes'
            )
        }),
        ('Documents & Additional Information', {
            'fields': (
                'years_of_experience', 'previous_employers',
                'references', 'resume', 'certificates',
                'id_copy', 'passport_photo'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_staff', 'deactivate_staff', 'retire_staff']
    
    def get_full_name(self, obj):
        """Get staff's full name"""
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_role_display(self, obj):
        """Get staff's role"""
        return obj.user.get_role_display()
    get_role_display.short_description = 'Role'
    
    def department_display(self, obj):
        """Display department"""
        return obj.get_department_display()
    department_display.short_description = 'Department'
    
    def employment_type_display(self, obj):
        """Display employment type"""
        return obj.get_employment_type_display()
    employment_type_display.short_description = 'Employment Type'
    
    def activate_staff(self, request, queryset):
        """Activate selected staff"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} staff activated.')
    activate_staff.short_description = 'Activate selected staff'
    
    def deactivate_staff(self, request, queryset):
        """Deactivate selected staff"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} staff deactivated.')
    deactivate_staff.short_description = 'Deactivate selected staff'
    
    def retire_staff(self, request, queryset):
        """Retire selected staff"""
        from django.utils import timezone
        updated = queryset.update(
            is_retired=True,
            is_active=False,
            retirement_date=timezone.now().date()
        )
        self.message_user(request, f'{updated} staff retired.')
    retire_staff.short_description = 'Retire selected staff'


# Register the model
admin.site.register(Staff, StaffAdmin)