# academic/signals.py
"""
Signals for Academic models.
Handles auto-generated fields and relationships.
"""

from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.utils.text import slugify
import logging
from .models import (
    AcademicSession, AcademicTerm, Program, ClassLevel, 
    Subject, Class, ClassSubject
)
from django.db import transaction

logger = logging.getLogger(__name__)


# ============================================
# ACADEMIC SESSION SIGNALS
# ============================================

@receiver(pre_save, sender=AcademicSession)
def academic_session_pre_save(sender, instance, **kwargs):
    """
    Signal before academic session is saved.
    """
    # Ensure name is properly formatted if not provided
    if not instance.name and instance.start_date and instance.end_date:
        instance.name = f"{instance.start_date.year}/{instance.end_date.year}"
    
    # If this session is set as current, ensure only one current session exists
    if instance.is_current:
        # Using transaction to avoid race conditions
        with transaction.atomic():
            AcademicSession.objects.filter(
                is_current=True
            ).exclude(pk=instance.pk).update(is_current=False)


@receiver(post_save, sender=AcademicSession)
def academic_session_post_save(sender, instance, created, **kwargs):
    """
    Signal after academic session is saved.
    """
    if created:
        logger.info(f"New academic session created: {instance.name}")


# ============================================
# ACADEMIC TERM SIGNALS
# ============================================

@receiver(pre_save, sender=AcademicTerm)
def academic_term_pre_save(sender, instance, **kwargs):
    """
    Signal before academic term is saved.
    """
    # Generate term name if not provided
    if not instance.name and instance.session and instance.term:
        instance.name = f"{instance.get_term_display()} {instance.session.name}"
    
    # If this term is set as current, ensure only one current term exists
    if instance.is_current:
        with transaction.atomic():
            AcademicTerm.objects.filter(
                is_current=True
            ).exclude(pk=instance.pk).update(is_current=False)


@receiver(post_save, sender=AcademicTerm)
def academic_term_post_save(sender, instance, created, **kwargs):
    """
    Signal after academic term is saved.
    """
    if created:
        logger.info(f"New academic term created: {instance.name}")


# ============================================
# PROGRAM SIGNALS
# ============================================

@receiver(pre_save, sender=Program)
def program_pre_save(sender, instance, **kwargs):
    """
    Signal before program is saved.
    """
    # Generate code from name if not provided
    if not instance.code and instance.name:
        # Create code from program type and name
        code_parts = []
        if instance.program_type:
            code_parts.append(instance.program_type[:3].upper())
        if instance.name:
            # Take first letter of each word
            code_parts.append(''.join(word[0].upper() for word in instance.name.split() if word))
        
        instance.code = '_'.join(code_parts)


@receiver(post_save, sender=Program)
def program_post_save(sender, instance, created, **kwargs):
    """
    Signal after program is saved.
    """
    if created:
        logger.info(f"New program created: {instance.name} ({instance.code})")


# ============================================
# CLASS LEVEL SIGNALS
# ============================================

@receiver(pre_save, sender=ClassLevel)
def class_level_pre_save(sender, instance, **kwargs):
    """
    Signal before class level is saved.
    """
    # Generate name from level if not provided
    if not instance.name:
        instance.name = instance.get_level_display()
    
    # Generate code if not provided
    if not instance.code:
        if instance.program and instance.level:
            instance.code = f"{instance.program.code}_{instance.level}"


@receiver(post_save, sender=ClassLevel)
def class_level_post_save(sender, instance, created, **kwargs):
    """
    Signal after class level is saved.
    """
    if created:
        logger.info(f"New class level created: {instance.name} ({instance.code})")


# ============================================
# SUBJECT SIGNALS
# ============================================

@receiver(pre_save, sender=Subject)
def subject_pre_save(sender, instance, **kwargs):
    """
    Signal before subject is saved.
    """
    # Generate short name from name if not provided
    if not instance.short_name and instance.name:
        # Take first 3 words or 15 characters
        words = instance.name.split()
        if len(words) <= 3:
            instance.short_name = instance.name[:20]
        else:
            instance.short_name = ' '.join(words[:3])[:20]
    
    # Generate code from name if not provided
    if not instance.code and instance.name:
        # Create code from subject name (e.g., "Mathematics" -> "MATH")
        if len(instance.name.split()) == 1:
            instance.code = instance.name[:4].upper()
        else:
            # Take first letters of first two words
            words = instance.name.split()
            instance.code = ''.join(word[0].upper() for word in words[:2] if word)
    
    # Set default pass mark if not provided
    if not instance.pass_mark:
        instance.pass_mark = 40  # Nigerian standard pass mark


@receiver(post_save, sender=Subject)
def subject_post_save(sender, instance, created, **kwargs):
    """
    Signal after subject is saved.
    """
    if created:
        logger.info(f"New subject created: {instance.name} ({instance.code})")


# ============================================
# CLASS SIGNALS
# ============================================

@receiver(pre_save, sender=Class)
def class_pre_save(sender, instance, **kwargs):
    """
    Signal before class is saved.
    """
    # Generate slug for URL
    if not instance.slug and instance.name and instance.session and instance.term:
        slug_text = f"{instance.name}-{instance.session.name}-{instance.term.term}"
        instance.slug = slugify(slug_text)
    
    # Generate code if not provided
    if not instance.code and instance.class_level and instance.session and instance.term:
        class_code = instance.class_level.code.replace('_', '')
        term_code = instance.term.term[:1].upper()
        year = instance.session.start_date.year % 100
        
        # Find next sequence number for this class
        existing_classes = Class.objects.filter(
            class_level=instance.class_level,
            session=instance.session,
            term=instance.term
        ).count()
        
        seq = existing_classes + 1
        instance.code = f"{class_code}{term_code}{year:02d}{seq:02d}"


@receiver(post_save, sender=Class)
def class_post_save(sender, instance, created, **kwargs):
    """
    Signal after class is saved.
    """
    if created:
        logger.info(f"New class created: {instance.name} ({instance.code})")
        
        # Auto-assign subjects based on class level and stream
        try:
            assigned_subjects = instance.get_assigned_subjects()
            for subject in assigned_subjects:
                # Check if subject is already assigned
                if not ClassSubject.objects.filter(
                    class_obj=instance,
                    subject=subject
                ).exists():
                    ClassSubject.objects.create(
                        class_obj=instance,
                        subject=subject,
                        is_active=True,
                        is_compulsory=subject.is_compulsory
                    )
                    
            logger.info(f"Auto-assigned {len(assigned_subjects)} subjects to class {instance.name}")
        except Exception as e:
            logger.error(f"Error auto-assigning subjects to class {instance.name}: {e}")


# ============================================
# CLASS-SUBJECT SIGNALS
# ============================================

@receiver(pre_save, sender=ClassSubject)
def class_subject_pre_save(sender, instance, **kwargs):
    """
    Signal before class-subject assignment is saved.
    """
    # Validate that subject is appropriate for class level
    if instance.class_obj and instance.subject:
        class_level = instance.class_obj.class_level.level
        
        # Check subject availability for this class level
        if class_level == 'creche' and not instance.subject.available_for_creche:
            raise ValueError(f"Subject {instance.subject.name} is not available for creche level")
        elif class_level.startswith('nursery') or class_level.startswith('kg_') and not instance.subject.available_for_nursery:
            raise ValueError(f"Subject {instance.subject.name} is not available for nursery level")
        elif class_level.startswith('primary_') and not instance.subject.available_for_primary:
            raise ValueError(f"Subject {instance.subject.name} is not available for primary level")
        elif class_level.startswith('jss_') and not instance.subject.available_for_jss:
            raise ValueError(f"Subject {instance.subject.name} is not available for JSS level")
        elif class_level.startswith('sss_') and not instance.subject.available_for_sss:
            raise ValueError(f"Subject {instance.subject.name} is not available for SSS level")
        
        # For SSS, check stream compatibility
        if class_level.startswith('sss_'):
            class_stream = instance.class_obj.stream
            subject_stream = instance.subject.stream
            
            if class_stream and subject_stream != 'general' and class_stream != subject_stream:
                raise ValueError(
                    f"Subject {instance.subject.name} ({subject_stream}) "
                    f"is not compatible with class stream ({class_stream})"
                )


@receiver(post_save, sender=ClassSubject)
def class_subject_post_save(sender, instance, created, **kwargs):
    """
    Signal after class-subject assignment is saved.
    """
    if created:
        logger.info(
            f"Subject {instance.subject.name} assigned to class {instance.class_obj.name} "
            f"(Teacher: {instance.teacher.get_full_name() if instance.teacher else 'Not assigned'})"
        )


# ============================================
# CASCADE DELETE HANDLERS
# ============================================

@receiver(pre_delete, sender=Program)
def program_pre_delete(sender, instance, **kwargs):
    """
    Signal before program is deleted.
    Log the deletion for audit purposes.
    """
    logger.warning(f"Deleting program: {instance.name} ({instance.code})")


@receiver(pre_delete, sender=ClassLevel)
def class_level_pre_delete(sender, instance, **kwargs):
    """
    Signal before class level is deleted.
    """
    logger.warning(f"Deleting class level: {instance.name} ({instance.code})")


@receiver(pre_delete, sender=Subject)
def subject_pre_delete(sender, instance, **kwargs):
    """
    Signal before subject is deleted.
    """
    logger.warning(f"Deleting subject: {instance.name} ({instance.code})")


# ============================================
# BULK OPERATION SIGNALS
# ============================================

def handle_bulk_class_creation(sender, classes, **kwargs):
    """
    Signal handler for bulk class creation.
    """
    logger.info(f"Bulk creating {len(classes)} classes")
    
    # Auto-assign subjects to each class
    for class_obj in classes:
        try:
            assigned_subjects = class_obj.get_assigned_subjects()
            for subject in assigned_subjects:
                ClassSubject.objects.get_or_create(
                    class_obj=class_obj,
                    subject=subject,
                    defaults={'is_active': True, 'is_compulsory': subject.is_compulsory}
                )
        except Exception as e:
            logger.error(f"Error auto-assigning subjects to class {class_obj.name}: {e}")


# Connect custom signal (you would define this signal in your views)
# from django.dispatch import Signal
# bulk_class_created = Signal()
# bulk_class_created.connect(handle_bulk_class_creation)