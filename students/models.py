"""
Student models for the School Management System.
"""

from django.db import models
from django.utils import timezone
import random
import string
from django.db.models import Q
from users.models import User  # Changed from AUTH_USER_MODEL


class Student(models.Model):
    """
    Student Model - Nigerian School System
    Extends the main User model with student-specific fields
    """
    
    # Core Relationships
    user = models.OneToOneField(
        User,  # Changed from settings.AUTH_USER_MODEL
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text="Linked user account"
    )
    
    # Academic Information
    class_level = models.ForeignKey(
        'academic.ClassLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Current class/grade level"
    )
    
    # Secondary School Stream
    STREAM_CHOICES = [
        ('science', 'Science'),
        ('commercial', 'Commercial'),
        ('art', 'Arts/Humanities'),
        ('general', 'General (No stream yet)'),
        ('technical', 'Technical'),
        ('none', 'Not Applicable (Primary School)'),
    ]
    
    stream = models.CharField(
        max_length=20,
        choices=STREAM_CHOICES,
        default='none',
        help_text="Secondary school stream (Science/Commercial/Arts)"
    )
    
    # Admission Information
    admission_date = models.DateField(
        default=timezone.now,
        help_text="Date student was admitted"
    )
    
    admission_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="School admission number (e.g., CTS_2024_001)"
    )
    
    student_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="School-specific student ID"
    )
    
    # Personal Information
    age_at_admission = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Student's age when admitted"
    )
    
    place_of_birth = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Student's place of birth (City, State)"
    )
    
    home_language = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Primary language spoken at home"
    )
    
    # House/Group System
    HOUSE_CHOICES = [
        ('red', 'Red House'),
        ('blue', 'Blue House'),
        ('green', 'Green House'),
        ('yellow', 'Yellow House'),
        ('purple', 'Purple House'),
        ('orange', 'Orange House'),
        ('none', 'No House Assigned'),
    ]
    
    house = models.CharField(
        max_length=20,
        choices=HOUSE_CHOICES,
        default='none',
        help_text="House/Group assignment"
    )
    
    # Previous School Information
    previous_class = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Previous class attended"
    )
    
    previous_school = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Name of previous school"
    )
    
    transfer_certificate_no = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Transfer certificate number"
    )
    
    # Prefect/Leadership Roles
    is_prefect = models.BooleanField(
        default=False,
        blank=True,
        
        help_text="Is this student a prefect?"
    )
    
    prefect_role = models.CharField(
        max_length=100,
        blank=True,
        help_text="Prefect role/position"
    )
    
    # Student Category
    STUDENT_CATEGORY_CHOICES = [
        ('day', 'Day Student'),
        ('boarding', 'Boarding Student'),
        ('special_needs', 'Special Needs Student'),
        ('scholarship', 'Scholarship Student'),
        ('repeat', 'Repeating Student'),
        ('new', 'New Student'),
    ]
    
    student_category = models.CharField(
        max_length=20,
        choices=STUDENT_CATEGORY_CHOICES,
        default='day',
        help_text="Student category/type"
    )
    
    # Parent/Guardian Links
    father = models.ForeignKey(
    'parents.Parent',
    on_delete=models.SET_NULL,
    null=True,
    related_name='father_of_students'
    )

    mother = models.ForeignKey(
        'parents.Parent',
        on_delete=models.SET_NULL,
        null=True,
        related_name='mother_of_students'
    )

    
    # Emergency Contact
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Emergency contact person"
    )
    
    emergency_contact_phone = models.CharField(
        max_length=15,
        blank=True,
        default='',
        help_text="Emergency contact phone"
    )
    
    emergency_contact_relationship = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Relationship to student"
    )
    
    # Fee Information
    FEE_STATUS_CHOICES = [
        ('paid_full', 'Paid in Full'),
        ('paid_partial', 'Partially Paid'),
        ('not_paid', 'Not Paid'),
        ('scholarship', 'On Scholarship'),
        ('exempted', 'Fee Exempted'),
    ]
    
    fee_status = models.CharField(
        max_length=20,
        choices=FEE_STATUS_CHOICES,
        default='not_paid',
        help_text="Current fee payment status"
    )
    
    total_fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total fee amount for the term"
    )
    
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Amount paid so far"
    )
    
    balance_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Remaining balance to pay"
    )
    
    # Fee Payment Evidence
    fee_payment_evidence = models.ImageField(
        upload_to='fee_evidence/',
        blank=True,
        null=True,
        help_text="Upload payment receipt/evidence"
    )
    
    last_payment_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date of last fee payment"
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
    
    # Medical Information
    has_allergies = models.BooleanField(
        default=False,
        help_text="Does child have any allergies?"
    )
    
    allergy_details = models.TextField(
        blank=True,
        help_text="Please specify allergies if any"
    )
    
    has_received_vaccinations = models.BooleanField(
        default=True,
        help_text="Has child received required vaccinations?"
    )
    
    family_doctor_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of family doctor/clinic"
    )
    
    family_doctor_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Doctor's phone number"
    )
    
    medical_conditions = models.TextField(
        blank=True,
        help_text="Any known medical conditions"
    )
    
    # Special Needs
    has_learning_difficulties = models.BooleanField(
        default=False,
        help_text="Does child have any identified learning difficulties?"
    )
    
    learning_difficulties_details = models.TextField(
        blank=True,
        help_text="Please elaborate on learning difficulties or developmental needs"
    )
    
    # Document Upload Checklist
    birth_certificate_uploaded = models.BooleanField(default=False)
    birth_certificate = models.FileField(
        upload_to='student_documents/birth_certificates/',
        blank=True,
        null=True,
        help_text="Upload birth certificate"
    )
    
    student_image_uploaded = models.BooleanField(default=False)
    student_image = models.ImageField(
        upload_to='student_documents/images/',
        blank=True,
        null=True,
        help_text="Upload student photograph"
    )
    
    immunization_record_uploaded = models.BooleanField(default=False)
    immunization_record = models.FileField(
        upload_to='student_documents/immunization/',
        blank=True,
        null=True,
        help_text="Upload immunization record"
    )
    
    previous_school_report_uploaded = models.BooleanField(default=False)
    previous_school_report = models.FileField(
        upload_to='student_documents/reports/',
        blank=True,
        null=True,
        help_text="Upload previous school report"
    )
    
    parent_id_copy_uploaded = models.BooleanField(default=False)
    parent_id_copy = models.FileField(
        upload_to='student_documents/parent_ids/',
        blank=True,
        null=True,
        help_text="Upload parent/guardian ID copy"
    )
    
    # Transportation
    TRANSPORT_CHOICES = [
        ('school_bus', 'School Bus'),
        ('parent_drop', 'Parent Drop-off'),
        ('public_transport', 'Public Transport'),
        ('walk', 'Walks to School'),
        ('other', 'Other'),
    ]
    
    transportation_mode = models.CharField(
        max_length=20,
        choices=TRANSPORT_CHOICES,
        default='parent_drop',
        help_text="Mode of transportation to school"
    )
    
    bus_route = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bus route (if using school bus)"
    )
    
    # Status Flags
    is_active = models.BooleanField(
        default=True,
        help_text="Is student currently active/enrolled?"
    )
    
    is_graduated = models.BooleanField(
        default=False,
        help_text="Has student graduated?"
    )
    
    graduation_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date of graduation"
    )
    
    # Attendance Tracking
    days_present = models.PositiveIntegerField(default=0)
    days_absent = models.PositiveIntegerField(default=0)
    days_late = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['class_level__order', 'user__first_name']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        indexes = [
            models.Index(fields=['admission_number']),
            models.Index(fields=['student_id']),
            models.Index(fields=['class_level']),
            models.Index(fields=['stream']),
            models.Index(fields=['fee_status']),
        ]
    
    def __str__(self):
        class_display = self.class_level.name if self.class_level else "No Class"
        return f"{self.user.get_full_name()} - {class_display}"
    
    def save(self, *args, **kwargs):
        """Auto-generate fields and calculate balances"""
        
        # Auto-generate admission number if not set
        if not self.admission_number:
            year = timezone.now().year
            while True:
                random_num = ''.join(random.choices(string.digits, k=4))
                admission_num = f"CTS_{year}_{random_num}"
                if not Student.objects.filter(admission_number=admission_num).exists():
                    self.admission_number = admission_num
                    break
        
        # Auto-generate student ID if not set
        if not self.student_id:
            prefix = "STU"
            while True:
                random_num = ''.join(random.choices(string.digits, k=6))
                student_id = f"{prefix}{random_num}"
                if not Student.objects.filter(student_id=student_id).exists():
                    self.student_id = student_id
                    break
        
        # Calculate age at admission if not set
        if not self.age_at_admission and self.user.date_of_birth and self.admission_date:
            age = self.admission_date.year - self.user.date_of_birth.year
            if (self.admission_date.month, self.admission_date.day) < \
               (self.user.date_of_birth.month, self.user.date_of_birth.day):
                age -= 1
            self.age_at_admission = age
        
        # Calculate balance automatically
        self.balance_due = self.total_fee_amount - self.amount_paid
        
        # Update fee status based on payments
        if self.total_fee_amount > 0:
            if self.amount_paid >= self.total_fee_amount:
                self.fee_status = 'paid_full'
            elif self.amount_paid > 0:
                self.fee_status = 'paid_partial'
            elif self.fee_status not in ['scholarship', 'exempted']:
                self.fee_status = 'not_paid'
        
        # Update document upload flags
        self.birth_certificate_uploaded = bool(self.birth_certificate)
        self.student_image_uploaded = bool(self.student_image)
        self.immunization_record_uploaded = bool(self.immunization_record)
        self.previous_school_report_uploaded = bool(self.previous_school_report)
        self.parent_id_copy_uploaded = bool(self.parent_id_copy)
        
        # Update user's role to student if not already
        if self.user.role != 'student':
            self.user.role = 'student'
            self.user.save()
        
        super().save(*args, **kwargs)
    
    def get_parents(self):
        """Get both parents if available"""
        parents = []
        if self.father:
            parents.append(self.father)
        if self.mother:
            parents.append(self.mother)
        return parents
    
    def get_fee_summary(self):
        """Get fee payment summary"""
        if self.total_fee_amount > 0:
            percentage_paid = (self.amount_paid / self.total_fee_amount) * 100
        else:
            percentage_paid = 0
        
        return {
            'total_fee': float(self.total_fee_amount),
            'paid': float(self.amount_paid),
            'balance': float(self.balance_due),
            'status': self.get_fee_status_display(),
            'percentage_paid': round(percentage_paid, 2)
        }
    
    def get_document_checklist_summary(self):
        """Get summary of uploaded documents"""
        return {
            'birth_certificate': self.birth_certificate_uploaded,
            'student_image': self.student_image_uploaded,
            'immunization_record': self.immunization_record_uploaded,
            'previous_school_report': self.previous_school_report_uploaded,
            'parent_id_copy': self.parent_id_copy_uploaded,
            'all_documents_uploaded': all([
                self.birth_certificate_uploaded,
                self.student_image_uploaded,
                self.immunization_record_uploaded,
                self.previous_school_report_uploaded,
                self.parent_id_copy_uploaded
            ])
        }
    
    def can_edit_profile(self, user):
        """Check if user can edit this student's profile"""
        allowed_roles = ['head', 'hm', 'principal', 'vice_principal', 'accountant', 'secretary']
        return user.role in allowed_roles or user.is_staff
    
    def get_academic_level(self):
        """Get academic level category"""
        if not self.class_level:
            return 'Not Assigned'
        
        level_code = self.class_level.level
        
        if level_code in ['pre_nursery', 'nursery_1', 'nursery_2', 'kg_1', 'kg_2']:
            return 'Pre-School'
        elif level_code in ['primary_1', 'primary_2', 'primary_3', 'primary_4', 'primary_5', 'primary_6']:
            return 'Primary School'
        elif level_code in ['jss_1', 'jss_2', 'jss_3']:
            return 'Junior Secondary'
        elif level_code in ['sss_1', 'sss_2', 'sss_3']:
            return 'Senior Secondary'
        else:
            return 'Unknown'


class StudentEnrollment(models.Model):
    """
    Student Enrollment Model
    Links students to classes for specific sessions/terms
    """
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Student"
    )
    
    class_obj = models.ForeignKey(
        'academic.Class',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Class"
    )
    
    session = models.ForeignKey(
        'academic.AcademicSession',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Academic session"
    )
    
    term = models.ForeignKey(
        'academic.AcademicTerm',
        on_delete=models.CASCADE,
        related_name='enrollments',
        help_text="Academic term"
    )
    
    # Enrollment Information
    enrollment_date = models.DateField(
        default=timezone.now,
        help_text="Date of enrollment"
    )
    
    enrollment_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Unique enrollment number"
    )
    
    # Enrollment Status
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('withdrawn', 'Withdrawn'),
        ('transferred', 'Transferred'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Enrollment status"
    )
    
    # Academic Status
    is_repeating = models.BooleanField(
        default=False,
        help_text="Is student repeating this class?"
    )
    
    is_promoted = models.BooleanField(
        default=False,
        help_text="Has student been promoted from previous class?"
    )
    
    promotion_date = models.DateField(
        null=True,
        blank=True,
        help_text="Promotion date"
    )
    
    # Attendance Tracking
    days_present = models.IntegerField(
        default=0,
        help_text="Days present in this enrollment"
    )
    
    days_absent = models.IntegerField(
        default=0,
        help_text="Days absent in this enrollment"
    )
    
    # Performance - REMOVED average_score and position fields
    
    # Additional Information
    remarks = models.TextField(
        blank=True,
        help_text="Enrollment remarks"
    )
    
    enrolled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='enrolled_students',
        help_text="User who enrolled the student"
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_enrollments',
        help_text="User who approved the enrollment"
    )
    
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Approval date"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-enrollment_date', 'student']
        verbose_name = 'Student Enrollment'
        verbose_name_plural = 'Student Enrollments'
        unique_together = ['student', 'session', 'term', 'class_obj']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['enrollment_date']),
            models.Index(fields=['student', 'class_obj']),
        ]
    
    def __str__(self):
        if self.student and self.student.user:
            student_name = self.student.user.get_full_name()
        else:
            student_name = "Unknown Student"
        
        class_name = self.class_obj.name if self.class_obj else "No Class"
        session = self.session.name if self.session else "No Session"
        term = self.term.name if self.term else "No Term"
        
        return f"{student_name} - {class_name} ({session} {term})"
    
    def save(self, *args, **kwargs):
        """Auto-generate enrollment number"""
        if not self.enrollment_number:
            year = self.session.start_date.year
            student_id = self.student.student_id
            class_code = self.class_obj.code if self.class_obj.code else f"CLS{self.class_obj.id}"
            self.enrollment_number = f"ENR-{year}-{class_code}-{student_id}"
        
        super().save(*args, **kwargs)