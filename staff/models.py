# staff/models.py
"""
Staff models for the School Management System.
"""

from django.db import models
from django.utils import timezone
import random
import string
from users.models import User  # Direct import instead of AUTH_USER_MODEL


class Staff(models.Model):
    """
    Staff Model - Base model for all school staff members
    """
    
    # Core Relationship
    user = models.OneToOneField(
        User,  # Changed from settings.AUTH_USER_MODEL to User
        on_delete=models.CASCADE,
        related_name='staff_profile',
        help_text="Linked user account"
    )
    
    # Staff Identification
    staff_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Unique staff identification number"
    )
    
    # Employment Information
    employment_date = models.DateField(
        default=timezone.now,
        help_text="Date staff was employed"
    )
    
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full-Time'),
        ('part_time', 'Part-Time'),
        ('contract', 'Contract'),
        ('volunteer', 'Volunteer'),
        ('trainee', 'Trainee/Intern'),
        ('probation', 'Probation'),
    ]
    
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        help_text="Type of employment"
    )
    
    # Department & Position
    DEPARTMENT_CHOICES = [
        ('administration', 'Administration'),
        ('academic', 'Academic'),
        ('finance', 'Finance/Bursary'),
        ('library', 'Library'),
        ('laboratory', 'Laboratory'),
        ('ict', 'ICT/Computer'),
        ('security', 'Security'),
        ('maintenance', 'Maintenance'),
        ('transport', 'Transport'),
        ('health', 'Health Clinic'),
        ('counseling', 'Guidance & Counseling'),
        ('sports', 'Sports & Games'),
        ('kitchen', 'Kitchen/Cafeteria'),
        ('none', 'Not Applicable'),
    ]
    
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        default='none',
        help_text="Department/Unit assignment"
    )
    
    position_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title/position"
    )
    
    # Qualification & Certification
    highest_qualification = models.CharField(
        max_length=100,
        blank=True,
        help_text="Highest educational qualification (e.g., B.Sc, M.Ed, PhD)"
    )
    
    qualification_institution = models.CharField(
        max_length=200,
        blank=True,
        help_text="Institution where qualification was obtained"
    )
    
    year_of_graduation = models.IntegerField(
        blank=True,
        null=True,
        help_text="Year of graduation"
    )
    
    professional_certifications = models.TextField(
        blank=True,
        help_text="Professional certifications (TRCN, etc.)"
    )
    
    trcn_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Teachers Registration Council of Nigeria Number"
    )
    
    trcn_expiry_date = models.DateField(
        blank=True,
        null=True,
        help_text="TRCN license expiry date"
    )
    
    specialization = models.TextField(
        blank=True,
        help_text="Areas of specialization/expertise"
    )
    
    # Salary Information (Simplified - employee_number removed)
    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Basic monthly salary"
    )
    
    salary_scale = models.CharField(
        max_length=50,
        blank=True,
        help_text="Salary scale/grade level"
    )
    
    salary_step = models.IntegerField(
        default=1,
        help_text="Step within salary scale"
    )
    
    # Bank Information
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bank name for salary payments"
    )
    
    account_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Account name as registered with bank"
    )
    
    account_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Bank account number"
    )
    
    # Leave Information
    annual_leave_days = models.IntegerField(
        default=21,
        help_text="Annual leave entitlement in days"
    )
    
    sick_leave_days = models.IntegerField(
        default=10,
        help_text="Annual sick leave entitlement in days"
    )
    
    leave_days_taken = models.IntegerField(
        default=0,
        help_text="Leave days already taken"
    )
    
    leave_days_remaining = models.IntegerField(
        default=21,
        help_text="Remaining leave days"
    )
    
    # Next of Kin Information
    next_of_kin_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Next of kin full name"
    )
    
    next_of_kin_relationship = models.CharField(
        max_length=50,
        blank=True,
        help_text="Relationship to staff"
    )
    
    next_of_kin_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Next of kin phone number"
    )
    
    next_of_kin_address = models.TextField(
        blank=True,
        help_text="Next of kin address"
    )
    
    # Health Information
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    GENOTYPE_CHOICES = [
        ('AA', 'AA'), ('AS', 'AS'),
        ('SS', 'SS'), ('AC', 'AC'),
    ]
    
    blood_group = models.CharField(
        max_length=5,
        blank=True,
        choices=BLOOD_GROUP_CHOICES
    )
    
    genotype = models.CharField(
        max_length=3,
        blank=True,
        choices=GENOTYPE_CHOICES
    )
    
    medical_conditions = models.TextField(
        blank=True,
        help_text="Any known medical conditions"
    )
    
    allergies = models.TextField(
        blank=True,
        help_text="Known allergies"
    )
    
    # Emergency Contact
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Emergency contact person"
    )
    
    emergency_contact_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Emergency contact phone number"
    )
    
    emergency_contact_relationship = models.CharField(
        max_length=50,
        blank=True,
        help_text="Relationship to staff"
    )
    
    # Status Flags
    is_active = models.BooleanField(
        default=True,
        help_text="Is staff currently active/employed?"
    )
    
    is_on_probation = models.BooleanField(
        default=False,
        help_text="Is staff on probation?"
    )
    
    probation_end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Probation end date"
    )
    
    is_retired = models.BooleanField(
        default=False,
        help_text="Has staff retired?"
    )
    
    retirement_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date of retirement"
    )
    
    is_on_leave = models.BooleanField(
        default=False,
        help_text="Is staff currently on leave?"
    )
    
    leave_start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Leave start date"
    )
    
    leave_end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Leave end date"
    )
    
    # Performance & Ratings
    performance_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        help_text="Overall performance rating (0-5)"
    )
    
    last_appraisal_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date of last performance appraisal"
    )
    
    next_appraisal_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date of next performance appraisal"
    )
    
    appraisal_notes = models.TextField(
        blank=True,
        help_text="Performance appraisal notes"
    )
    
    # Documents & Certificates
    resume = models.FileField(
        upload_to='staff_documents/resumes/',
        blank=True,
        null=True,
        help_text="Upload resume/CV"
    )
    
    certificates = models.FileField(
        upload_to='staff_documents/certificates/',
        blank=True,
        null=True,
        help_text="Upload certificates"
    )
    
    id_copy = models.FileField(
        upload_to='staff_documents/ids/',
        blank=True,
        null=True,
        help_text="Upload ID card copy"
    )
    
    passport_photo = models.ImageField(
        upload_to='staff_documents/photos/',
        blank=True,
        null=True,
        help_text="Passport photograph"
    )
    
    # Additional Information
    years_of_experience = models.IntegerField(
        default=0,
        help_text="Total years of work experience"
    )
    
    previous_employers = models.TextField(
        blank=True,
        help_text="Previous employers"
    )
    
    references = models.TextField(
        blank=True,
        help_text="Professional references"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__first_name']
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
        indexes = [
            models.Index(fields=['staff_id']),
            models.Index(fields=['employment_type']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
            models.Index(fields=['trcn_number']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.staff_id} ({self.user.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-generate staff ID and update leave balance"""
        
        # Auto-generate staff ID if not set
        if not self.staff_id:
            prefix = "STF"
            while True:
                random_num = ''.join(random.choices(string.digits, k=6))
                staff_id = f"{prefix}{random_num}"
                if not Staff.objects.filter(staff_id=staff_id).exists():
                    self.staff_id = staff_id
                    break
        
        # Calculate remaining leave days
        self.leave_days_remaining = self.annual_leave_days - self.leave_days_taken
        
        super().save(*args, **kwargs)
    
    def get_staff_type(self):
        """Get staff type based on user role"""
        teaching_roles = ['teacher', 'form_teacher', 'subject_teacher',
                         'head', 'hm', 'principal', 'vice_principal']
        
        if self.user.role in teaching_roles:
            return 'teaching'
        elif self.user.role in ['accountant', 'secretary', 'librarian',
                              'laboratory', 'security', 'cleaner']:
            return 'non_teaching'
        else:
            return 'other'
    
    def get_monthly_salary(self):
        """Calculate total monthly salary"""
        return self.basic_salary
    
    def get_employment_duration(self):
        """Calculate duration of employment"""
        from dateutil.relativedelta import relativedelta
        
        today = timezone.now().date()
        employment_duration = relativedelta(today, self.employment_date)
        
        return {
            'years': employment_duration.years,
            'months': employment_duration.months,
            'days': employment_duration.days
        }
    
    def can_access_student_records(self):
        """Check if staff can access student records"""
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal',
                        'teacher', 'form_teacher', 'subject_teacher']
        return self.user.role in allowed_roles
    
    def can_access_financial_records(self):
        """Check if staff can access financial records"""
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal', 'accountant']
        return self.user.role in allowed_roles
    
    
    
class StaffPermission(models.Model):
    """
    Staff Permission Model
    Manages granular permissions for staff members
    """
    
    staff = models.OneToOneField(
        Staff,
        on_delete=models.CASCADE,
        related_name='permissions',
        help_text="Staff member"
    )
    
    # Academic Permissions
    can_view_all_students = models.BooleanField(default=False)
    can_edit_student_records = models.BooleanField(default=False)
    can_view_all_results = models.BooleanField(default=False)
    can_edit_results = models.BooleanField(default=False)
    can_publish_results = models.BooleanField(default=False)
    
    # Staff Permissions
    can_view_all_staff = models.BooleanField(default=False)
    can_edit_staff_records = models.BooleanField(default=False)
    can_manage_staff_permissions = models.BooleanField(default=False)
    
    # Financial Permissions
    can_view_financial_records = models.BooleanField(default=False)
    can_manage_fees = models.BooleanField(default=False)
    can_process_payments = models.BooleanField(default=False)
    
    # Administrative Permissions
    can_manage_classes = models.BooleanField(default=False)
    can_manage_subjects = models.BooleanField(default=False)
    can_manage_sessions = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Staff Permission'
        verbose_name_plural = 'Staff Permissions'
    
    def __str__(self):
        return f"Permissions for {self.staff.staff_id}"
    
    def update_permissions(self, permissions_dict):
        """Update permissions from a dictionary"""
        for key, value in permissions_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()