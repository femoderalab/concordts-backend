# parents/views.py (Updated with better error handling)
"""
API views for parent management.
Handles parent CRUD, children relationships, and communications.
"""

from rest_framework.exceptions import ValidationError
from users.models import User
from rest_framework import generics, permissions, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.db import transaction
from django.utils import timezone
import logging

from .models import Parent
from .serializers import (
    ParentSerializer, ParentCreateSerializer, ParentListSerializer,
    ParentDashboardSerializer, LinkChildToParentSerializer,
    AcceptDeclarationSerializer, ParentUpdateSerializer,
    PTAManagementSerializer, ParentCommunicationSerializer
)
from .permissions import (
    IsParent, IsAdminOrPrincipal, CanEditParent, CanViewParentInfo,
    CanAddParent, CanViewChildrenInfo, CanManagePTA, CanLinkChild,
    CanAcceptDeclaration
)

logger = logging.getLogger(__name__)


# =====================
# PARENT MANAGEMENT VIEWS
# =====================

class ParentListView(generics.ListAPIView):
    """
    List all parents
    
    GET /api/parents/
    """
    
    serializer_class = ParentListSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewParentInfo]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['parent_type', 'marital_status', 'is_pta_member', 'is_active', 'is_verified']
    search_fields = [
        'user__first_name', 'user__last_name',
        'user__email', 'user__registration_number', 'parent_id', 'occupation', 'employer'
    ]
    ordering_fields = ['user__first_name', 'created_at']
    ordering = ['user__first_name']
    
    def get_queryset(self):
        """Filter parents based on permissions"""
        user = self.request.user
        
        # Admin/Principal/Secretary/Accountant can see all
        if user.role in ['head', 'hm', 'principal', 'vice_principal', 'accountant', 'secretary'] or user.is_staff:
            return Parent.objects.select_related('user', 'spouse').all()
        
        # Teachers can see parents of their students
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            try:
                from students.models import Student
                from academic.models import Class
                
                teaching_classes = Class.objects.filter(
                    Q(class_teacher=user) | Q(assistant_class_teacher=user)
                )
                
                students = Student.objects.filter(
                    class_level__in=teaching_classes.values('class_level')
                )
                
                parent_ids = []
                for student in students:
                    if student.father:
                        parent_ids.append(student.father.id)
                    if student.mother:
                        parent_ids.append(student.mother.id)
                
                return Parent.objects.filter(id__in=parent_ids).distinct().select_related('user', 'spouse')
            except Exception:
                return Parent.objects.none()
        
        # Parents can only see themselves
        if user.role == 'parent':
            try:
                return Parent.objects.filter(user=user).select_related('user', 'spouse')
            except:
                return Parent.objects.none()
        
        return Parent.objects.none()


class ParentCreateView(generics.CreateAPIView):
    """
    Create new parent profile
    
    POST /api/parents/create/
    """
    
    serializer_class = ParentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CanAddParent]
    
    def create(self, request, *args, **kwargs):
        """Create parent with comprehensive validation"""
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate user exists
            user_id = serializer.validated_data.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                
                # Check if user already has parent profile
                if hasattr(user, 'parent_profile'):
                    return Response({
                        'error': 'Duplicate parent profile',
                        'detail': f'User {user.get_full_name()} already has a parent profile.',
                        'existing_parent_id': user.parent_profile.parent_id
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update user role if needed
                if user.role != 'parent':
                    user.role = 'parent'
                    user.save()
                    logger.info(f"Updated user {user.id} role to 'parent'")
                
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found',
                    'detail': f'User with ID {user_id} does not exist.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Create parent
            parent = serializer.save()
            
            logger.info(f"Parent created: {parent.parent_id} by {request.user.registration_number}")
            
            # Return detailed parent info
            full_serializer = ParentSerializer(parent)
            
            return Response({
                'message': 'Parent created successfully',
                'parent': full_serializer.data,
                'parent_id': parent.parent_id,
                'user_id': parent.user.id,
                'registration_number': parent.user.registration_number
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating parent: {str(e)}", exc_info=True)
            return Response({
                'error': 'Parent creation failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ParentDetailView(generics.RetrieveAPIView):
    """
    Get parent details
    
    GET /api/parents/{id}/
    """
    
    serializer_class = ParentSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditParent]
    
    def get_queryset(self):
        return Parent.objects.select_related('user', 'spouse')
    
    def get_object(self):
        """Get parent with permission checks"""
        # If user is parent and no pk provided, return their own profile
        if self.kwargs.get('pk') is None and self.request.user.role == 'parent':
            try:
                return self.request.user.parent_profile
            except Parent.DoesNotExist:
                raise ValidationError("Parent profile not found")
        
        parent = super().get_object()
        self.check_object_permissions(self.request, parent)
        return parent


class ParentUpdateView(generics.UpdateAPIView):
    """
    Update parent profile
    
    PUT/PATCH /api/parents/{id}/update/
    """
    
    permission_classes = [permissions.IsAuthenticated, CanEditParent]
    queryset = Parent.objects.select_related('user')
    
    def get_serializer_class(self):
        """Use different serializer based on user role"""
        if self.request.user.role == 'parent':
            return ParentUpdateSerializer
        return ParentSerializer
    
    def update(self, request, *args, **kwargs):
        """Update parent with permission checks"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check permissions
        self.check_object_permissions(request, instance)
        
        # Parents cannot edit restricted fields
        if request.user.role == 'parent' and instance.user == request.user:
            restricted_fields = [
                'parent_id', 'is_verified', 'user', 'parent_type',
                'pta_position', 'pta_committee', 'is_pta_member',
                'declaration_accepted', 'annual_income_range',
                'spouse', 'is_active'
            ]
            for field in restricted_fields:
                if field in request.data:
                    return Response({
                        'error': f'You cannot modify the {field} field'
                    }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response({
                'error': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        
        logger.info(f"Parent updated: {instance.parent_id} by {request.user.registration_number}")
        
        return Response({
            'message': 'Parent updated successfully',
            'parent': ParentSerializer(instance).data
        })


# =====================
# PARENT DASHBOARD VIEW
# =====================

class ParentDashboardView(APIView):
    """
    Parent dashboard with children and fee summary
    
    GET /api/parents/dashboard/
    """
    
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get(self, request):
        """Get parent dashboard"""
        try:
            parent = request.user.parent_profile
            
            dashboard_data = {
                'parent': parent,
                'children_count': parent.get_children_count(),
                'fee_summary': parent.get_fee_summary(),
                'children_by_class': parent.get_children_by_class(),
                'outstanding_fees': parent.get_outstanding_fees(),
                'documents_complete': parent.has_all_documents_uploaded()
            }
            
            serializer = ParentDashboardSerializer(dashboard_data)
            
            return Response({
                'success': True,
                'dashboard': serializer.data,
                'quick_stats': {
                    'total_children': parent.get_children_count(),
                    'active_children': parent.get_children().filter(is_active=True).count(),
                    'total_fee_due': parent.get_fee_summary().get('total_balance', 0),
                    'pta_member': parent.is_pta_member,
                    'declaration_accepted': parent.declaration_accepted
                }
            })
            
        except Parent.DoesNotExist:
            return Response({
                'error': 'Parent profile not found',
                'detail': 'Please contact administrator to create your parent profile.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in parent dashboard: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to load dashboard',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =====================
# CHILDREN MANAGEMENT VIEW
# =====================

class ParentChildrenView(generics.ListAPIView):
    """
    Get all children of logged-in parent
    
    GET /api/parents/children/
    """
    
    permission_classes = [permissions.IsAuthenticated, IsParent]
    
    def get_serializer_class(self):
        """Dynamically get serializer"""
        try:
            from students.serializers import StudentListSerializer
            return StudentListSerializer
        except ImportError:
            from .serializers import StudentMiniSerializer
            return StudentMiniSerializer
    
    def get_queryset(self):
        """Get parent's children"""
        try:
            parent = self.request.user.parent_profile
            return parent.get_children().order_by('class_level__order')
        except Parent.DoesNotExist:
            return []
        except Exception:
            return []


# =====================
# LINK CHILD TO PARENT VIEW
# =====================

class LinkChildToParentView(APIView):
    """
    Link existing student to parent
    
    POST /api/parents/link-child/
    """
    
    permission_classes = [permissions.IsAuthenticated, CanLinkChild]
    
    def post(self, request):
        """Link student to parent"""
        try:
            serializer = LinkChildToParentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            student_admission = serializer.validated_data['student_admission_number']
            parent_id = serializer.validated_data['parent_id']
            relationship = serializer.validated_data['relationship_type']
            
            # Get student and parent
            from students.models import Student
            
            student = get_object_or_404(Student, admission_number=student_admission)
            parent = get_object_or_404(Parent, parent_id=parent_id)
            
            # Check if relationship already exists
            if relationship == 'father' and student.father == parent:
                return Response({
                    'message': 'Student is already linked to this parent as father'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if relationship == 'mother' and student.mother == parent:
                return Response({
                    'message': 'Student is already linked to this parent as mother'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Link student to parent
                if relationship == 'father':
                    student.father = parent
                else:
                    student.mother = parent
                
                student.save()
            
            logger.info(
                f"Linked student {student.admission_number} to parent {parent.parent_id} "
                f"as {relationship} by {request.user.registration_number}"
            )
            
            # Get serializers
            try:
                from students.serializers import StudentListSerializer
                student_serializer = StudentListSerializer
            except ImportError:
                from .serializers import StudentMiniSerializer
                student_serializer = StudentMiniSerializer
            
            return Response({
                'success': True,
                'message': f'Successfully linked student to parent as {relationship}',
                'student': student_serializer(student).data,
                'parent': ParentSerializer(parent).data
            })
            
        except Exception as e:
            logger.error(f"Error linking child to parent: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to link child to parent',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# =====================
# DECLARATION MANAGEMENT VIEW
# =====================

class AcceptDeclarationView(APIView):
    """
    Accept parent declaration
    
    POST /api/parents/{id}/accept-declaration/
    """
    
    permission_classes = [permissions.IsAuthenticated, CanAcceptDeclaration]
    
    def post(self, request, pk=None):
        """Accept declaration"""
        try:
            if pk:
                parent = get_object_or_404(Parent, pk=pk)
                self.check_object_permissions(request, parent)
            else:
                # Parent accepting their own declaration
                try:
                    parent = request.user.parent_profile
                except Parent.DoesNotExist:
                    return Response({
                        'error': 'Parent profile not found'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = AcceptDeclarationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            signature = serializer.validated_data.get('signature')
            
            with transaction.atomic():
                parent.accept_declaration(signature=signature)
            
            logger.info(
                f"Declaration accepted for parent {parent.parent_id} "
                f"by {request.user.registration_number}"
            )
            
            return Response({
                'success': True,
                'message': 'Declaration accepted successfully',
                'parent': ParentSerializer(parent).data
            })
            
        except Exception as e:
            logger.error(f"Error accepting declaration: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to accept declaration',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# =====================
# PTA MANAGEMENT VIEW
# =====================

class ManagePTAView(APIView):
    """
    Manage PTA membership
    
    POST /api/parents/{id}/manage-pta/
    """
    
    permission_classes = [permissions.IsAuthenticated, CanManagePTA]
    
    def post(self, request, pk):
        """Update PTA membership"""
        try:
            parent = get_object_or_404(Parent, pk=pk)
            
            serializer = PTAManagementSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                parent.is_pta_member = serializer.validated_data['is_pta_member']
                parent.pta_position = serializer.validated_data.get('pta_position', '')
                parent.pta_committee = serializer.validated_data.get('pta_committee', '')
                parent.save()
            
            logger.info(
                f"PTA membership updated for parent {parent.parent_id} "
                f"by {request.user.registration_number}"
            )
            
            return Response({
                'success': True,
                'message': 'PTA membership updated successfully',
                'parent': ParentSerializer(parent).data
            })
            
        except Exception as e:
            logger.error(f"Error managing PTA: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to update PTA membership',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# =====================
# PARENT STATISTICS VIEW
# =====================

class ParentStatisticsView(APIView):
    """
    Get parent statistics
    
    GET /api/parents/statistics/
    """
    
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPrincipal]
    
    def get(self, request):
        """Get comprehensive parent statistics"""
        try:
            total_parents = Parent.objects.count()
            active_parents = Parent.objects.filter(is_active=True).count()
            verified_parents = Parent.objects.filter(is_verified=True).count()
            pta_members = Parent.objects.filter(is_pta_member=True).count()
            
            parents_by_type = list(Parent.objects.values('parent_type').annotate(
                count=Count('id')
            ))
            
            parents_by_marital_status = list(Parent.objects.values('marital_status').annotate(
                count=Count('id')
            ))
            
            # Calculate total children across all parents
            from students.models import Student
            total_children = Student.objects.filter(
                Q(father__isnull=False) | Q(mother__isnull=False)
            ).distinct().count()
            
            avg_children = total_children / total_parents if total_parents > 0 else 0
            
            return Response({
                'success': True,
                'overall': {
                    'total_parents': total_parents,
                    'active_parents': active_parents,
                    'verified_parents': verified_parents,
                    'pta_members': pta_members,
                    'inactive_parents': total_parents - active_parents
                },
                'demographics': {
                    'parents_by_type': parents_by_type,
                    'parents_by_marital_status': parents_by_marital_status
                },
                'children': {
                    'total_children': total_children,
                    'avg_children_per_parent': round(avg_children, 2)
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting parent statistics: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to get statistics',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =====================
# SEARCH VIEW
# =====================

class ParentSearchView(generics.ListAPIView):
    """
    Advanced parent search
    
    GET /api/parents/search/
    """
    
    serializer_class = ParentListSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewParentInfo]
    
    def get_queryset(self):
        """Advanced parent search"""
        try:
            queryset = Parent.objects.select_related('user', 'spouse')
            
            name = self.request.query_params.get('name', '')
            parent_id = self.request.query_params.get('parent_id', '')
            registration_number = self.request.query_params.get('registration_number', '')
            occupation = self.request.query_params.get('occupation', '')
            parent_type = self.request.query_params.get('parent_type', '')
            is_pta_member = self.request.query_params.get('is_pta_member', '')
            is_active = self.request.query_params.get('is_active', '')
            
            if name:
                queryset = queryset.filter(
                    Q(user__first_name__icontains=name) |
                    Q(user__last_name__icontains=name)
                )
            
            if parent_id:
                queryset = queryset.filter(parent_id__icontains=parent_id)
            
            if registration_number:
                queryset = queryset.filter(user__registration_number__icontains=registration_number)
            
            if occupation:
                queryset = queryset.filter(occupation__icontains=occupation)
            
            if parent_type and parent_type != 'all':
                queryset = queryset.filter(parent_type=parent_type)
            
            if is_pta_member:
                queryset = queryset.filter(is_pta_member=(is_pta_member.lower() == 'true'))
            
            if is_active:
                queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
            
            return queryset.order_by('user__first_name')
            
        except Exception:
            return Parent.objects.none()
        
        
        
# parents/views.py - ADD THIS VIEW
class ParentDeleteView(APIView):
    """
    Delete parent
    POST /api/parents/{id}/delete/
    """
    
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPrincipal]
    
    def delete(self, request, pk):
        """Delete parent"""
        try:
            parent = get_object_or_404(Parent, pk=pk)
            
            # Get parent name for response
            parent_name = parent.user.get_full_name()
            
            with transaction.atomic():
                parent.delete()
            
            logger.info(f"Parent deleted: {parent.parent_id} by {request.user.registration_number}")
            
            return Response({
                'success': True,
                'message': f'Parent {parent_name} deleted successfully'
            })
            
        except Exception as e:
            logger.error(f"Error deleting parent: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to delete parent',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)