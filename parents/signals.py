# parents/signals.py
"""
Signals for Parent model.
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
import logging
from .models import Parent
from users.models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Parent)
def parent_post_save(sender, instance, created, **kwargs):
    """
    Signal after parent is saved.
    """
    if created:
        logger.info(f"New parent created: {instance.parent_id} - {instance.user.get_full_name()}")
        
        # Send welcome email/sms if needed
        try:
            # You can add email sending logic here
            # Example: send_welcome_email(instance)
            pass
        except Exception as e:
            logger.error(f"Error sending welcome message for parent {instance.parent_id}: {e}")


@receiver(pre_save, sender=Parent)
def parent_pre_save(sender, instance, **kwargs):
    """
    Signal before parent is saved.
    """
    # Ensure parent ID is set
    if not instance.parent_id:
        import random
        import string
        prefix = "PAR"
        while True:
            random_num = ''.join(random.choices(string.digits, k=6))
            parent_id = f"{prefix}{random_num}"
            if not Parent.objects.filter(parent_id=parent_id).exclude(pk=instance.pk).exists():
                instance.parent_id = parent_id
                break
    
    # Update user role if needed
    if instance.user.role != 'parent':
        instance.user.role = 'parent'
        instance.user.save()


@receiver(post_delete, sender=Parent)
def parent_post_delete(sender, instance, **kwargs):
    """
    Signal after parent is deleted.
    """
    logger.info(f"Parent deleted: {instance.parent_id} - {instance.user.get_full_name()}")
    
    # Update user role back if no longer parent
    try:
        # Check if user has any other parent profiles (shouldn't happen, but just in case)
        if not Parent.objects.filter(user=instance.user).exists():
            # Check if user is also a student or staff
            if not hasattr(instance.user, 'student_profile') and not hasattr(instance.user, 'staff_profile'):
                instance.user.role = 'student'  # Default role
                instance.user.save()
                logger.info(f"Updated user {instance.user.id} role to student after parent deletion")
    except Exception as e:
        logger.error(f"Error updating user role after parent deletion: {e}")


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal after user is saved to ensure role consistency.
    """
    if created and instance.role == 'parent':
        # If new user is created as parent, log it
        logger.info(f"New user created with parent role: {instance.registration_number}")
    
    # Check role consistency
    if instance.role == 'parent' and not hasattr(instance, 'parent_profile'):
        logger.warning(f"User {instance.id} has parent role but no parent profile")
    elif instance.role != 'parent' and hasattr(instance, 'parent_profile'):
        logger.warning(f"User {instance.id} has parent profile but role is {instance.role}")