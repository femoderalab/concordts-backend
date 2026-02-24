"""
API views for user authentication and management.
"""

from rest_framework.decorators import api_view, permission_classes, action  # <-- ADD action here
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Q, Count, Sum, F
from django.db.models.functions import Coalesce  # <-- ADD this for Coalesce
from django.core.mail import send_mail
from django.conf import settings
import logging
import random
import string

from .models import User, Activity
from .serializers import (
    RegisterSerializer, LoginSerializer, UserProfileSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    AdminResetPasswordSerializer, UserListSerializer,
    ResetPasswordSerializer, UpdateUserRoleSerializer,
    ActivitySerializer, ActivityCreateSerializer
)

# Import permission classes
from .permissions import IsSuperAdmin, IsAdminOrPrincipal, IsTeacherOrAbove, IsStudent, IsParent, CanAddStaff, CanAddStudentParent, CanResetPassword, IsSelfOrAdmin, IsAccountant, IsSecretary

# Set up logger
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    Register a new user (Student, Teacher, Parent, etc.)
    POST /api/auth/register/
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def create(self, request, *args, **kwargs):
        """
        Create new user and log the action.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Log registration
        logger.info(
            f"New user registered: {user.registration_number} "
            f"({user.role}) from IP: {self.get_client_ip(request)}"
        )

        # Generate tokens for auto-login
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'message': 'User registered successfully',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            },
            status=status.HTTP_201_CREATED
        )

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that accepts registration_number only.
    POST /api/auth/login/
    """
    serializer_class = LoginSerializer
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def post(self, request, *args, **kwargs):
        # Use the custom LoginSerializer to validate
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Login validation error: {str(e)}")
            return Response({
                'error': 'Invalid registration number or password',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get the validated user
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Update login stats
        try:
            user.last_login = timezone.now()
            user.last_login_ip = self.get_client_ip(request)
            user.login_count += 1
            user.save(update_fields=['last_login', 'last_login_ip', 'login_count'])
            
            logger.info(f"User logged in: {user.registration_number} from IP: {user.last_login_ip}")
        except Exception as e:
            logger.warning(f"Could not update login stats: {str(e)}")
        
        # Return response in the exact format frontend expects
        return Response({
            'message': 'Login successful',
            'tokens': {
                'access': access_token,
                'refresh': str(refresh)
            },
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    Logout user by blacklisting refresh token.
    POST /api/auth/logout/
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f"User logged out: {request.user.registration_number}")

            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)

class AdminResetPasswordView(APIView):
    """
    Admin reset user password - ONLY for Head of School (head) and Head Master (hm).
    POST /api/auth/admin/reset-password/
    
    Simple password validation - minimum 5 characters.
    """
    
    permission_classes = [IsSuperAdmin]  # Uses your custom permission - only head/hm

    def post(self, request):
        serializer = AdminPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            # Extra safety check - ensure only head/hm can reset
            if request.user.role not in ['head', 'hm'] and not request.user.is_superuser:
                return Response({
                    'error': 'Only Head of School or Head Master can reset passwords'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Prevent head/hm from resetting each other's passwords
            if user.role in ['head', 'hm'] and user != request.user:
                return Response({
                    'error': 'Heads cannot reset each other\'s passwords'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Reset password
            user.set_password(new_password)
            user.save()
            
            # Log the action
            logger.info(f"Admin {request.user.registration_number} ({request.user.role}) reset password for: {user.registration_number}")
            
            # Send email notification if email exists
            if user.email:
                try:
                    send_mail(
                        subject=f"Password Reset by Administrator - {settings.SCHOOL_NAME}",
                        message=f"Hello {user.first_name},\n\nYour password has been reset by the school administrator.\n\nYour new registration number: {user.registration_number}\nYour new password: [The password set by admin]\n\nPlease login and change your password if needed.\n\nBest regards,\n{settings.SCHOOL_NAME} Administration",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    logger.error(f"Failed to send admin reset email: {str(e)}")
            
            return Response({
                'message': f'Password reset successfully for {user.get_full_name()}',
                'user': {
                    'registration_number': user.registration_number,
                    'email': user.email,
                    'role': user.get_role_display()
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update user profile.
    GET /api/auth/profile/ - Get user profile
    PUT /api/auth/profile/ - Update user profile
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# class ChangePasswordView(APIView):
#     """
#     Change password using email verification.
#     POST /api/auth/change-password/
    
#     All users (including admin) must use their email to change password.
#     """
    
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         serializer = ChangePasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data['user']
#             new_password = serializer.validated_data['new_password']
            
#             # Ensure user can only change their own password
#             if user != request.user:
#                 return Response({
#                     'error': 'You can only change your own password'
#                 }, status=status.HTTP_403_FORBIDDEN)
            
#             # Set new password
#             user.set_password(new_password)
#             user.save()
            
#             # Send email notification
#             try:
#                 send_mail(
#                     subject=f"Password Changed - {settings.SCHOOL_NAME}",
#                     message=f"Hello {user.first_name},\n\nYour password has been successfully changed.\n\nIf you did not make this change, please contact the school administrator immediately.\n\nBest regards,\n{settings.SCHOOL_NAME} Administration",
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[user.email],
#                     fail_silently=True,
#                 )
#                 logger.info(f"Password changed email sent to {user.email}")
#             except Exception as e:
#                 logger.error(f"Failed to send password change email: {str(e)}")
            
#             logger.info(f"Password changed for user: {user.registration_number}")
            
#             return Response({
#                 'message': 'Password changed successfully'
#             }, status=status.HTTP_200_OK)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ForgotPasswordView(APIView):
#     """
#     Request password reset via email.
#     POST /api/auth/forgot-password/
    
#     Sends reset link to email.
#     """
    
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             user = User.objects.get(email=email)
            
#             # Generate reset token
#             reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
#             user.reset_token = reset_token
#             user.reset_token_expiry = timezone.now() + timezone.timedelta(hours=24)
#             user.save()
            
#             # Send reset email
#             reset_link = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
            
#             try:
#                 send_mail(
#                     subject=f"Password Reset Request - {settings.SCHOOL_NAME}",
#                     message=f"Hello {user.first_name},\n\nYou requested a password reset. Click the link below to reset your password:\n\n{reset_link}\n\nThis link will expire in 24 hours.\n\nIf you did not request this, please ignore this email.\n\nBest regards,\n{settings.SCHOOL_NAME} Administration",
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[user.email],
#                     fail_silently=True,
#                 )
#                 logger.info(f"Password reset email sent to {user.email}")
#             except Exception as e:
#                 logger.error(f"Failed to send reset email: {str(e)}")
            
#             return Response({
#                 'message': 'Password reset instructions sent to your email',
#                 'note': 'Check your email for the reset link'
#             }, status=status.HTTP_200_OK)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class ResetPasswordView(APIView):
#     """
#     Reset password using token from email.
#     POST /api/auth/reset-password/
#     """
    
#     permission_classes = [AllowAny]
    
#     def post(self, request):
#         serializer = ResetPasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             new_password = serializer.validated_data['new_password']
            
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 return Response({
#                     'error': 'User not found'
#                 }, status=status.HTTP_404_NOT_FOUND)
            
#             # Set new password
#             user.set_password(new_password)
#             user.reset_token = None
#             user.reset_token_expiry = None
#             user.save()
            
#             # Send confirmation email
#             try:
#                 send_mail(
#                     subject=f"Password Reset Successful - {settings.SCHOOL_NAME}",
#                     message=f"Hello {user.first_name},\n\nYour password has been successfully reset.\n\nYou can now login with your new password.\n\nBest regards,\n{settings.SCHOOL_NAME} Administration",
#                     from_email=settings.DEFAULT_FROM_EMAIL,
#                     recipient_list=[user.email],
#                     fail_silently=True,
#                 )
#                 logger.info(f"Password reset confirmation sent to {user.email}")
#             except Exception as e:
#                 logger.error(f"Failed to send confirmation email: {str(e)}")
            
#             logger.info(f"Password reset for user: {user.registration_number}")
            
#             return Response({
#                 'message': 'Password reset successfully'
#             }, status=status.HTTP_200_OK)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UserListView(generics.ListAPIView):
    """
    List all users (Admin only).
    GET /api/auth/users/
    """

    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = User.objects.all()

        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)

        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))

        # Filter by verification status
        is_verified = self.request.query_params.get('is_verified', None)
        if is_verified is not None:
            queryset = queryset.filter(is_verified=(is_verified.lower() == 'true'))

        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(registration_number__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone_number__icontains=search)
            )

        return queryset.order_by('-created_at')


class UserDetailView(generics.RetrieveAPIView):
    """
    Get user details by registration number.
    GET /api/auth/users/{registration_number}/
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'registration_number'
    lookup_url_kwarg = 'registration_number'

    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all users
        if user.role in ['head', 'hm', 'principal', 'vice_principal'] or user.is_staff:
            return User.objects.all()
        
        # Users can only see themselves
        return User.objects.filter(pk=user.pk)


class VerifyUserView(APIView):
    """
    Verify a user (Admin only).
    POST /api/auth/verify/{registration_number}/
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, registration_number):
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        user.is_verified = True
        user.save()

        logger.info(f"User verified by admin: {user.registration_number}")

        return Response({
            'message': f'User {user.get_full_name()} verified successfully',
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)


class DeactivateUserView(APIView):
    """
    Deactivate a user (Admin only).
    POST /api/auth/deactivate/{registration_number}/
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, registration_number):
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Cannot deactivate self
        if user == request.user:
            return Response({
                'error': 'You cannot deactivate your own account'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save()

        logger.info(f"User deactivated by admin: {user.registration_number}")

        return Response({
            'message': f'User {user.get_full_name()} deactivated successfully',
            'user': UserProfileSerializer(user).data
        })


class ActivateUserView(APIView):
    """
    Activate a user (Admin only).
    POST /api/auth/activate/{registration_number}/
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, registration_number):
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save()

        logger.info(f"User activated by admin: {user.registration_number}")

        return Response({
            'message': f'User {user.get_full_name()} activated successfully',
            'user': UserProfileSerializer(user).data
        })


@api_view(['POST'])
@permission_classes([AllowAny])
def check_user_exists(request):
    """
    Check if user exists by registration_number, email, or phone.
    """
    try:
        registration_number = request.data.get('registration_number', '').strip()
        email = request.data.get('email', '').lower().strip()
        phone_number = request.data.get('phone_number', '').strip()
        
        user = None
        exists = False
        
        # First check by registration_number (primary check for login)
        if registration_number:
            exists = User.objects.filter(registration_number=registration_number).exists()
            if exists:
                user = User.objects.filter(registration_number=registration_number).first()
        
        # Then check by email
        elif email:
            exists = User.objects.filter(email__iexact=email).exists()
            if exists:
                user = User.objects.filter(email__iexact=email).first()
        
        # Or check by phone
        elif phone_number:
            exists = User.objects.filter(phone_number=phone_number).exists()
            if exists:
                user = User.objects.filter(phone_number=phone_number).first()
        
        # Check if parent exists
        is_parent = False
        if user and hasattr(user, 'parent_profile'):
            is_parent = True
        
        return Response({
            'exists': exists,
            'is_parent': is_parent,
            'user': UserProfileSerializer(user).data if user else None,
            'message': 'User exists' if exists else 'User not found'
        })
        
    except Exception as e:
        logger.error(f"Check user exists error: {str(e)}")
        return Response({
            'error': 'Server error',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateUserRoleView(APIView):
    """
    Update user role (Admin only).
    POST /api/auth/update-role/{registration_number}/
    """

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, registration_number):
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateUserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_role = serializer.validated_data['role']

        # Cannot change own role if it would remove admin privileges
        if user == request.user and new_role not in ['head', 'hm', 'principal', 'vice_principal']:
            return Response({
                'error': 'You cannot remove your own administrative privileges'
            }, status=status.HTTP_400_BAD_REQUEST)

        old_role = user.role
        user.role = new_role
        user.save()

        logger.info(f"User role updated from {old_role} to {new_role} by {request.user.registration_number}")

        return Response({
            'message': f'User role updated from {old_role} to {new_role}',
            'user': UserProfileSerializer(user).data
        })


# users/views.py - Add this view
class AdminDirectPasswordResetView(APIView):
    """
    Admin reset user password directly without email verification.
    POST /api/auth/admin/direct-reset-password/
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = AdminDirectPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_password = serializer.validated_data['new_password']
            
            # Check if admin is trying to reset another admin's password
            if user.role in ['head', 'hm', 'principal'] and request.user.role not in ['head', 'hm']:
                return Response({
                    'error': 'Only Head of School or Head Master can reset admin passwords'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Reset password
            user.set_password(new_password)
            user.save()
            
            # Send email notification to user
            try:
                send_mail(
                    subject=f"Password Reset by Administrator - {settings.SCHOOL_NAME}",
                    message=f"Hello {user.first_name},\n\nYour password has been reset by the school administrator.\n\nYour new registration number: {user.registration_number}\n\nPlease login with your new password and change it immediately.\n\nBest regards,\n{settings.SCHOOL_NAME} Administration",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email] if user.email else [],
                    fail_silently=True,
                )
                logger.info(f"Admin password reset notification sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send admin reset email: {str(e)}")
            
            logger.info(f"Admin {request.user.registration_number} reset password for: {user.registration_number}")
            
            return Response({
                'message': f'Password reset successfully for {user.get_full_name()}',
                'user': {
                    'registration_number': user.registration_number,
                    'email': user.email,
                    'role': user.get_role_display()
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# class AdminDashboardView(APIView):
#     """
#     Get admin dashboard statistics.
#     GET /api/auth/admin/dashboard/
#     """
    
#     permission_classes = [permissions.IsAdminUser]
    
#     def get(self, request):
#         try:
#             logger.info("AdminDashboardView: Starting statistics collection")
            
#             # ===========================
#             # USER STATISTICS
#             # ===========================
#             from users.models import User
#             from users.serializers import UserProfileSerializer
            
#             total_users = User.objects.all().count()
#             active_users = User.objects.filter(is_active=True).count()
#             verified_users = User.objects.filter(is_verified=True).count()
            
#             logger.info(f"User stats - Total: {total_users}, Active: {active_users}, Verified: {verified_users}")
            
#             # Role counts
#             role_counts = {}
#             for role_code, role_name in User.ROLE_CHOICES:
#                 count = User.objects.filter(role=role_code).count()
#                 role_counts[role_name] = count
            
#             # ===========================
#             # STUDENT STATISTICS
#             # ===========================
#             try:
#                 from students.models import Student
#                 total_students = Student.objects.all().count()
                
#                 # Try different field names for enrollment status
#                 enrolled_students = 0
#                 try:
#                     # Check enrollment_status field
#                     enrolled_students = Student.objects.filter(enrollment_status='enrolled').count()
#                 except Exception as e1:
#                     logger.info(f"enrollment_status field not found: {str(e1)}")
#                     try:
#                         # Check status field
#                         enrolled_students = Student.objects.filter(status='active').count()
#                     except Exception as e2:
#                         logger.info(f"status field not found: {str(e2)}")
#                         try:
#                             # Check is_active field
#                             enrolled_students = Student.objects.filter(is_active=True).count()
#                         except Exception as e3:
#                             logger.info(f"is_active field not found: {str(e3)}")
#                             # Default: count all active students
#                             enrolled_students = Student.objects.filter(user__is_active=True).count()
                
#                 logger.info(f"Student stats - Total: {total_students}, Enrolled: {enrolled_students}")
#             except Exception as e:
#                 logger.error(f"Error getting student statistics: {str(e)}", exc_info=True)
#                 total_students = 0
#                 enrolled_students = 0
            
#             # ===========================
#             # PARENT STATISTICS
#             # ===========================
#             try:
#                 from parents.models import Parent
#                 total_parents = Parent.objects.all().count()
#                 registered_parents = Parent.objects.filter(user__is_active=True).count()
#                 logger.info(f"Parent stats - Total: {total_parents}, Registered: {registered_parents}")
#             except Exception as e:
#                 logger.error(f"Error getting parent statistics: {str(e)}", exc_info=True)
#                 total_parents = 0
#                 registered_parents = 0
            
#             # ===========================
#             # STAFF STATISTICS
#             # ===========================
#             try:
#                 from staff.models import Staff
#                 total_staff = Staff.objects.all().count()
                
#                 # Try to get teaching staff - use user's role instead
#                 teaching_staff = 0
#                 try:
#                     # Filter by user role
#                     teaching_staff = Staff.objects.filter(
#                         user__role__in=['teacher', 'form_teacher', 'subject_teacher']
#                     ).count()
#                 except Exception as e1:
#                     logger.info(f"Error filtering by user role: {str(e1)}")
#                     try:
#                         # Try staff_type field
#                         teaching_staff = Staff.objects.filter(staff_type='teaching').count()
#                     except Exception as e2:
#                         logger.info(f"staff_type field not found: {str(e2)}")
#                         # If no staff_type field, count all staff
#                         teaching_staff = total_staff
                
#                 non_teaching_staff = total_staff - teaching_staff
#                 logger.info(f"Staff stats - Total: {total_staff}, Teaching: {teaching_staff}")
#             except Exception as e:
#                 logger.error(f"Error getting staff statistics: {str(e)}", exc_info=True)
#                 total_staff = 0
#                 teaching_staff = 0
#                 non_teaching_staff = 0
            
#             # ===========================
#             # ACADEMIC STATISTICS - FIXED
#             # ===========================
#             try:
#                 # Try Class model first
#                 try:
#                     from academic.models import Class
#                     total_classes = Class.objects.all().count()
                    
#                     # Try different ways to find active classes
#                     try:
#                         active_classes = Class.objects.filter(is_active=True).count()
#                     except Exception as e:
#                         logger.info(f"is_active field not found: {str(e)}")
#                         try:
#                             active_classes = Class.objects.filter(status='active').count()
#                         except Exception as e:
#                             logger.info(f"status field not found: {str(e)}")
#                             active_classes = total_classes
                
#                 except ImportError:
#                     # Try alternative model names
#                     try:
#                         from academic.models import SchoolClass
#                         total_classes = SchoolClass.objects.all().count()
#                         active_classes = SchoolClass.objects.filter(is_active=True).count()
#                     except ImportError:
#                         try:
#                             from academic.models import ClassLevel
#                             total_classes = ClassLevel.objects.all().count()
#                             active_classes = ClassLevel.objects.filter(is_active=True).count()
#                         except ImportError:
#                             total_classes = 0
#                             active_classes = 0
                
#                 logger.info(f"Class stats - Total: {total_classes}, Active: {active_classes}")
#             except Exception as e:
#                 logger.error(f"Error getting class statistics: {str(e)}", exc_info=True)
#                 total_classes = 0
#                 active_classes = 0
            
#             # ===========================
#             # SUBJECT STATISTICS - FIXED
#             # ===========================
#             try:
#                 from academic.models import Subject
#                 total_subjects = Subject.objects.all().count()
                
#                 # Try different ways to find active subjects
#                 try:
#                     active_subjects = Subject.objects.filter(is_active=True).count()
#                 except Exception as e:
#                     logger.info(f"Subject is_active field not found: {str(e)}")
#                     try:
#                         active_subjects = Subject.objects.filter(status='active').count()
#                     except Exception as e:
#                         logger.info(f"Subject status field not found: {str(e)}")
#                         active_subjects = total_subjects
                
#                 logger.info(f"Subject stats - Total: {total_subjects}, Active: {active_subjects}")
#             except Exception as e:
#                 logger.error(f"Error getting subject statistics: {str(e)}", exc_info=True)
#                 total_subjects = 0
#                 active_subjects = 0
            
#             # ===========================
#             # RESULTS STATISTICS - FIXED
#             # ===========================
#             total_results = 0
#             results_published = 0
#             results_percentage = 0
            
#             try:
#                 # Try different model names for results
#                 try:
#                     from results.models import StudentResult
#                     total_results = StudentResult.objects.all().count()
#                     results_published = StudentResult.objects.filter(is_published=True).count()
#                     logger.info(f"Using StudentResult model - Total: {total_results}, Published: {results_published}")
                
#                 except ImportError:
#                     try:
#                         from results.models import Result
#                         total_results = Result.objects.all().count()
#                         results_published = Result.objects.filter(is_published=True).count()
#                         logger.info(f"Using Result model - Total: {total_results}, Published: {results_published}")
                    
#                     except ImportError:
#                         try:
#                             from results.models import ExamResult
#                             total_results = ExamResult.objects.all().count()
#                             results_published = ExamResult.objects.filter(is_published=True).count()
#                             logger.info(f"Using ExamResult model - Total: {total_results}, Published: {results_published}")
                        
#                         except ImportError:
#                             logger.warning("Could not find any Result model in results.models")
                
#                 # Calculate percentage
#                 if total_results > 0:
#                     results_percentage = round((results_published / total_results * 100), 2)
#                 else:
#                     results_percentage = 0
                    
#                 logger.info(f"Result stats - Total: {total_results}, Published: {results_published}, Percentage: {results_percentage}%")
                
#             except Exception as e:
#                 logger.error(f"Error getting result statistics: {str(e)}", exc_info=True)
            
#             # ===========================
#             # FEE STATISTICS - FIXED
#             # ===========================
#             fee_stats = {
#                 'total_expected': 0,
#                 'total_collected': 0,
#                 'percentage': 0,
#                 'currency': '₦',
#                 'status': {
#                     'fully_paid': 0,
#                     'partial': 0,
#                     'not_paid': 0,
#                     'scholarship': 0,
#                     'exempted': 0,
#                 }
#             }
            
#             try:
#                 from students.models import Student
                
#                 # Get all available fields from Student model
#                 student_fields = [f.name for f in Student._meta.get_fields()]
#                 logger.info(f"Available Student fields: {student_fields}")
                
#                 # Try to find fee-related fields dynamically
#                 fee_expected = 0
#                 fee_paid = 0
                
#                 # Method 1: Check if there's a separate Fee model
#                 try:
#                     from students.models import Fee
#                     # If Fee model exists, calculate from there
#                     fee_totals = Fee.objects.aggregate(
#                         total_expected=Sum('amount_expected'),
#                         total_collected=Sum('amount_paid')
#                     )
#                     fee_expected = fee_totals.get('total_expected') or 0
#                     fee_paid = fee_totals.get('total_collected') or 0
                    
#                     # Get fee status counts
#                     fully_paid = Fee.objects.filter(
#                         amount_paid__gte=F('amount_expected')
#                     ).count()
                    
#                     partial_paid = Fee.objects.filter(
#                         amount_paid__gt=0,
#                         amount_paid__lt=F('amount_expected')
#                     ).count()
                    
#                     not_paid = Fee.objects.filter(
#                         Q(amount_paid=0) | Q(amount_paid__isnull=True)
#                     ).count()
                    
#                     # Check for scholarship/exemption
#                     scholarship_count = Fee.objects.filter(
#                         Q(fee_status='scholarship') | Q(is_scholarship=True)
#                     ).count()
                    
#                     exempted_count = Fee.objects.filter(
#                         Q(fee_status='exempted') | Q(is_exempted=True)
#                     ).count()
                    
#                     fee_stats['status']['fully_paid'] = fully_paid
#                     fee_stats['status']['partial'] = partial_paid
#                     fee_stats['status']['not_paid'] = not_paid
#                     fee_stats['status']['scholarship'] = scholarship_count
#                     fee_stats['status']['exempted'] = exempted_count
                    
#                 except ImportError:
#                     # Method 2: Check for fee fields directly in Student model
#                     fee_fields_found = False
                    
#                     # List of possible fee field names
#                     fee_field_options = [
#                         ('fees_expected', 'fees_paid'),
#                         ('total_fee', 'paid_fee'),
#                         ('fee_amount', 'amount_paid'),
#                         ('expected_fee', 'fee_paid'),
#                         ('annual_fee', 'fee_paid_amount'),
#                     ]
                    
#                     for expected_field, paid_field in fee_field_options:
#                         if expected_field in student_fields and paid_field in student_fields:
#                             try:
#                                 totals = Student.objects.aggregate(
#                                     total_expected=Sum(expected_field),
#                                     total_collected=Sum(paid_field)
#                                 )
#                                 fee_expected = totals.get('total_expected') or 0
#                                 fee_paid = totals.get('total_collected') or 0
                                
#                                 # Calculate payment status
#                                 fully_paid = Student.objects.filter(
#                                     **{f'{paid_field}__gte': F(expected_field)}
#                                 ).count()
                                
#                                 partial_paid = Student.objects.filter(
#                                     **{
#                                         f'{paid_field}__gt': 0,
#                                         f'{paid_field}__lt': F(expected_field)
#                                     }
#                                 ).count()
                                
#                                 not_paid = Student.objects.filter(
#                                     Q(**{paid_field: 0}) | Q(**{f'{paid_field}__isnull': True})
#                                 ).count()
                                
#                                 # Check scholarship fields
#                                 scholarship_fields = ['has_scholarship', 'scholarship', 'is_scholarship']
#                                 exemption_fields = ['fee_exemption', 'is_exempted', 'exempted']
                                
#                                 scholarship_count = 0
#                                 exempted_count = 0
                                
#                                 for field in scholarship_fields:
#                                     if field in student_fields:
#                                         scholarship_count = Student.objects.filter(**{field: True}).count()
#                                         break
                                
#                                 for field in exemption_fields:
#                                     if field in student_fields:
#                                         exempted_count = Student.objects.filter(**{field: True}).count()
#                                         break
                                
#                                 fee_stats['status']['fully_paid'] = fully_paid
#                                 fee_stats['status']['partial'] = partial_paid
#                                 fee_stats['status']['not_paid'] = not_paid
#                                 fee_stats['status']['scholarship'] = scholarship_count
#                                 fee_stats['status']['exempted'] = exempted_count
                                
#                                 fee_fields_found = True
#                                 logger.info(f"Found fee fields: {expected_field}, {paid_field}")
#                                 break
                                
#                             except Exception as e:
#                                 logger.info(f"Error with fee fields {expected_field}/{paid_field}: {str(e)}")
#                                 continue
                    
#                     if not fee_fields_found:
#                         logger.warning("No fee fields found in Student model")
#                         # Try to check if there are any payment-related fields
#                         payment_related_fields = [f for f in student_fields if 'fee' in f.lower() or 'payment' in f.lower() or 'amount' in f.lower()]
#                         logger.info(f"Payment-related fields found: {payment_related_fields}")
                
#                 # Calculate percentage
#                 percentage = 0
#                 if fee_expected > 0:
#                     percentage = round((fee_paid / fee_expected * 100), 2)
                
#                 fee_stats['total_expected'] = float(fee_expected)
#                 fee_stats['total_collected'] = float(fee_paid)
#                 fee_stats['percentage'] = percentage
                
#                 logger.info(f"Fee stats - Expected: {fee_expected}, Collected: {fee_paid}, Percentage: {percentage}%")
                
#             except Exception as e:
#                 logger.error(f"Error getting fee statistics: {str(e)}", exc_info=True)
#                 # Don't fail the entire dashboard if fee stats fail
            
#             # ===========================
#             # ADDITIONAL STATISTICS
#             # ===========================
            
#             # Get session/term statistics
#             current_session = None
#             current_term = None
#             try:
#                 from academic.models import AcademicSession, AcademicTerm
                
#                 current_session = AcademicSession.objects.filter(is_current=True).first()
#                 current_term = AcademicTerm.objects.filter(is_current=True).first()
                
#                 logger.info(f"Current session: {current_session.name if current_session else 'None'}")
#                 logger.info(f"Current term: {current_term.name if current_term else 'None'}")
#             except Exception as e:
#                 logger.error(f"Error getting session/term info: {str(e)}")
            
#             # ===========================
#             # RECENT REGISTRATIONS
#             # ===========================
#             try:
#                 recent_users = User.objects.all().order_by('-created_at')[:10]
#                 recent_users_data = UserProfileSerializer(recent_users, many=True).data
#             except Exception as e:
#                 logger.error(f"Error getting recent registrations: {str(e)}")
#                 recent_users_data = []
            
#             # ===========================
#             # BUILD COMPREHENSIVE RESPONSE
#             # ===========================
#             response_data = {
#                 # User statistics
#                 'total_users': total_users,
#                 'active_users': active_users,
#                 'verified_users': verified_users,
#                 'role_counts': role_counts,
                
#                 # Student statistics
#                 'total_students': total_students,
#                 'enrolled_students': enrolled_students,
#                 'enrollment_percentage': round(
#                     (enrolled_students / total_students * 100) if total_students > 0 else 0,
#                     2
#                 ),
                
#                 # Parent statistics
#                 'total_parents': total_parents,
#                 'registered_parents': registered_parents,
#                 'parent_coverage': round(
#                     (registered_parents / total_students * 100) if total_students > 0 else 0,
#                     2
#                 ),
                
#                 # Staff statistics
#                 'total_staff': total_staff,
#                 'teaching_staff': teaching_staff,
#                 'non_teaching_staff': non_teaching_staff,
#                 'student_teacher_ratio': round(
#                     total_students / teaching_staff if teaching_staff > 0 else 0,
#                     1
#                 ),
                
#                 # Academic statistics
#                 'total_classes': total_classes,
#                 'active_classes': active_classes,
#                 'total_subjects': total_subjects,
#                 'active_subjects': active_subjects,
#                 'average_subjects_per_class': round(
#                     total_subjects / total_classes if total_classes > 0 else 0,
#                     1
#                 ),
                
#                 # Results statistics
#                 'results_published': results_published,
#                 'total_results': total_results,
#                 'results_percentage': results_percentage,
                
#                 # Fee statistics
#                 'fee_collection': fee_stats,
                
#                 # System info
#                 'current_session': current_session.name if current_session else 'Not set',
#                 'current_term': current_term.name if current_term else 'Not set',
#                 'academic_year': current_session.name if current_session else 'Not set',
                
#                 # Recent data
#                 'recent_registrations': recent_users_data,
#                 'timestamp': timezone.now().isoformat(),
                
#                 # Summary statistics
#                 'summary': {
#                     'total_entities': total_users + total_students + total_parents + total_staff,
#                     'active_entities': active_users + enrolled_students + registered_parents + total_staff,
#                     'overall_activity_percentage': round(
#                         ((active_users + enrolled_students + registered_parents + total_staff) / 
#                          (total_users + total_students + total_parents + total_staff) * 100) 
#                         if (total_users + total_students + total_parents + total_staff) > 0 else 0,
#                         2
#                     )
#                 }
#             }
            
#             logger.info(f"AdminDashboardView: Successfully collected all statistics")
#             logger.info(f"Response summary - Users: {total_users}, Students: {total_students}, Parents: {total_parents}, Staff: {total_staff}")
#             logger.info(f"Classes: {total_classes}, Subjects: {total_subjects}, Results: {total_results}, Published: {results_published}")
#             logger.info(f"Fees - Expected: {fee_stats['total_expected']}, Collected: {fee_stats['total_collected']}, Percentage: {fee_stats['percentage']}%")
            
#             return Response(response_data, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             logger.error(f"AdminDashboardView: Critical error - {str(e)}", exc_info=True)
#             return Response({
#                 'error': 'Failed to fetch dashboard statistics',
#                 'detail': str(e),
#                 'total_users': 0,
#                 'total_students': 0,
#                 'total_parents': 0,
#                 'total_staff': 0,
#                 'total_classes': 0,
#                 'total_subjects': 0,
#                 'results_published': 0,
#                 'fee_collection': {
#                     'total_expected': 0,
#                     'total_collected': 0,
#                     'percentage': 0,
#                     'currency': '₦',
#                     'status': {
#                         'fully_paid': 0,
#                         'partial': 0,
#                         'not_paid': 0,
#                         'scholarship': 0,
#                         'exempted': 0,
#                     }
#                 }
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdminDashboardView(APIView):
    """
    Get admin dashboard statistics.
    GET /api/auth/admin/dashboard/
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        try:
            logger.info("AdminDashboardView: Starting statistics collection")
            
            # ===========================
            # USER STATISTICS
            # ===========================
            from users.models import User
            from users.serializers import UserProfileSerializer
            
            total_users = User.objects.all().count()
            active_users = User.objects.filter(is_active=True).count()
            verified_users = User.objects.filter(is_verified=True).count()
            
            logger.info(f"User stats - Total: {total_users}, Active: {active_users}, Verified: {verified_users}")
            
            # Role counts
            role_counts = {}
            for role_code, role_name in User.ROLE_CHOICES:
                count = User.objects.filter(role=role_code).count()
                role_counts[role_name] = count
            
            # ===========================
            # STUDENT STATISTICS
            # ===========================
            try:
                from students.models import Student
                total_students = Student.objects.all().count()
                
                # Try different field names for enrollment status
                enrolled_students = 0
                # First try: check if student has an active user
                enrolled_students = Student.objects.filter(user__is_active=True).count()
                
                # Alternative: check student's own active field
                try:
                    enrolled_students = Student.objects.filter(is_active=True).count()
                except:
                    pass
                
                # Alternative: check status field
                try:
                    enrolled_students = Student.objects.filter(status='active').count()
                except:
                    pass
                
                # Alternative: check enrollment_status field
                try:
                    enrolled_students = Student.objects.filter(enrollment_status='enrolled').count()
                except:
                    pass
                
                logger.info(f"Student stats - Total: {total_students}, Enrolled: {enrolled_students}")
            except Exception as e:
                logger.error(f"Error getting student statistics: {str(e)}", exc_info=True)
                total_students = 0
                enrolled_students = 0
            
            # ===========================
            # PARENT STATISTICS
            # ===========================
            try:
                from parents.models import Parent
                total_parents = Parent.objects.all().count()
                registered_parents = Parent.objects.filter(user__is_active=True).count()
                logger.info(f"Parent stats - Total: {total_parents}, Registered: {registered_parents}")
            except Exception as e:
                logger.error(f"Error getting parent statistics: {str(e)}", exc_info=True)
                total_parents = 0
                registered_parents = 0
            
            # ===========================
            # STAFF STATISTICS
            # ===========================
            try:
                from staff.models import Staff
                total_staff = Staff.objects.all().count()
                
                # Try to get teaching staff based on user role
                teaching_staff = 0
                
                # Method 1: Filter by user role
                teaching_staff = Staff.objects.filter(
                    user__role__in=['teacher', 'form_teacher', 'subject_teacher']
                ).count()
                
                # If that returns 0, try alternative method
                if teaching_staff == 0:
                    try:
                        teaching_staff = Staff.objects.filter(staff_type='teaching').count()
                    except:
                        pass
                
                non_teaching_staff = total_staff - teaching_staff
                logger.info(f"Staff stats - Total: {total_staff}, Teaching: {teaching_staff}")
            except Exception as e:
                logger.error(f"Error getting staff statistics: {str(e)}", exc_info=True)
                total_staff = 0
                teaching_staff = 0
                non_teaching_staff = 0
            
            # ===========================
            # CLASSES STATISTICS - USING YOUR ACADEMIC MODELS
            # ===========================
            total_classes = 0
            active_classes = 0
            
            try:
                # Try to import Class from academic.models
                try:
                    from academic.models import Class
                    total_classes = Class.objects.all().count()
                    
                    # Try to find active classes
                    try:
                        active_classes = Class.objects.filter(is_active=True).count()
                    except:
                        try:
                            active_classes = Class.objects.filter(status='active').count()
                        except:
                            active_classes = total_classes
                
                except ImportError:
                    # If Class doesn't exist, try SchoolClass
                    try:
                        from academic.models import SchoolClass
                        total_classes = SchoolClass.objects.all().count()
                        active_classes = SchoolClass.objects.filter(is_active=True).count()
                    except ImportError:
                        pass
                
                logger.info(f"Class stats - Total: {total_classes}, Active: {active_classes}")
            except Exception as e:
                logger.error(f"Error getting class statistics: {str(e)}", exc_info=True)
            
            # ===========================
            # SUBJECTS STATISTICS - USING YOUR ACADEMIC MODELS
            # ===========================
            total_subjects = 0
            active_subjects = 0
            
            try:
                # Import Subject from academic.models
                from academic.models import Subject
                total_subjects = Subject.objects.all().count()
                
                # Try to find active subjects
                try:
                    active_subjects = Subject.objects.filter(is_active=True).count()
                except:
                    try:
                        active_subjects = Subject.objects.filter(status='active').count()
                    except:
                        active_subjects = total_subjects
                
                logger.info(f"Subject stats - Total: {total_subjects}, Active: {active_subjects}")
            except Exception as e:
                logger.error(f"Error getting subject statistics: {str(e)}", exc_info=True)
            
            # ===========================
            # RESULTS STATISTICS - USING YOUR RESULTS MODELS
            # ===========================
            total_results = 0
            results_published = 0
            results_percentage = 0
            
            try:
                # Try to import from results.models
                from results.models import StudentResult
                total_results = StudentResult.objects.all().count()
                results_published = StudentResult.objects.filter(is_published=True).count()
                
                results_percentage = round(
                    (results_published / total_results * 100) if total_results > 0 else 0, 
                    2
                )
                logger.info(f"Result stats - Total: {total_results}, Published: {results_published}")
                
            except ImportError:
                # Try alternative names
                try:
                    from results.models import Result
                    total_results = Result.objects.all().count()
                    results_published = Result.objects.filter(is_published=True).count()
                    
                    results_percentage = round(
                        (results_published / total_results * 100) if total_results > 0 else 0, 
                        2
                    )
                    logger.info(f"Result stats (Result model) - Total: {total_results}, Published: {results_published}")
                    
                except ImportError:
                    try:
                        from results.models import ExamResult
                        total_results = ExamResult.objects.all().count()
                        results_published = ExamResult.objects.filter(is_published=True).count()
                        
                        results_percentage = round(
                            (results_published / total_results * 100) if total_results > 0 else 0, 
                            2
                        )
                        logger.info(f"Result stats (ExamResult model) - Total: {total_results}, Published: {results_published}")
                        
                    except ImportError:
                        logger.warning("Could not find Result model in results.models")
            
            # ===========================
            # FEE STATISTICS - CHECKING STUDENT MODEL
            # ===========================
            fee_stats = {
                'total_expected': 0,
                'total_collected': 0,
                'percentage': 0,
                'currency': '₦',
                'status': {
                    'fully_paid': 0,
                    'partial': 0,
                    'not_paid': 0,
                    'scholarship': 0,
                    'exempted': 0,
                }
            }
            
            try:
                from students.models import Student
                
                # Check what fields exist in Student model
                student_fields = [f.name for f in Student._meta.get_fields()]
                logger.info(f"Available Student fields: {', '.join(student_fields)}")
                
                # Look for fee-related fields
                fee_field_names = {
                    'expected': ['fees_expected', 'total_fee', 'fee_amount', 'expected_fee', 'annual_fee'],
                    'paid': ['fees_paid', 'paid_amount', 'amount_paid', 'fee_paid', 'paid_fee']
                }
                
                # Find which fee fields exist
                expected_field = None
                paid_field = None
                
                for field in fee_field_names['expected']:
                    if field in student_fields:
                        expected_field = field
                        break
                
                for field in fee_field_names['paid']:
                    if field in student_fields:
                        paid_field = field
                        break
                
                logger.info(f"Found fee fields - Expected: {expected_field}, Paid: {paid_field}")
                
                if expected_field and paid_field:
                    # Calculate totals
                    total_expected = Student.objects.aggregate(
                        total=Sum(expected_field)
                    )['total'] or 0
                    
                    total_collected = Student.objects.aggregate(
                        total=Sum(paid_field)
                    )['total'] or 0
                    
                    # Calculate payment status counts
                    try:
                        # Fully paid: paid >= expected
                        fully_paid = Student.objects.annotate(
                            paid_value=Coalesce(F(paid_field), 0),
                            expected_value=Coalesce(F(expected_field), 0)
                        ).filter(paid_value__gte=F('expected_value')).count()
                        
                        # Partial paid: paid > 0 and paid < expected
                        partial_paid = Student.objects.annotate(
                            paid_value=Coalesce(F(paid_field), 0),
                            expected_value=Coalesce(F(expected_field), 0)
                        ).filter(
                            paid_value__gt=0,
                            paid_value__lt=F('expected_value')
                        ).count()
                        
                        # Not paid: paid = 0 or null
                        not_paid = Student.objects.annotate(
                            paid_value=Coalesce(F(paid_field), 0)
                        ).filter(Q(paid_value=0) | Q(**{paid_field: None})).count()
                        
                        # Check for scholarship fields
                        scholarship_count = 0
                        scholarship_fields = ['has_scholarship', 'scholarship', 'is_scholarship']
                        for field_name in scholarship_fields:
                            if field_name in student_fields:
                                scholarship_count = Student.objects.filter(**{field_name: True}).count()
                                break
                        
                        # Check for exemption fields
                        exempted_count = 0
                        exemption_fields = ['fee_exemption', 'is_exempted', 'exempted']
                        for field_name in exemption_fields:
                            if field_name in student_fields:
                                exempted_count = Student.objects.filter(**{field_name: True}).count()
                                break
                        
                        fee_stats['status']['fully_paid'] = fully_paid
                        fee_stats['status']['partial'] = partial_paid
                        fee_stats['status']['not_paid'] = not_paid
                        fee_stats['status']['scholarship'] = scholarship_count
                        fee_stats['status']['exempted'] = exempted_count
                        
                    except Exception as calc_error:
                        logger.error(f"Error calculating fee statuses: {str(calc_error)}")
                        # Set defaults if calculation fails
                        fee_stats['status']['not_paid'] = total_students
                    
                    # Calculate percentage
                    percentage = 0
                    if total_expected > 0:
                        percentage = round((total_collected / total_expected * 100), 2)
                    
                    fee_stats['total_expected'] = float(total_expected)
                    fee_stats['total_collected'] = float(total_collected)
                    fee_stats['percentage'] = percentage
                    
                    logger.info(f"Fee stats - Expected: {total_expected}, Collected: {total_collected}, Percentage: {percentage}%")
                else:
                    logger.warning(f"No matching fee fields found in Student model")
                    # Set not_paid to total students as default
                    fee_stats['status']['not_paid'] = total_students
                    
            except Exception as e:
                logger.error(f"Error getting fee statistics: {str(e)}", exc_info=True)
                # Set not_paid to total students as default
                fee_stats['status']['not_paid'] = total_students
            
            # ===========================
            # ACADEMIC SESSION AND TERM
            # ===========================
            current_session_name = "Not set"
            current_term_name = "Not set"
            
            try:
                from academic.models import AcademicSession, AcademicTerm
                
                current_session = AcademicSession.objects.filter(is_current=True).first()
                current_term = AcademicTerm.objects.filter(is_current=True).first()
                
                current_session_name = current_session.name if current_session else "Not set"
                current_term_name = current_term.name if current_term else "Not set"
                
                logger.info(f"Current session: {current_session_name}, Current term: {current_term_name}")
            except Exception as e:
                logger.error(f"Error getting academic session/term: {str(e)}")
            
            # ===========================
            # RECENT REGISTRATIONS
            # ===========================
            try:
                recent_users = User.objects.all().order_by('-created_at')[:10]
                recent_users_data = UserProfileSerializer(recent_users, many=True).data
            except Exception as e:
                logger.error(f"Error getting recent registrations: {str(e)}")
                recent_users_data = []
            
            # ===========================
            # BUILD RESPONSE
            # ===========================
            response_data = {
                # User statistics
                'total_users': total_users,
                'active_users': active_users,
                'verified_users': verified_users,
                'role_counts': role_counts,
                
                # Student statistics
                'total_students': total_students,
                'enrolled_students': enrolled_students,
                'enrollment_percentage': round(
                    (enrolled_students / total_students * 100) if total_students > 0 else 0,
                    2
                ),
                
                # Parent statistics
                'total_parents': total_parents,
                'registered_parents': registered_parents,
                
                # Staff statistics
                'total_staff': total_staff,
                'teaching_staff': teaching_staff,
                'non_teaching_staff': non_teaching_staff,
                
                # Academic statistics
                'total_classes': total_classes,
                'active_classes': active_classes,
                'total_subjects': total_subjects,
                'active_subjects': active_subjects,
                
                # Results statistics
                'results_published': results_published,
                'total_results': total_results,
                'results_percentage': results_percentage,
                
                # Fee statistics
                'fee_collection': fee_stats,
                
                # Academic info
                'current_session': current_session_name,
                'current_term': current_term_name,
                
                # Recent data
                'recent_registrations': recent_users_data,
                'timestamp': timezone.now().isoformat()
            }
            
            # Add some summary calculations
            response_data['student_teacher_ratio'] = round(
                total_students / teaching_staff if teaching_staff > 0 else 0,
                1
            )
            
            response_data['parent_coverage'] = round(
                (registered_parents / total_students * 100) if total_students > 0 else 0,
                2
            )
            
            logger.info(f"AdminDashboardView: Successfully collected all statistics")
            logger.info(f"Response summary - Users: {total_users}, Students: {total_students}, Parents: {total_parents}, Staff: {total_staff}")
            logger.info(f"Classes: {total_classes}, Subjects: {total_subjects}, Results: {total_results}, Published: {results_published}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"AdminDashboardView: Critical error - {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to fetch dashboard statistics',
                'detail': str(e),
                'total_users': 0,
                'total_students': 0,
                'total_parents': 0,
                'total_staff': 0,
                'total_classes': 0,
                'total_subjects': 0,
                'results_published': 0,
                'fee_collection': {
                    'total_expected': 0,
                    'total_collected': 0,
                    'percentage': 0,
                    'currency': '₦',
                    'status': {
                        'fully_paid': 0,
                        'partial': 0,
                        'not_paid': 0,
                        'scholarship': 0,
                        'exempted': 0,
                    }
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActivityPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ActivityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing activities
    """
    
    queryset = Activity.objects.all().order_by('-created_at')
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ActivityPagination
    
    def get_queryset(self):
        """Filter activities based on user role and permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all activities
        if user.role in ['head', 'hm', 'principal', 'vice_principal'] or user.is_staff:
            return queryset
        
        # Teachers see activities related to their classes
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            return queryset.filter(
                Q(user=user) | 
                Q(activity_type__in=['student_created', 'student_updated', 'result_published']) |
                Q(is_system=True)
            )
        
        # Parents see activities related to their children
        if user.role == 'parent':
            try:
                from students.models import Student
                from parents.models import Parent
                
                parent_profile = Parent.objects.get(user=user)
                children = Student.objects.filter(
                    Q(father=parent_profile) | Q(mother=parent_profile)
                )
                
                # Get child user IDs
                child_user_ids = [child.user.id for child in children if child.user]
                
                return queryset.filter(
                    Q(user__in=child_user_ids) |
                    Q(activity_type='result_published', target_id__in=[str(child.id) for child in children]) |
                    Q(activity_type='announcement') |
                    Q(is_system=True)
                )
            except Exception as e:
                print(f"Error filtering parent activities: {e}")
                return queryset.filter(
                    Q(activity_type='announcement') |
                    Q(is_system=True)
                )
        
        # Students see only their own activities
        if user.role == 'student':
            return queryset.filter(
                Q(user=user) |
                Q(activity_type='result_published', target_id=str(user.id)) |
                Q(activity_type='announcement') |
                Q(is_system=True)
            )
        
        return queryset.none()
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent activities"""
        limit = int(request.query_params.get('limit', 10))
        activity_type = request.query_params.get('activity_type')
        
        queryset = self.get_queryset()
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        activities = queryset[:limit]
        serializer = self.get_serializer(activities, many=True)
        
        return Response({
            'count': activities.count(),
            'activities': serializer.data,
            'timestamp': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def user_activities(self, request):
        """Get activities for current user"""
        user_id = request.query_params.get('user_id', request.user.id)
        limit = int(request.query_params.get('limit', 10))
        
        queryset = self.get_queryset().filter(user_id=user_id)[:limit]
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'count': queryset.count(),
            'activities': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark activity as read"""
        activity = self.get_object()
        
        # Check if user can mark this activity as read
        if not self._can_mark_read(request.user, activity):
            return Response(
                {'error': 'Not authorized to mark this activity as read'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        activity.mark_as_read()
        
        return Response({
            'message': 'Activity marked as read',
            'activity_id': activity.id,
            'read_at': activity.read_at
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all activities as read for current user"""
        user = request.user
        activities = self.get_queryset().filter(is_read=False)
        
        updated_count = activities.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'{updated_count} activities marked as read',
            'user_id': user.id,
            'marked_at': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread activities"""
        unread_count = self.get_queryset().filter(is_read=False).count()
        
        return Response({
            'count': unread_count,
            'user_id': request.user.id,
            'timestamp': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get activity statistics"""
        from django.db.models import Count
        
        total_activities = self.get_queryset().count()
        today_activities = self.get_queryset().filter(
            created_at__date=timezone.now().date()
        ).count()
        
        user_activities = self.get_queryset().filter(is_system=False).count()
        system_activities = self.get_queryset().filter(is_system=True).count()
        
        # Group by activity type
        activity_types = self.get_queryset().values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_activities': total_activities,
            'today_activities': today_activities,
            'user_activities': user_activities,
            'system_activities': system_activities,
            'by_type': list(activity_types),
            'timestamp': timezone.now().isoformat()
        })
    
    def _can_mark_read(self, user, activity):
        """Check if user can mark activity as read"""
        if user.role in ['head', 'hm', 'principal', 'vice_principal'] or user.is_staff:
            return True
        
        if activity.user == user:
            return True
        
        if user.role == 'parent' and activity.user:
            try:
                from parents.models import Parent
                from students.models import Student
                
                parent_profile = Parent.objects.get(user=user)
                children = Student.objects.filter(
                    Q(father=parent_profile) | Q(mother=parent_profile)
                )
                child_users = [child.user for child in children if child.user]
                return activity.user in child_users
            except:
                return False
        
        return False


class LogActivityView(generics.CreateAPIView):
    """
    View for logging new activities
    """
    
    serializer_class = ActivityCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Log a new activity"""
        data = request.data.copy()
        data['user'] = request.user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        activity = serializer.save()
        
        logger.info(f"Activity logged: {activity.activity_type} by {request.user.username}")
        
        return Response(
            ActivitySerializer(activity).data,
            status=status.HTTP_201_CREATED
        )