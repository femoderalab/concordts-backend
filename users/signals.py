"""
Signal handlers for the User model.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import logging

from .models import User

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """
    Signal triggered before saving a User.
    """
    # Ensure email is None instead of empty string if not provided
    if instance.email == '':
        instance.email = None
    
    # Log user updates
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            changes = []
            
            # Track important field changes
            for field in ['first_name', 'last_name', 'email', 'role', 'is_active']:
                old_value = getattr(old_user, field, None)
                new_value = getattr(instance, field, None)
                if old_value != new_value:
                    changes.append(f"{field}: {old_value} -> {new_value}")
            
            if changes:
                logger.info(f"User {instance.registration_number} updated: {', '.join(changes)}")
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal triggered after saving a User.
    Sends welcome email and handles account status.
    """
    if created:
        # New user created
        logger.info(f"New user created: {instance.registration_number} ({instance.role})")
        
        # Send welcome email if email exists
        if instance.email and settings.EMAIL_HOST_USER:
            try:
                subject = f"Welcome to {settings.SCHOOL_NAME} Management System"
                message = f"""
Dear {instance.first_name} {instance.last_name},

Welcome to {settings.SCHOOL_NAME} Management System!

Your registration details:
- Registration Number: {instance.registration_number}
- Role: {instance.get_role_display()}
- Email: {instance.email}

Important:
1. Keep your registration number safe for login
2. Use your email for password resets
3. Contact administration if you need help

Best regards,
{settings.SCHOOL_NAME} Administration
"""
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.email],
                    fail_silently=True,
                )
                logger.info(f"Welcome email sent to {instance.email}")
            except Exception as e:
                logger.error(f"Failed to send welcome email: {str(e)}")
    
    # Handle activation/deactivation
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            if old_user.is_active != instance.is_active:
                action = "activated" if instance.is_active else "deactivated"
                logger.info(f"User {instance.registration_number} {action}")
                
                # Send notification email
                if instance.email and settings.EMAIL_HOST_USER:
                    try:
                        status_text = "activated" if instance.is_active else "deactivated"
                        subject = f"Account {status_text.title()} - {settings.SCHOOL_NAME}"
                        message = f"""
Dear {instance.first_name} {instance.last_name},

Your account has been {status_text} by the school administration.

Account Status: {status_text.title()}
Registration Number: {instance.registration_number}

{'You can now login to the system.' if instance.is_active else 'Your account access has been suspended. Contact administration for assistance.'}

Best regards,
{settings.SCHOOL_NAME} Administration
"""
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [instance.email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send status email: {str(e)}")
        except User.DoesNotExist:
            pass
    
    # Handle verification
    if instance.is_verified and instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            if not old_user.is_verified and instance.is_verified:
                logger.info(f"User {instance.registration_number} verified")
                
                # Send verification email
                if instance.email and settings.EMAIL_HOST_USER:
                    try:
                        subject = f"Account Verified - {settings.SCHOOL_NAME}"
                        message = f"""
Dear {instance.first_name} {instance.last_name},

Your account has been verified by the school administration.

You now have full access to the School Management System.

Registration Number: {instance.registration_number}
Role: {instance.get_role_display()}

Best regards,
{settings.SCHOOL_NAME} Administration
"""
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [instance.email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        logger.error(f"Failed to send verification email: {str(e)}")
        except User.DoesNotExist:
            pass