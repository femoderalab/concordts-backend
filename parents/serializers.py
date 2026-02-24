# parents/serializers.py (Updated with all fixes)
"""
Serializers for the Parent model and related operations.
Converts between Python objects and JSON for API communication.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Parent
from users.models import User  # Direct import from users app


# =====================
# STUDENT MINI SERIALIZER (Avoid Circular Import)
# =====================
class StudentMiniSerializer(serializers.Serializer):
    """Lightweight student serializer to avoid circular imports"""
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    admission_number = serializers.CharField(read_only=True)
    student_id = serializers.CharField(read_only=True)
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    fee_status = serializers.CharField(source='get_fee_status_display', read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_active = serializers.BooleanField(read_only=True)


# =====================
# MAIN PARENT SERIALIZER
# =====================
class ParentSerializer(serializers.ModelSerializer):
    """Main parent serializer with comprehensive data"""
    
    user = serializers.SerializerMethodField(read_only=True)
    children = serializers.SerializerMethodField(read_only=True)
    children_count = serializers.IntegerField(source='get_children_count', read_only=True)
    fee_summary = serializers.SerializerMethodField(read_only=True)
    spouse_info = serializers.SerializerMethodField(read_only=True)
    communication_summary = serializers.SerializerMethodField(read_only=True)
    documents_status = serializers.SerializerMethodField(read_only=True)
    outstanding_fees = serializers.SerializerMethodField(read_only=True)
    
    parent_id = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    parent_type_display = serializers.CharField(source='get_parent_type_display', read_only=True)
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)
    preferred_communication_display = serializers.CharField(
        source='get_preferred_communication_display', 
        read_only=True
    )
    annual_income_range_display = serializers.CharField(
        source='get_annual_income_range_display', 
        read_only=True
    )

    class Meta:
        model = Parent
        fields = '__all__'
        read_only_fields = [
            'id', 'user', 'parent_id', 'is_verified',
            'created_at', 'updated_at', 'children_count',
            'parent_type_display', 'marital_status_display',
            'preferred_communication_display', 'annual_income_range_display',
            'children', 'fee_summary', 'spouse_info', 'communication_summary',
            'documents_status', 'outstanding_fees'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'parent_id': {'read_only': True},
            'is_verified': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_user(self, obj):
        """Get user information"""
        user_data = {
            'id': obj.user.id,
            'full_name': obj.user.get_full_name(),
            'email': obj.user.email,
            'phone_number': obj.user.phone_number,
            'registration_number': obj.user.registration_number,
            'date_of_birth': obj.user.date_of_birth,
            'gender': obj.user.get_gender_display() if obj.user.gender else None,
            'address': obj.user.address,
            'city': obj.user.city,
            'state_of_origin': obj.user.state_of_origin,
            'lga': obj.user.lga,
            'nationality': obj.user.nationality,
            'is_active': obj.user.is_active,
        }
        
        # Handle profile picture safely
        if obj.user.profile_picture and hasattr(obj.user.profile_picture, 'url'):
            user_data['profile_picture'] = obj.user.profile_picture.url
        else:
            user_data['profile_picture'] = None
            
        return user_data

    def get_children(self, obj):
        """Get children information"""
        try:
            children = obj.get_children()
            if children.exists():
                return StudentMiniSerializer(children, many=True).data
        except Exception as e:
            # Log error but don't crash
            print(f"Error getting children: {e}")
        return []

    def get_fee_summary(self, obj):
        """Get comprehensive fee summary"""
        try:
            return obj.get_fee_summary()
        except Exception as e:
            return {
                'error': 'Could not retrieve fee summary',
                'detail': str(e)
            }

    def get_spouse_info(self, obj):
        """Get spouse information if available"""
        if obj.spouse:
            return {
                'id': obj.spouse.id,
                'full_name': obj.spouse.user.get_full_name(),
                'parent_id': obj.spouse.parent_id,
                'parent_type': obj.spouse.get_parent_type_display(),
                'phone': obj.spouse.user.phone_number,
                'email': obj.spouse.user.email,
                'is_active': obj.spouse.is_active
            }
        return None

    def get_communication_summary(self, obj):
        """Get detailed communication summary"""
        try:
            return {
                'preferred_method': obj.get_preferred_communication_display(),
                'email_alerts': obj.receive_email_alerts,
                'sms_alerts': obj.receive_sms_alerts,
                'email': obj.user.email,
                'phone': obj.user.phone_number,
                'office_phone': obj.office_phone
            }
        except Exception as e:
            return {
                'error': 'Could not get communication summary',
                'detail': str(e)
            }

    def get_documents_status(self, obj):
        """Get documents upload status for all children"""
        try:
            has_all_docs = obj.has_all_documents_uploaded()
            children = obj.get_children()
            
            return {
                'all_documents_uploaded': has_all_docs,
                'children_count': children.count(),
                'missing_documents': not has_all_docs
            }
        except Exception as e:
            return {
                'error': 'Could not check documents status',
                'detail': str(e)
            }

    def get_outstanding_fees(self, obj):
        """Get children with outstanding fees"""
        try:
            outstanding = obj.get_outstanding_fees()
            if outstanding.exists():
                return StudentMiniSerializer(outstanding, many=True).data
            return []
        except Exception as e:
            print(f"Error getting outstanding fees: {e}")
            return []


# =====================
# PARENT CREATE SERIALIZER
# =====================
class ParentCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = Parent
        fields = [
            'user_id', 'parent_type', 'occupation', 'employer',
            'employer_address', 'office_phone', 'marital_status',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'preferred_communication',
            'receive_sms_alerts', 'receive_email_alerts',
            'annual_income_range', 'bank_name', 'account_name', 'account_number',
            'is_pta_member', 'pta_position', 'pta_committee',
            'declaration_accepted', 'is_active', 'is_verified'
        ]
    
    def validate_user_id(self, value):
        """
        Validate that user exists
        """
        try:
            user = User.objects.get(id=value)
            
            # Check if user already has a parent profile
            if Parent.objects.filter(user=user).exists():
                raise serializers.ValidationError(
                    f'User {user.get_full_name()} already has a parent profile.'
                )
                
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError(f'User with ID {value} does not exist.')
    
    def create(self, validated_data):
        """
        Create parent instance with proper user role update
        """
        user_id = validated_data.pop('user_id')
        user = User.objects.get(id=user_id)
        
        # Update user role to 'parent' if not already
        if user.role != 'parent':
            user.role = 'parent'
            user.save(update_fields=['role'])
        
        # Create parent with the user
        parent = Parent.objects.create(user=user, **validated_data)
        
        return parent


# =====================
# PARENT LIST SERIALIZER
# =====================
class ParentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for parent lists"""
    
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.phone_number', read_only=True)
    registration_number = serializers.CharField(source='user.registration_number', read_only=True)
    children_count = serializers.IntegerField(source='get_children_count', read_only=True)
    parent_type_display = serializers.CharField(source='get_parent_type_display', read_only=True)
    marital_status_display = serializers.CharField(source='get_marital_status_display', read_only=True)

    class Meta:
        model = Parent
        fields = [
            'id', 'full_name', 'email', 'phone', 'registration_number',
            'parent_id', 'parent_type', 'parent_type_display', 'occupation', 
            'marital_status', 'marital_status_display', 'office_phone',
            'children_count', 'is_pta_member', 'is_active',
            'is_verified', 'created_at'
        ]


# =====================
# PARENT DASHBOARD SERIALIZER
# =====================
class ParentDashboardSerializer(serializers.Serializer):
    """Serializer for parent dashboard data"""
    
    parent = ParentSerializer(read_only=True)
    children_count = serializers.IntegerField(read_only=True)
    fee_summary = serializers.DictField(read_only=True)
    children_by_class = serializers.SerializerMethodField(read_only=True)
    outstanding_fees = serializers.SerializerMethodField(read_only=True)
    documents_complete = serializers.BooleanField(read_only=True)
    
    def get_children_by_class(self, obj):
        """Get children grouped by class"""
        try:
            children_dict = obj.get_children_by_class()
            result = {}
            
            for class_name, students in children_dict.items():
                result[class_name] = StudentMiniSerializer(students, many=True).data
            
            return result
        except Exception:
            return {}
    
    def get_outstanding_fees(self, obj):
        """Get children with outstanding fees"""
        try:
            outstanding = obj.get_outstanding_fees()
            return StudentMiniSerializer(outstanding, many=True).data
        except Exception:
            return []


# =====================
# LINK CHILD SERIALIZER
# =====================
class LinkChildToParentSerializer(serializers.Serializer):
    """Serializer for linking a child to parent"""
    
    student_admission_number = serializers.CharField(
        required=True,
        help_text="Student's admission number"
    )
    parent_id = serializers.CharField(
        required=True,
        help_text="Parent ID"
    )
    relationship_type = serializers.ChoiceField(
        choices=['father', 'mother'],
        required=True,
        help_text="Relationship type (father or mother)"
    )

    def validate_student_admission_number(self, value):
        """Validate student exists"""
        try:
            # Use try-except to avoid circular import
            from students.models import Student
            Student.objects.get(admission_number=value)
        except ImportError:
            # Fallback if students app not available
            pass
        except Exception as e:
            raise serializers.ValidationError("Student not found with this admission number")
        
        return value

    def validate_parent_id(self, value):
        """Validate parent exists"""
        try:
            Parent.objects.get(parent_id=value)
        except Parent.DoesNotExist:
            raise serializers.ValidationError("Parent not found with this ID")
        
        return value


# =====================
# DECLARATION SERIALIZER
# =====================
class AcceptDeclarationSerializer(serializers.Serializer):
    """Serializer for accepting parent declaration"""
    
    declaration_accepted = serializers.BooleanField(
        required=True,
        help_text="I hereby declare that the information provided is true and correct"
    )
    signature = serializers.CharField(
        required=False,
        max_length=200,
        help_text="Digital signature (parent name)"
    )

    def validate_declaration_accepted(self, value):
        """Validate declaration is accepted"""
        if not value:
            raise serializers.ValidationError(
                "You must accept the declaration to proceed"
            )
        return value


# =====================
# PARENT UPDATE SERIALIZER
# =====================
class ParentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating parent profile (with restrictions)"""
    
    class Meta:
        model = Parent
        fields = [
            'occupation',
            'employer',
            'employer_address',
            'office_phone',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'preferred_communication',
            'receive_sms_alerts',
            'receive_email_alerts',
            'annual_income_range',
            'bank_name',
            'account_name',
            'account_number'
        ]

    def validate(self, data):
        """Validate update data"""
        # Validate phone numbers if provided
        office_phone = data.get('office_phone', '')
        if office_phone and not (office_phone.startswith('0') or office_phone.startswith('+234')):
            raise serializers.ValidationError({
                'office_phone': 'Phone number must start with 0 or +234'
            })
        
        return data


# =====================
# PTA MANAGEMENT SERIALIZER
# =====================
class PTAManagementSerializer(serializers.Serializer):
    """Serializer for managing PTA membership"""
    
    is_pta_member = serializers.BooleanField(
        required=True,
        help_text="Is parent a PTA member?"
    )
    pta_position = serializers.CharField(
        required=False,
        max_length=100,
        allow_blank=True,
        help_text="PTA position/role"
    )
    pta_committee = serializers.CharField(
        required=False,
        max_length=100,
        allow_blank=True,
        help_text="PTA committee membership"
    )

    def validate(self, data):
        """Validate PTA data"""
        if data.get('is_pta_member'):
            if not data.get('pta_position') and not data.get('pta_committee'):
                raise serializers.ValidationError(
                    "Please specify PTA position or committee for PTA members"
                )
        
        return data


# =====================
# PARENT COMMUNICATION SERIALIZER
# =====================
class ParentCommunicationSerializer(serializers.Serializer):
    """Serializer for sending communication to parents"""
    
    parent_ids = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of parent IDs to send to (empty for all)"
    )
    subject = serializers.CharField(
        required=True,
        max_length=200,
        help_text="Communication subject"
    )
    message = serializers.CharField(
        required=True,
        help_text="Communication message"
    )
    communication_method = serializers.ChoiceField(
        choices=['email', 'sms', 'both'],
        default='email',
        help_text="Method of communication"
    )
    send_to_all = serializers.BooleanField(
        default=False,
        help_text="Send to all active parents"
    )

    def validate(self, data):
        """Validate communication data"""
        if not data.get('send_to_all') and not data.get('parent_ids'):
            raise serializers.ValidationError(
                "Please specify parent_ids or set send_to_all to true"
            )
        
        return data


# =====================
# PARENT STATISTICS SERIALIZER
# =====================
class ParentStatisticsSerializer(serializers.Serializer):
    """Serializer for parent statistics"""
    
    total_parents = serializers.IntegerField(read_only=True)
    active_parents = serializers.IntegerField(read_only=True)
    verified_parents = serializers.IntegerField(read_only=True)
    pta_members = serializers.IntegerField(read_only=True)
    parents_by_type = serializers.ListField(read_only=True)
    parents_by_marital_status = serializers.ListField(read_only=True)
    total_children = serializers.IntegerField(read_only=True)
    avg_children_per_parent = serializers.FloatField(read_only=True)