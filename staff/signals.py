"""
Signals for Staff models.
Auto-creates Staff profile when user with staff role is created.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
import logging
from .models import Staff, StaffPermission
from academic.models import TeacherProfile
from users.models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal after user is saved.
    Auto-creates Staff profile if user has staff role.
    """
    staff_roles = [
        'head', 'hm', 'principal', 'vice_principal', 'teacher', 
        'form_teacher', 'subject_teacher', 'accountant', 'secretary',
        'librarian', 'laboratory', 'security', 'cleaner'
    ]
    
    if instance.role in staff_roles:
        # Check if staff profile exists
        if not hasattr(instance, 'staff_profile'):
            try:
                # Auto-create staff profile for staff roles
                with transaction.atomic():
                    staff_profile = Staff.objects.create(
                        user=instance,
                        is_active=True,
                        department='none',  # Default department
                    )
                    
                    # Auto-create staff permissions
                    StaffPermission.objects.get_or_create(staff=staff_profile)
                    
                    logger.info(
                        f"Auto-created staff profile for user {instance.registration_number} "
                        f"(role: {instance.role})"
                    )
            except Exception as e:
                logger.error(
                    f"Error auto-creating staff profile for user {instance.registration_number}: {e}"
                )


@receiver(post_save, sender=Staff)
def staff_post_save(sender, instance, created, **kwargs):
    """
    Signal after staff is saved.
    """
    if created:
        logger.info(
            f"New staff profile created: {instance.staff_id} - {instance.user.get_full_name()}"
        )
        
        # Create default permissions if not exists
        try:
            StaffPermission.objects.get_or_create(staff=instance)
            logger.info(f"Default permissions created for staff {instance.staff_id}")
        except Exception as e:
            logger.error(f"Error creating permissions for staff {instance.staff_id}: {e}")


@receiver(pre_save, sender=Staff)
def staff_pre_save(sender, instance, **kwargs):
    """
    Signal before staff is saved.
    Generates staff ID if not set.
    """
    # Auto-generate staff ID if not set
    if not instance.staff_id:
        import random
        import string
        prefix = "STF"
        while True:
            random_num = ''.join(random.choices(string.digits, k=6))
            staff_id = f"{prefix}{random_num}"
            if not Staff.objects.filter(staff_id=staff_id).exclude(pk=instance.pk).exists():
                instance.staff_id = staff_id
                break
        logger.info(f"Generated staff ID: {instance.staff_id}")


@receiver(post_save, sender=TeacherProfile)
def teacher_profile_post_save(sender, instance, created, **kwargs):
    """
    Signal after teacher profile is saved.
    """
    if created:
        logger.info(
            f"New teacher profile created for staff {instance.staff.staff_id}"
        )
        
        # Ensure staff user has appropriate teacher role
        teaching_roles = [
            'teacher', 'form_teacher', 'subject_teacher',
            'head', 'hm', 'principal', 'vice_principal'
        ]
        
        if instance.staff.user.role not in teaching_roles:
            instance.staff.user.role = 'teacher'
            instance.staff.user.save()
            logger.info(
                f"Updated user {instance.staff.user.id} role to 'teacher'"
            )


@receiver(post_delete, sender=Staff)
def staff_post_delete(sender, instance, **kwargs):
    """
    Signal after staff is deleted.
    Updates user role if necessary.
    """
    logger.info(f"Staff profile deleted: {instance.staff_id}")
    
    try:
        user = instance.user
        
        # Check if user has other staff profiles (shouldn't happen with OneToOneField)
        if not Staff.objects.filter(user=user).exists():
            # Change role back to student if no other profile exists
            user.role = 'student'
            user.save(update_fields=['role'])
            logger.info(
                f"Updated user {user.id} role to 'student' after staff deletion"
            )
    except Exception as e:
        logger.error(f"Error updating user role after staff deletion: {e}")