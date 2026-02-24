"""
Serializers for the User model and related operations.
Converts between Python objects and JSON for API communication.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from .models import User, Activity
from django.utils import timezone


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration - Simple password validation (minimum 5 characters)
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password must be at least 5 characters long"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Enter the same password as above"
    )

    class Meta:
        model = User
        fields = (
            'password', 'password2',
            'first_name', 'last_name', 'role', 'gender',
            'email', 'phone_number', 'date_of_birth', 'address',
            'city', 'state_of_origin', 'lga', 'nationality'
        )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True},
            'email': {'required': False},
        }

    def validate(self, attrs):
        """
        Simple validation - only check passwords match and minimum length.
        """
        # Check passwords match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Simple length check - minimum 5 characters
        if len(attrs['password']) < 5:
            raise serializers.ValidationError({"password": "Password must be at least 5 characters long."})

        # Validate phone number (Nigerian format) - optional
        phone = attrs.get('phone_number', '')
        if phone:
            if not phone.startswith('0') and not phone.startswith('+234'):
                raise serializers.ValidationError(
                    {"phone_number": "Phone number must start with 0 or +234"}
                )

        # Check email doesn't already exist if provided
        email = attrs.get('email')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already exists."})

        # For students, email is optional
        role = attrs.get('role')
        if role != 'student' and not email:
            raise serializers.ValidationError({"email": "Email is required for non-student roles."})

        return attrs

    def create(self, validated_data):
        """
        Create user with hashed password - simple and clean.
        """
        validated_data.pop('password2')
        
        # Ensure user is active and verified
        validated_data['is_active'] = True
        validated_data['is_verified'] = True
        
        user = User.objects.create_user(**validated_data)
        return user


class AdminPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for admin to reset any user's password.
    ONLY accessible by Head of School (head) or Head Master (hm).
    Simple password validation (minimum 5 characters).
    """

    registration_number = serializers.CharField(
        required=True,
        help_text="Enter user's registration number"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Enter new password (minimum 5 characters)"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm new password"
    )

    def validate(self, attrs):
        """
        Simple validation for admin password reset.
        """
        registration_number = attrs.get('registration_number')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        # Check passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"new_password": "Passwords don't match"}
            )

        # Simple length check - minimum 5 characters
        if len(new_password) < 5:
            raise serializers.ValidationError(
                {"new_password": "Password must be at least 5 characters long."}
            )

        # Check if user exists
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"registration_number": "No user found with this registration number"}
            )

        attrs['user'] = user
        return attrs

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login - Uses registration_number only.
    """

    registration_number = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Enter your registration number (e.g., CTS_1234)"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Enter your password"
    )

    def validate(self, attrs):
        """
        Validate login credentials.
        """
        registration_number = attrs.get('registration_number')
        password = attrs.get('password')

        if registration_number and password:
            # Use Django's authenticate with custom backend
            from django.contrib.auth.backends import ModelBackend
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            # First, get the user by registration_number
            try:
                user = User.objects.get(registration_number=registration_number)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {"registration_number": "Invalid registration number or password"}
                )
            
            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError(
                    {"registration_number": "Account is deactivated. Contact administrator."}
                )
            
            # Check password manually since we're using registration_number
            if not user.check_password(password):
                raise serializers.ValidationError({"password": "Invalid registration number or password"})
            
            # Manual authentication
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                {"registration_number": "Both registration number and password are required"}
            )

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """

    role_display = serializers.CharField(source='get_role_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    state_of_origin_display = serializers.CharField(source='get_state_of_origin_display', read_only=True)
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'registration_number', 'email',
            'first_name', 'last_name', 'full_name',
            'role', 'role_display',
            'gender', 'gender_display', 'date_of_birth',
            'phone_number', 'alternative_phone', 'profile_picture',
            'address', 'city', 'state_of_origin', 'state_of_origin_display',
            'lga', 'nationality', 'is_active', 'is_verified',
            'last_login_ip', 'login_count', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'registration_number', 'is_verified', 'last_login_ip',
            'login_count', 'created_at', 'updated_at', 'role_display',
            'gender_display', 'state_of_origin_display', 'full_name'
        )

    def get_full_name(self, obj):
        return obj.get_full_name()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change - Now using email-based password reset for all users.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Enter your registered email address"
    )
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Enter your current password"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Enter new password (min 8 characters)"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm new password"
    )

    def validate(self, attrs):
        """
        Validate password change data.
        """
        email = attrs.get('email')
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        # Check new passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"new_password": "New passwords don't match"}
            )

        # Check old and new password are different
        if old_password == new_password:
            raise serializers.ValidationError(
                {"new_password": "New password cannot be same as old password"}
            )

        # Verify email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No user found with this email address"}
            )

        # Check old password is correct
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Current password is incorrect"})

        attrs['user'] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password request.
    Sends reset link to email.
    """

    email = serializers.EmailField(
        required=True,
        help_text="Enter your registered email address"
    )

    def validate_email(self, value):
        """
        Validate email exists in the system.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No account found with this email address"
            )
        return value


class AdminResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for admin to reset user password.
    Only admin can reset passwords for staff, parents, and students.
    """

    registration_number = serializers.CharField(
        required=True,
        help_text="Enter user's registration number"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Enter new password for user (min 8 characters)"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm new password"
    )

    def validate(self, attrs):
        """
        Validate admin reset password data.
        """
        registration_number = attrs.get('registration_number')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        # Check passwords match
        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"new_password": "Passwords don't match"}
            )

        # Check registration number exists
        try:
            user = User.objects.get(registration_number=registration_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"registration_number": "No user found with this registration number"}
            )

        attrs['user'] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for email-based password reset.
    """
    
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Passwords don't match"})
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (admin only).
    """

    full_name = serializers.SerializerMethodField(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'registration_number', 'email', 'full_name',
            'first_name', 'last_name', 'role', 'role_display',
            'phone_number', 'is_active', 'is_verified',
            'last_login', 'created_at'
        )

    def get_full_name(self, obj):
        return obj.get_full_name()


class UpdateUserRoleSerializer(serializers.Serializer):
    """
    Serializer for updating user role.
    """

    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        help_text="New role for the user"
    )


class TokenSerializer(serializers.Serializer):
    """
    Serializer for JWT tokens.
    """

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserProfileSerializer()
    
    


# Add these serializers AFTER your existing serializers

class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for Activity model"""
    
    user_name = serializers.CharField(read_only=True)
    user_role = serializers.CharField(read_only=True)
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = [
            'id',
            'activity_type',
            'action',
            'description',
            'user',
            'user_name',
            'user_role',
            'target_type',
            'target_id',
            'target_name',
            'is_read',
            'read_at',
            'is_system',
            'created_at',
            'updated_at',
            'time_ago',
            'metadata'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_time_ago(self, obj):
        """Calculate time ago from created_at"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"


class ActivityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating activities"""
    
    class Meta:
        model = Activity
        fields = [
            'activity_type',
            'action',
            'description',
            'target_type',
            'target_id',
            'target_name',
            'metadata'
        ]