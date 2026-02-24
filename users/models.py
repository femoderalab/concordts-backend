# users/models.py
"""
User models for the School Management System.
Contains the custom User model and related models.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import random
import string
import uuid
from django.conf import settings


# class CustomUserManager(BaseUserManager):
#     """
#     Custom user manager to handle user creation with registration numbers.
#     """
    
#     def create_user(self, email=None, password=None, **extra_fields):
#         """
#         Create and save a regular user with registration number.
#         """
#         # Generate registration number if not provided
#         if 'registration_number' not in extra_fields or not extra_fields['registration_number']:
#             while True:
#                 random_digits = ''.join(random.choices(string.digits, k=4))
#                 registration_number = f"CTS_{random_digits}"
#                 if not User.objects.filter(registration_number=registration_number).exists():
#                     extra_fields['registration_number'] = registration_number
#                     break
        
#         # Set default values for active and verified
#         extra_fields.setdefault('is_active', True)
#         extra_fields.setdefault('is_verified', True)
        
#         # Email can be None or empty string
#         if email is not None:
#             email = self.normalize_email(email)
#             if email == '':
#                 email = None
        
#         user = self.model(email=email, **extra_fields)
        
#         # Set password if provided, otherwise set default
#         if password:
#             user.set_password(password)
#         else:
#             # Set a default password that can be changed later
#             user.set_password('Student@2024')
            
#         user.save(using=self._db)
#         return user
    
#     def create_superuser(self, email=None, password=None, **extra_fields):
#         """
#         Create and save a superuser with administrative privileges.
#         """
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#         extra_fields.setdefault('is_verified', True)  # Add this line
#         extra_fields.setdefault('role', 'head')
        
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')
        
#         return self.create_user(email, password, **extra_fields)

class CustomUserManager(BaseUserManager):
    """
    Custom user manager to handle user creation with registration numbers.
    """
    
    def create_user(self, email=None, password=None, **extra_fields):
        """
        Create and save a regular user with registration number.
        """
        # Generate registration number if not provided
        if 'registration_number' not in extra_fields or not extra_fields['registration_number']:
            while True:
                random_digits = ''.join(random.choices(string.digits, k=4))
                registration_number = f"CTS_{random_digits}"
                if not User.objects.filter(registration_number=registration_number).exists():
                    extra_fields['registration_number'] = registration_number
                    break
        
        # Set default values for active and verified
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        
        # Email can be None or empty string
        if email is not None:
            email = self.normalize_email(email)
            if email == '':
                email = None
        
        user = self.model(email=email, **extra_fields)
        
        # Set password if provided, otherwise set default
        if password:
            user.set_password(password)
        else:
            # Set a default password that can be changed later
            user.set_password('Student@2024')
            
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        """
        Create and save a superuser with administrative privileges.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)  # Add this line
        extra_fields.setdefault('role', 'head')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User model for School Management System (Nigeria Context).
    Extends Django's AbstractUser to add school-specific fields.
    """
    
    # Remove username field from AbstractUser, we use registration_number instead
    username = None
    
    # Role Choices
    ROLE_CHOICES = (
        ('head', 'Head of School/Proprietor'),
        ('hm', 'Head Master'),
        ('principal', 'Principal'),
        ('vice_principal', 'Vice Principal'),
        ('teacher', 'Teacher'),
        ('form_teacher', 'Form Teacher'),
        ('subject_teacher', 'Subject Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent/Guardian'),
        ('accountant', 'Accountant/Bursar'),
        ('secretary', 'Secretary'),
        ('librarian', 'Librarian'),
        ('laboratory', 'Laboratory Technician'),
        ('security', 'Security Personnel'),
        ('cleaner', 'Cleaner'),
    )
    
    # Gender Choices
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    
    # Nigerian States
    NIGERIAN_STATES = (
        ('abia', 'Abia'), ('adamawa', 'Adamawa'), ('akwa_ibom', 'Akwa Ibom'),
        ('anambra', 'Anambra'), ('bauchi', 'Bauchi'), ('bayelsa', 'Bayelsa'),
        ('benue', 'Benue'), ('borno', 'Borno'), ('cross_river', 'Cross River'),
        ('delta', 'Delta'), ('ebonyi', 'Ebonyi'), ('edo', 'Edo'),
        ('ekiti', 'Ekiti'), ('enugu', 'Enugu'), ('gombe', 'Gombe'),
        ('imo', 'Imo'), ('jigawa', 'Jigawa'), ('kaduna', 'Kaduna'),
        ('kano', 'Kano'), ('katsina', 'Katsina'), ('kebbi', 'Kebbi'),
        ('kogi', 'Kogi'), ('kwara', 'Kwara'), ('lagos', 'Lagos'),
        ('nasarawa', 'Nasarawa'), ('niger', 'Niger'), ('ogun', 'Ogun'),
        ('ondo', 'Ondo'), ('osun', 'Osun'), ('oyo', 'Oyo'),
        ('plateau', 'Plateau'), ('rivers', 'Rivers'), ('sokoto', 'Sokoto'),
        ('taraba', 'Taraba'), ('yobe', 'Yobe'), ('zamfara', 'Zamfara'),
        ('fct', 'Federal Capital Territory'),
    )
    
    # =====================
    # CORE USER FIELDS
    # =====================
    registration_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Auto-generated: CTS_XXXX format"
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True)
    alternative_phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,  # Allow null
        unique=False,  # Don't require unique since it's optional
        help_text="Email address (optional)"
    )
    
    # Address Information
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True)
    state_of_origin = models.CharField(max_length=50, choices=NIGERIAN_STATES, blank=True)
    lga = models.CharField(max_length=100, blank=True, verbose_name="Local Government Area")
    nationality = models.CharField(max_length=50, default='Nigerian')
    
    # =====================
    # PASSWORD RESET FIELDS  <-- ADD THESE
    # =====================
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)
    
    # =====================
    # STATUS & TRACKING
    # =====================
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    login_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Set custom manager
    objects = CustomUserManager()
    
    # Use registration_number as the username field for authentication
    USERNAME_FIELD = 'registration_number'
    
    # Required fields for all users
    # Required fields for all users (besides USERNAME_FIELD and password)
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['registration_number']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['reset_token']),  # Optional: Add index for reset token
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.registration_number} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """
        Auto-generate registration number if not set.
        """
        if not self.registration_number:
            while True:
                random_digits = ''.join(random.choices(string.digits, k=4))
                registration_number = f"CTS_{random_digits}"
                if not User.objects.filter(registration_number=registration_number).exists():
                    self.registration_number = registration_number
                    break
        
        self.is_active = True
        self.is_verified = True
        super().save(*args, **kwargs)
    
    def get_display_name(self):
        """
        Get a display-friendly name for the user.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.registration_number
    
    def can_change_password(self):
        """
        Check if user can change password themselves.
        """
        # Admin roles can change passwords
        admin_roles = ['head', 'hm', 'principal', 'vice_principal']
        return self.role in admin_roles or self.is_superuser
    
    def is_admin_user(self):
        """
        Check if user is admin (can add staff/students/parents).
        """
        admin_roles = ['head', 'hm', 'principal', 'secretary']
        return self.role in admin_roles or self.is_superuser
    
    def is_reset_token_valid(self):
        """
        Check if reset token is valid (not expired).
        """
        if not self.reset_token or not self.reset_token_expiry:
            return False
        return timezone.now() < self.reset_token_expiry
    
    def update_login_info(self, ip_address):
        """
        Update login information safely.
        """
        self.last_login = timezone.now()
        self.last_login_ip = ip_address
        self.login_count += 1
        self.save(update_fields=['last_login', 'last_login_ip', 'login_count'])
        
# In your User model, add this method:
    def get_staff_profile_info(self):
        """
        Safely get staff profile info or return None.
        This prevents the 'has staff role but no staff profile' error.
        """
        if self.role in ['head', 'hm', 'principal', 'vice_principal', 'teacher', 
                        'form_teacher', 'subject_teacher', 'accountant', 'secretary', 
                        'librarian', 'laboratory', 'security', 'cleaner']:
            # This is a staff role
            try:
                # Try to get staff profile, but don't crash if it doesn't exist
                return self.staff_profile
            except:
                # Staff profile doesn't exist yet - that's OK
                return None
        return None

    # Also add this property for convenience
    @property
    def has_staff_profile(self):
        """
        Check if user has a staff profile (without causing errors).
        """
        try:
            return hasattr(self, 'staff_profile') and self.staff_profile is not None
        except:
            return False

# Add this AFTER your User model, before any other models that might reference it

class Activity(models.Model):
    """
    Model for tracking system activities and notifications
    """
    
    # Activity types
    ACTIVITY_TYPES = (
        ('user_created', 'User Created'),
        ('user_updated', 'User Updated'),
        ('user_deleted', 'User Deleted'),
        ('student_created', 'Student Created'),
        ('student_updated', 'Student Updated'),
        ('parent_created', 'Parent Created'),
        ('parent_updated', 'Parent Updated'),
        ('staff_created', 'Staff Created'),
        ('staff_updated', 'Staff Updated'),
        ('result_published', 'Result Published'),
        ('result_updated', 'Result Updated'),
        ('fee_paid', 'Fee Paid'),
        ('fee_updated', 'Fee Updated'),
        ('announcement', 'Announcement'),
        ('system', 'System Activity'),
    )
    
    # Target types (what the activity is about)
    TARGET_TYPES = (
        ('user', 'User'),
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('staff', 'Staff'),
        ('result', 'Result'),
        ('fee', 'Fee'),
        ('announcement', 'Announcement'),
        ('system', 'System'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Activity details
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    action = models.CharField(max_length=255)
    description = models.TextField()
    
    # User who performed the action
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities'
    )
    
    # User details (cached for performance)
    user_name = models.CharField(max_length=255, blank=True)
    user_role = models.CharField(max_length=50, blank=True)
    
    # Target information
    target_type = models.CharField(max_length=50, choices=TARGET_TYPES, null=True, blank=True)
    target_id = models.CharField(max_length=100, null=True, blank=True)
    target_name = models.CharField(max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_system = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['user']),
            models.Index(fields=['is_read']),
            models.Index(fields=['target_type', 'target_id']),
        ]
    
    def __str__(self):
        return f"{self.activity_type}: {self.action}"
    
    def save(self, *args, **kwargs):
        """Save with cached user information"""
        if self.user:
            if not self.user_name:
                self.user_name = self.user.get_full_name() or self.user.username
            if not self.user_role:
                self.user_role = self.user.role
        
        super().save(*args, **kwargs)
    
    def mark_as_read(self):
        """Mark activity as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at', 'updated_at'])
    
    @classmethod
    def log_activity(cls, activity_type, action, description, user=None, 
                    target_type=None, target_id=None, target_name=None, 
                    metadata=None, request=None):
        """Helper method to log activities"""
        
        activity_data = {
            'activity_type': activity_type,
            'action': action,
            'description': description,
            'user': user,
            'target_type': target_type,
            'target_id': target_id,
            'target_name': target_name,
            'metadata': metadata or {},
            'is_system': user is None
        }
        
        # Add request information if available
        if request:
            activity_data['ip_address'] = cls._get_client_ip(request)
            activity_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        # Create activity
        activity = cls.objects.create(**activity_data)
        
        # Return activity for further processing if needed
        return activity
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')