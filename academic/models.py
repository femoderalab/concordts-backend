"""
Complete Academic Models for Nigerian School Management System
Updated with all Nigerian classes, subjects, and proper assignments
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from users.models import User 


class AcademicSession(models.Model):
    """Academic Session - e.g., 2024/2025"""
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Academic Session'
        verbose_name_plural = 'Academic Sessions'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicSession.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class AcademicTerm(models.Model):
    """Academic Term"""
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='terms')
    
    TERM_CHOICES = [
        ('first', 'First Term'),
        ('second', 'Second Term'),
        ('third', 'Third Term'),
    ]
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    # Nigerian school calendar
    resumption_date = models.DateField(null=True, blank=True)
    vacation_date = models.DateField(null=True, blank=True)
    total_school_days = models.IntegerField(default=0)
    total_teaching_weeks = models.IntegerField(default=0)
    mid_term_break_start = models.DateField(null=True, blank=True)
    mid_term_break_end = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['session__start_date', 'term']
        unique_together = ['session', 'term']

    def __str__(self):
        return f"{self.get_term_display()} - {self.session.name}"

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicTerm.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        if not self.name:
            self.name = f"{self.get_term_display()} {self.session.name}"
        super().save(*args, **kwargs)


class Program(models.Model):
    """Academic Program"""
    PROGRAM_CHOICES = [
        ('creche', 'Creche'),
        ('nursery', 'Nursery'),
        ('primary', 'Primary School'),
        ('junior_secondary', 'Junior Secondary School (JSS)'),
        ('senior_secondary', 'Senior Secondary School (SSS)'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    program_type = models.CharField(max_length=30, choices=PROGRAM_CHOICES)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    duration_years = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['program_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class ClassLevel(models.Model):
    """Class Level - All Nigerian Classes"""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='class_levels')
    
    LEVEL_CHOICES = [
        # Creche
        ('creche', 'Creche'),
        
        # Nursery
        ('nursery_1', 'Nursery 1'),
        ('nursery_2', 'Nursery 2'),
        ('kg_1', 'Kindergarten 1 (KG 1)'),
        ('kg_2', 'Kindergarten 2 (KG 2)'),
        
        # Primary
        ('primary_1', 'Primary 1 (Basic 1)'),
        ('primary_2', 'Primary 2 (Basic 2)'),
        ('primary_3', 'Primary 3 (Basic 3)'),
        ('primary_4', 'Primary 4 (Basic 4)'),
        ('primary_5', 'Primary 5 (Basic 5)'),
        ('primary_6', 'Primary 6 (Basic 6)'),
        
        # Junior Secondary
        ('jss_1', 'JSS 1'),
        ('jss_2', 'JSS 2'),
        ('jss_3', 'JSS 3'),
        
        # Senior Secondary
        ('sss_1', 'SSS 1'),
        ('sss_2', 'SSS 2'),
        ('sss_3', 'SSS 3'),
    ]
    
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    order = models.IntegerField(default=0)
    min_age = models.IntegerField(default=0)
    max_age = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Nigerian specific
    has_common_entrance = models.BooleanField(default=False)
    has_bece = models.BooleanField(default=False)
    has_waec_neco = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['program__program_type', 'order']
        unique_together = ['program', 'level']

    def __str__(self):
        return self.name


class Subject(models.Model):
    """All Nigerian Subjects with automatic class assignment"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    short_name = models.CharField(max_length=50, blank=True)
    
    SUBJECT_TYPE_CHOICES = [
        ('core', 'Core Subject'),
        ('elective', 'Elective Subject'),
        ('vocational', 'Vocational Subject'),
        ('religious', 'Religious Studies'),
        ('language', 'Language'),
        ('science', 'Science'),
        ('arts', 'Arts/Humanities'),
        ('commercial', 'Commercial/Business'),
        ('technical', 'Technical'),
        ('pre_school', 'Pre-School Subject'),
    ]
    subject_type = models.CharField(max_length=30, choices=SUBJECT_TYPE_CHOICES, default='core')
    
    # Stream for SSS
    STREAM_CHOICES = [
        ('science', 'Science Stream'),
        ('commercial', 'Commercial Stream'),
        ('arts', 'Arts/Humanities Stream'),
        ('general', 'General (All Streams)'),
        ('technical', 'Technical Stream'),
        ('pre_school', 'Pre-School'),
    ]
    stream = models.CharField(max_length=20, choices=STREAM_CHOICES, default='general')
    
    # Subject configuration
    is_compulsory = models.BooleanField(default=False)
    is_examinable = models.BooleanField(default=True)
    has_practical = models.BooleanField(default=False)
    
    # Assessment configuration (Nigerian standard: CA 40%, Exam 60%)
    ca_weight = models.IntegerField(default=40, help_text="CA percentage (40%)")
    exam_weight = models.IntegerField(default=60, help_text="Exam percentage (60%)")
    total_marks = models.IntegerField(default=100, help_text="Total marks obtainable")
    pass_mark = models.IntegerField(default=40, help_text="Pass mark (40)")
    
    # Class level availability
    available_for_creche = models.BooleanField(default=False)
    available_for_nursery = models.BooleanField(default=False)
    available_for_primary = models.BooleanField(default=False)
    available_for_jss = models.BooleanField(default=False)
    available_for_sss = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Class(models.Model):
    """Class - Specific sections for each term"""
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='classes')
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE, related_name='classes')
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE, related_name='classes')
    
    name = models.CharField(max_length=100, help_text="e.g., JSS 1 Three, SSS 2 Science A")
    code = models.CharField(max_length=20)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    # For SSS classes
    STREAM_CHOICES = [
        ('science', 'Science'),
        ('commercial', 'Commercial'),
        ('arts', 'Arts/Humanities'),
        ('general', 'General'),
    ]
    stream = models.CharField(max_length=20, choices=STREAM_CHOICES, blank=True, null=True)
    
    # Capacity
    max_capacity = models.IntegerField(default=40)
    current_enrollment = models.IntegerField(default=0)
    
    # Teachers
    class_teacher = models.ForeignKey(
        User,  # Direct import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_taught'
    )
    
    # Location
    room_number = models.CharField(max_length=20, blank=True)
    building = models.CharField(max_length=100, blank=True)
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['class_level__order', 'name']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        unique_together = ['session', 'term', 'class_level', 'name']

    def __str__(self):
        return f"{self.name} - {self.session.name} ({self.term.get_term_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.session.name}-{self.term.term}")
        super().save(*args, **kwargs)
    
    def get_assigned_subjects(self):
        """Get all subjects assigned to this class based on level and stream"""
        class_level_code = self.class_level.level
        
        # Creche subjects
        if class_level_code == 'creche':
            return Subject.objects.filter(available_for_creche=True, is_active=True)
        
        # Nursery subjects (Nursery 1, 2, KG 1, 2)
        elif class_level_code in ['nursery_1', 'nursery_2', 'kg_1', 'kg_2']:
            return Subject.objects.filter(available_for_nursery=True, is_active=True)
        
        # Primary subjects
        elif class_level_code.startswith('primary'):
            return Subject.objects.filter(available_for_primary=True, is_active=True)
        
        # JSS subjects
        elif class_level_code.startswith('jss'):
            return Subject.objects.filter(available_for_jss=True, is_active=True)
        
        # SSS subjects (with stream filtering)
        elif class_level_code.startswith('sss'):
            if self.stream and self.stream != 'general':
                # Get stream-specific subjects + general subjects
                return Subject.objects.filter(
                    available_for_sss=True,
                    is_active=True
                ).filter(
                    models.Q(stream=self.stream) | models.Q(stream='general')
                )
            else:
                # All SSS subjects
                return Subject.objects.filter(available_for_sss=True, is_active=True)
        
        return Subject.objects.none()

class TeacherProfile(models.Model):
    """
    Teacher Profile - Extended information for teaching staff
    """
    
    staff = models.OneToOneField(
        'staff.Staff',
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        help_text="Linked staff record"
    )
    
    # Teacher Type
    TEACHER_TYPE_CHOICES = [
        ('class_teacher', 'Class Teacher'),
        ('subject_teacher', 'Subject Teacher'),
        ('head_of_department', 'Head of Department'),
        ('senior_teacher', 'Senior Teacher'),
        ('assistant_teacher', 'Assistant Teacher'),
    ]
    
    teacher_type = models.CharField(
        max_length=30,
        choices=TEACHER_TYPE_CHOICES,
        default='subject_teacher'
    )
    
    # Teaching subjects and classes
    subjects = models.ManyToManyField(
        Subject,
        related_name='teachers',
        blank=True,
        help_text="Subjects this teacher can teach"
    )
    
    class_levels = models.ManyToManyField(
        ClassLevel,
        related_name='teachers',
        blank=True,
        help_text="Class levels this teacher can teach"
    )
    
    assigned_classes = models.ManyToManyField(
        Class,
        related_name='subject_teachers',
        blank=True,
        help_text="Classes currently assigned to this teacher"
    )
    
    assistant_classes = models.ManyToManyField(
        Class,
        related_name='assistant_teachers',
        blank=True,
        help_text="Classes where teacher is assistant"
    )
    
    # Stream specialization (for SSS)
    STREAM_CHOICES = [
        ('science', 'Science'),
        ('commercial', 'Commercial'),
        ('arts', 'Arts/Humanities'),
        ('general', 'General'),
        ('technical', 'Technical'),
    ]
    
    stream_specialization = models.CharField(
        max_length=20,
        choices=STREAM_CHOICES,
        blank=True,
        help_text="Stream specialization"
    )
    
    # Teaching workload
    max_periods_per_week = models.IntegerField(
        default=30,
        help_text="Maximum teaching periods per week"
    )
    
    current_periods_per_week = models.IntegerField(
        default=0,
        help_text="Current teaching periods per week"
    )
    
    # Head of Department
    hod_subjects = models.ManyToManyField(
        Subject,
        related_name='hod_teachers',
        blank=True,
        help_text="Subjects where teacher is HOD"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Teacher Profile'
        verbose_name_plural = 'Teacher Profiles'
    
    def __str__(self):
        return f"Teacher: {self.staff.user.get_full_name()}"
    
    def get_workload_percentage(self):
        """Calculate workload as percentage"""
        if self.max_periods_per_week > 0:
            return round((self.current_periods_per_week / self.max_periods_per_week) * 100, 2)
        return 0
    
    def get_workload_status(self):
        """Get workload status"""
        percentage = self.get_workload_percentage()
        if percentage >= 90:
            return 'overloaded'
        elif percentage >= 70:
            return 'full'
        elif percentage >= 50:
            return 'moderate'
        else:
            return 'light'
    
    def get_students(self):
        """Get all students this teacher teaches"""
        from students.models import Student
        return Student.objects.filter(
            enrollments__class_obj__in=self.assigned_classes.all()
        ).distinct()
    
    def get_class_teacher_students(self):
        """Get students where teacher is class teacher"""
        from students.models import Student
        return Student.objects.filter(
            enrollments__class_obj__class_teacher=self.staff.user
        ).distinct()
    
    def get_subjects_list(self):
        """Get list of subject names"""
        return [s.name for s in self.subjects.all()]
    
    def get_class_levels_list(self):
        """Get list of class level names"""
        return [cl.name for cl in self.class_levels.all()]
    
    def get_assigned_classes_list(self):
        """Get list of assigned class names"""
        return [c.name for c in self.assigned_classes.all()]

class ClassSubject(models.Model):
    """Links subjects to classes with teacher assignments"""
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_assignments')
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_assignments'
    )
    
    is_active = models.BooleanField(default=True)
    is_compulsory = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['class_obj', 'subject']

    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.name}"