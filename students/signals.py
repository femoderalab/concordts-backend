"""
Signals for Student models.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Student
from users.models import User
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """
    Create student profile when user with student role is created.
    """
    if created and instance.role == 'student':
        try:
            Student.objects.create(user=instance)
            logger.info(f"Student profile created for user: {instance.registration_number}")
        except Exception as e:
            logger.error(f"Failed to create student profile: {e}")


@receiver(pre_save, sender=Student)
def update_user_role(sender, instance, **kwargs):
    """
    Update user role to student when student profile is created.
    """
    if instance.user.role != 'student':
        instance.user.role = 'student'
        instance.user.save()
        logger.info(f"User role updated to student: {instance.user.registration_number}")


@receiver(pre_save, sender=Student)
def calculate_fee_balance(sender, instance, **kwargs):
    """
    Calculate fee balance before saving.
    """
    # Calculate balance due
    instance.balance_due = instance.total_fee_amount - instance.amount_paid
    
    # Update fee status based on payments
    if instance.total_fee_amount > 0:
        if instance.amount_paid >= instance.total_fee_amount:
            instance.fee_status = 'paid_full'
        elif instance.amount_paid > 0:
            instance.fee_status = 'paid_partial'
        elif instance.fee_status not in ['scholarship', 'exempted']:
            instance.fee_status = 'not_paid'


@receiver(pre_save, sender=Student)
def update_document_flags(sender, instance, **kwargs):
    """
    Update document upload flags before saving.
    """
    instance.birth_certificate_uploaded = bool(instance.birth_certificate)
    instance.student_image_uploaded = bool(instance.student_image)
    instance.immunization_record_uploaded = bool(instance.immunization_record)
    instance.previous_school_report_uploaded = bool(instance.previous_school_report)
    instance.parent_id_copy_uploaded = bool(instance.parent_id_copy)