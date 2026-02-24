
"""
API views for staff management.
Handles staff CRUD, teacher profiles, permissions, and staff operations.
"""

from rest_framework import generics, permissions, status, filters, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.db import transaction
from django.utils import timezone
import logging
from django.db import models
from .models import Staff, StaffPermission
from academic.models import TeacherProfile
from datetime import datetime, date

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model


from .serializers import (
    StaffSerializer, StaffCreateSerializer, StaffListSerializer,
    StaffDetailSerializer, StaffDashboardSerializer, TeacherProfileSerializer,
    TeacherProfileCreateSerializer, StaffUpdateSerializer,
    StaffPermissionSerializer, StaffPermissionUpdateSerializer,
    StaffActivationSerializer, StaffRetirementSerializer,
    StaffSalaryUpdateSerializer, StaffSearchSerializer,
    BulkStaffCreateSerializer, StaffPasswordUpdateSerializer
)
from rest_framework.pagination import PageNumberPagination  
from .permissions import (
    IsAdminOrPrincipal, CanManageStaff, CanViewStaffDetails,
    CanEditStaffProfile, CanManageTeacherProfile, CanManagePermissions,
    IsTeachingStaff, IsNonTeachingStaff, CanViewSalaryInfo,
    CanManageLeave, CanViewAllStaff, CanManageTeacherAssignments,
    CanAccessStaffDashboard, CanManageStaffDocuments,
    CanViewStaffStatistics, CanActivateDeactivateStaff,
    CanRetireStaff
)
from users.models import User

logger = logging.getLogger(__name__)

# =====================
# CUSTOM PAGINATION
# =====================

class StaffPagination(PageNumberPagination):
    """Custom pagination for staff listings"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

# =====================
# STAFF VIEWSET (Comprehensive CRUD)
# =====================

class StaffViewSet(viewsets.ModelViewSet):
    """
    ============================================================================
    COMPREHENSIVE STAFF VIEWSET - ALL CRUD OPERATIONS
    ============================================================================
    
    Handles all staff management operations:
    - List staff with pagination, filtering, and search
    - Retrieve individual staff details
    - Create new staff profiles
    - Update staff information (partial and full)
    - Delete staff records
    - Password management
    - File management (upload/delete)
    - Statistics and reporting
    
    IMPORTANT: Using ModelViewSet instead of ViewSet
    This provides built-in: list, create, retrieve, update, partial_update, destroy
    
    Endpoints:
    - GET    /api/staff/                          - List all staff
    - POST   /api/staff/                          - Create new staff
    - GET    /api/staff/<id>/                     - Get staff details
    - PUT    /api/staff/<id>/                     - Full update
    - PATCH  /api/staff/<id>/                     - Partial update
    - DELETE /api/staff/<id>/                     - Delete staff
    - POST   /api/staff/<id>/update-password/     - Update password
    - DELETE /api/staff/<id>/delete-file/         - Delete file
    - GET    /api/staff/stats/                    - Get statistics
    - POST   /api/staff/bulk-create/              - Bulk create staff
    
    Authentication: Required (IsAuthenticated)
    Permissions: CanManageStaff
    Pagination: StaffPagination (10 items per page)
    """
    
    # =====================
    # CLASS ATTRIBUTES
    # =====================
    queryset = Staff.objects.select_related('user').prefetch_related(
        'teacher_profile',
        'permissions'
    ).order_by('-created_at')
    
    serializer_class = StaffDetailSerializer
    # permission_classes = [permissions.IsAuthenticated, CanManageStaff]  # FIX: This is correct
    pagination_class = StaffPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'staff_id', 'user__email']
    ordering_fields = ['created_at', 'user__first_name', 'staff_id']
    
    # HTTP methods allowed
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    
    
    # =====================
    # HELPER METHODS
    # =====================
    
    def get_serializer_context(self):
        """
        Get serializer context with request object.
        Used by all serializers to access request in methods.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg
        }
    
    
    def get_queryset(self):
        """
        Get base queryset with filtering, searching, and ordering.
        
        Supports:
        - Filtering by: department, employment_type, is_active, is_on_leave
        - Search by: name, email, staff_id, phone, position_title
        - Ordering by: creation date (most recent first)
        
        Returns:
            QuerySet: Filtered and ordered Staff objects with user data
        """
        queryset = Staff.objects.select_related(
            'user'
        ).prefetch_related(
            'teacher_profile',
            'permissions'
        ).order_by('-created_at')
        
        # =====================
        # APPLY FILTERS
        # =====================
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department and department != 'all':
            logger.info(f"🔍 Filter by department: {department}")
            queryset = queryset.filter(department=department)
        
        # Filter by employment type
        employment_type = self.request.query_params.get('employment_type')
        if employment_type and employment_type != 'all':
            logger.info(f"🔍 Filter by employment_type: {employment_type}")
            queryset = queryset.filter(employment_type=employment_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None and is_active != 'all':
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            logger.info(f"🔍 Filter by is_active: {is_active_bool}")
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Filter by leave status
        is_on_leave = self.request.query_params.get('is_on_leave')
        if is_on_leave is not None and is_on_leave != 'all':
            is_on_leave_bool = is_on_leave.lower() in ['true', '1', 'yes']
            logger.info(f"🔍 Filter by is_on_leave: {is_on_leave_bool}")
            queryset = queryset.filter(is_on_leave=is_on_leave_bool)
        
        # Filter by probation status
        is_on_probation = self.request.query_params.get('is_on_probation')
        if is_on_probation is not None and is_on_probation != 'all':
            is_on_probation_bool = is_on_probation.lower() in ['true', '1', 'yes']
            logger.info(f"🔍 Filter by is_on_probation: {is_on_probation_bool}")
            queryset = queryset.filter(is_on_probation=is_on_probation_bool)
        
        # =====================
        # APPLY SEARCH
        # =====================
        
        search = self.request.query_params.get('search')
        if search and search.strip():
            logger.info(f"🔍 Search query: {search}")
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(staff_id__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__phone_number__icontains=search) |
                Q(user__registration_number__icontains=search) |
                Q(position_title__icontains=search) |
                Q(department__icontains=search)
            )
        
        logger.info(f"📋 Final queryset count: {queryset.count()}")
        return queryset
    
    
    def get_serializer_class(self):
        """
        Return different serializers based on action
        """
        if self.action == 'list':
            return StaffListSerializer
        elif self.action == 'retrieve':
            return StaffDetailSerializer
        return StaffDetailSerializer
    
    
    # =====================
    # OVERRIDE BUILT-IN METHODS
    # =====================
    
    def list(self, request, *args, **kwargs):
        """
        List all staff with pagination, filtering, and search.
        
        Query Parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 10, max: 100)
        - search: Search term (name, email, staff_id, etc.)
        - department: Filter by department
        - employment_type: Filter by employment type
        - is_active: Filter by active status (true/false)
        - is_on_leave: Filter by leave status (true/false)
        
        Returns:
            Response: Paginated list of staff with success status
        """
        try:
            logger.info(f"📋 LISTING STAFF")
            logger.info(f"👤 Request user: {request.user.username}")
            logger.info(f"🔗 Query params: {dict(request.query_params)}")
            
            # Get filtered queryset
            queryset = self.get_queryset()
            
            logger.info(f"📊 Total staff matching filters: {queryset.count()}")
            
            # =====================
            # PAGINATION
            # =====================
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                logger.info(f"📄 Page returned with {len(page)} items")
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"✅ Staff list returned - Total: {queryset.count()}")
            
            return Response({
                'success': True,
                'count': queryset.count(),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error listing staff: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to load staff list',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve individual staff details by ID.
        
        URL Parameters:
        - pk: Staff ID (required)
        
        Returns:
            Response: Complete staff details with user information
        """
        try:
            logger.info(f"👤 RETRIEVING STAFF {kwargs.get('pk')}")
            
            instance = self.get_object()
            
            logger.info(f"✓ Found staff: {instance.staff_id} - {instance.user.email}")
            
            serializer = self.get_serializer(instance)
            
            logger.info(f"✅ Staff details retrieved")
            
            return Response({
                'success': True,
                'staff': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Staff.DoesNotExist:
            logger.warning(f"❌ Staff not found: {kwargs.get('pk')}")
            return Response({
                'success': False,
                'message': 'Staff not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"❌ Error retrieving staff: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Error retrieving staff details',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
    def create(self, request, *args, **kwargs):
        """
        Create new staff profile.
        
        Body Parameters (JSON):
        - user_id: User ID (required)
        - department: Department (required)
        - position_title: Position title
        - employment_type: full_time/part_time/contract/volunteer
        - employment_date: Date of employment
        - And other optional staff fields...
        
        Returns:
            Response: Created staff object with ID
        """
        try:
            logger.info(f"➕ CREATING NEW STAFF")
            logger.info(f"📊 Request data: {request.data}")
            
            # Validate required fields
            user_id = request.data.get('user_id')
            department = request.data.get('department')
            
            if not user_id:
                return Response({
                    'success': False,
                    'message': 'user_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not department:
                return Response({
                    'success': False,
                    'message': 'department is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'User with ID {user_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if user already has staff profile
            if Staff.objects.filter(user=user).exists():
                return Response({
                    'success': False,
                    'message': 'User already has a staff profile'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract data
            data = dict(request.data)
            data.pop('user_id', None)
            
            # Create staff with transaction
            with transaction.atomic():
                staff = Staff.objects.create(
                    user=user,
                    **data
                )
                
                # Create default permissions
                StaffPermission.objects.create(staff=staff)
                
                # Create teacher profile if applicable
                if user.role in ['teacher', 'form_teacher', 'subject_teacher',
                                'head', 'hm', 'principal', 'vice_principal']:
                    TeacherProfile.objects.create(staff=staff)
                
                logger.info(f"✅ Staff created: {staff.staff_id}")
            
            # Serialize and return
            serializer = self.get_serializer(staff)
            
            return Response({
                'success': True,
                'message': 'Staff created successfully',
                'staff': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"❌ Error creating staff: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to create staff',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
    def update(self, request, *args, **kwargs):
        """
        Full update (PUT) - all fields
        """
        return self.full_update(request, *args, **kwargs)
    
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partial update (PATCH) - only provided fields
        """
        return self.full_update(request, *args, **kwargs)
    
    
    def full_update(self, request, pk=None, *args, **kwargs):
        """
        Comprehensive staff update with all fields.
        
        Handles:
        - User fields (first_name, last_name, email, phone_number, etc.)
        - Staff fields (department, position_title, salary, etc.)
        - File uploads (resume, certificates, id_copy, passport_photo)
        - Status changes (is_active, is_on_leave, is_on_probation, etc.)
        
        Methods:
        - PUT: Complete update (all fields required)
        - PATCH: Partial update (only provided fields updated)
        
        URL Parameters:
        - pk: Staff ID
        
        Body:
        - FormData (with files) or JSON (text only)
        
        Returns:
            Response: Updated staff object
        """
        logger.info(f"🔄 FULL UPDATE REQUEST FOR STAFF {pk}")
        logger.info(f"📊 Method: {request.method}")
        logger.info(f"👤 User: {request.user.username}")
        logger.info(f"📋 Data keys: {list(request.data.keys())}")
        logger.info(f"📁 Files: {list(request.FILES.keys())}")
        
        try:
            # =====================
            # GET STAFF OBJECT
            # =====================
            
            staff = Staff.objects.select_related('user').get(pk=pk)
            
            logger.info(f"✓ Found staff: {staff.staff_id} - {staff.user.email}")
            
            # Check permissions
            self.check_object_permissions(request, staff)
            
            user = staff.user
            
            # =====================
            # START TRANSACTION
            # =====================
            
            with transaction.atomic():
                
                # =====================
                # UPDATE USER FIELDS
                # =====================
                
                user_fields = [
                    'first_name', 'last_name', 'email', 'phone_number',
                    'gender', 'date_of_birth', 'address', 'city',
                    'state_of_origin', 'lga', 'nationality'
                ]
                
                user_updated = False
                
                logger.info("📋 Processing user fields...")
                
                for field in user_fields:
                    if field in request.data:
                        new_value = request.data.get(field)
                        current_value = getattr(user, field, None)
                        
                        # Handle empty strings
                        if new_value == '':
                            new_value = None
                        
                        # Handle date field
                        if field == 'date_of_birth' and new_value:
                            if isinstance(new_value, str):
                                try:
                                    new_value = datetime.strptime(new_value, '%Y-%m-%d').date()
                                except ValueError:
                                    logger.warning(f"⚠ Invalid date format for {field}: {new_value}")
                                    continue
                        
                        # Check if changed
                        if current_value != new_value:
                            setattr(user, field, new_value)
                            user_updated = True
                            logger.info(f"  ✓ {field}: '{current_value}' → '{new_value}'")
                
                # Save user changes
                if user_updated:
                    user.full_clean()
                    user.save()
                    logger.info(f"✅ User saved: {user.registration_number}")
                else:
                    logger.info("ℹ No user changes")
                
                # =====================
                # UPDATE STAFF FIELDS
                # =====================
                
                staff_fields = [
                    'department', 'position_title', 'employment_type',
                    'employment_date', 'highest_qualification', 
                    'qualification_institution', 'year_of_graduation', 
                    'professional_certifications', 'trcn_number',
                    'trcn_expiry_date', 'specialization', 'basic_salary', 
                    'salary_scale', 'salary_step', 'bank_name', 
                    'account_name', 'account_number', 'annual_leave_days', 
                    'sick_leave_days', 'next_of_kin_name',
                    'next_of_kin_relationship', 'next_of_kin_phone', 
                    'next_of_kin_address', 'blood_group', 'genotype', 
                    'medical_conditions', 'allergies',
                    'emergency_contact_name', 'emergency_contact_phone',
                    'emergency_contact_relationship', 'years_of_experience',
                    'previous_employers', 'references', 'is_active', 
                    'is_on_probation', 'probation_end_date', 'is_retired', 
                    'retirement_date', 'is_on_leave', 'leave_start_date', 
                    'leave_end_date', 'performance_rating', 
                    'last_appraisal_date', 'next_appraisal_date', 
                    'appraisal_notes'
                ]
                
                staff_updated = False
                
                logger.info("📋 Processing staff fields...")
                
                for field in staff_fields:
                    if field in request.data:
                        new_value = request.data.get(field)
                        current_value = getattr(staff, field, None)
                        
                        # Handle empty strings
                        if new_value == '':
                            new_value = None
                        
                        # Handle boolean fields
                        elif field in ['is_active', 'is_on_probation', 'is_retired', 'is_on_leave']:
                            if isinstance(new_value, str):
                                new_value = new_value.lower() in ['true', '1', 'yes', 'on']
                            else:
                                new_value = bool(new_value)
                        
                        # Handle decimal/float fields
                        elif field in ['basic_salary', 'performance_rating']:
                            try:
                                new_value = float(new_value) if new_value else 0.0
                            except (ValueError, TypeError):
                                logger.warning(f"⚠ Invalid numeric value for {field}: {new_value}")
                                continue
                        
                        # Handle integer fields
                        elif field in ['year_of_graduation', 'salary_step', 'annual_leave_days',
                                       'sick_leave_days', 'years_of_experience']:
                            try:
                                new_value = int(new_value) if new_value else None
                            except (ValueError, TypeError):
                                logger.warning(f"⚠ Invalid integer value for {field}: {new_value}")
                                continue
                        
                        # Handle date fields
                        elif field in ['employment_date', 'trcn_expiry_date', 'probation_end_date',
                                       'retirement_date', 'leave_start_date', 'leave_end_date',
                                       'last_appraisal_date', 'next_appraisal_date']:
                            if new_value and isinstance(new_value, str):
                                try:
                                    new_value = datetime.strptime(new_value, '%Y-%m-%d').date()
                                except ValueError:
                                    logger.warning(f"⚠ Invalid date format for {field}: {new_value}")
                                    continue
                            elif not new_value:
                                new_value = None
                        
                        # Check if changed
                        if current_value != new_value:
                            setattr(staff, field, new_value)
                            staff_updated = True
                            logger.info(f"  ✓ {field}: '{current_value}' → '{new_value}'")
                
                # =====================
                # HANDLE FILE UPLOADS
                # =====================
                
                file_fields = ['resume', 'certificates', 'id_copy', 'passport_photo']
                
                logger.info("📁 Processing files...")
                
                for field in file_fields:
                    if field in request.FILES:
                        file_obj = request.FILES[field]
                        setattr(staff, field, file_obj)
                        staff_updated = True
                        logger.info(f"  ✓ {field}: {file_obj.name} ({file_obj.size} bytes)")
                
                # =====================
                # SAVE STAFF CHANGES
                # =====================
                
                if staff_updated:
                    staff.updated_at = timezone.now()
                    staff.full_clean()
                    staff.save()
                    logger.info(f"✅ Staff saved: {staff.staff_id}")
                else:
                    logger.info("ℹ No staff changes")
            
            # =====================
            # RETURN UPDATED DATA
            # =====================
            
            staff.refresh_from_db()
            serializer = self.get_serializer(staff)
            
            logger.info(f"✅ UPDATE COMPLETE")
            logger.info(f"   Name: {staff.user.first_name} {staff.user.last_name}")
            logger.info(f"   Email: {staff.user.email}")
            
            return Response({
                'success': True,
                'message': 'Staff updated successfully',
                'staff': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Staff.DoesNotExist:
            logger.error(f"❌ Staff not found: {pk}")
            return Response({
                'success': False,
                'message': 'Staff not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"❌ UPDATE FAILED: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to update staff',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete staff record permanently.
        
        Restrictions:
        - Cannot delete own account
        - Requires CanManageStaff permission
        
        Returns:
            Response: Success message
        """
        try:
            logger.info(f"🗑️ DELETING STAFF {kwargs.get('pk')}")
            
            instance = self.get_object()
            
            # Check permissions
            self.check_object_permissions(request, instance)
            
            # Cannot delete yourself
            if instance.user == request.user:
                return Response({
                    'success': False,
                    'message': 'You cannot delete your own account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Store staff_id for logging
            staff_id = instance.staff_id
            
            # Delete staff
            instance.delete()
            
            logger.info(f"✅ Staff {staff_id} deleted")
            
            return Response({
                'success': True,
                'message': 'Staff deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Staff deletion failed: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Staff deletion failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
    # =====================
    # CUSTOM ACTIONS (@action decorators)
    # =====================
    
    @action(detail=True, methods=['post'])
    def update_password(self, request, pk=None):
        """
        Update staff password.
        
        URL Parameters:
        - pk: Staff ID
        
        Body (JSON):
        {
            "new_password": "newPassword123",
            "confirm_password": "newPassword123"
        }
        
        Returns:
            Response: Success message with status
        """
        try:
            logger.info(f"🔐 UPDATING PASSWORD FOR STAFF {pk}")
            
            staff = self.get_object()
            
            # Check permissions
            self.check_object_permissions(request, staff)
            
            # Validate password data
            serializer = StaffPasswordUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Update user password
            user = staff.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            logger.info(f"✅ Password updated for staff {staff.staff_id}")
            
            return Response({
                'success': True,
                'message': 'Password updated successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Password update failed: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Password update failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=True, methods=['delete'])
    def delete_file(self, request, pk=None):
        """
        Delete staff file.
        
        URL Parameters:
        - pk: Staff ID
        
        Query Parameters:
        - file_type: resume | certificates | id_copy | passport_photo
        
        Returns:
            Response: Success message
        """
        try:
            logger.info(f"🗑️ DELETING FILE FOR STAFF {pk}")
            
            staff = self.get_object()
            
            # Check permissions
            self.check_object_permissions(request, staff)
            
            # Get file type from query params
            file_type = request.query_params.get('file_type')
            
            if not file_type:
                return Response({
                    'success': False,
                    'message': 'file_type parameter is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate file type
            valid_file_types = ['resume', 'certificates', 'id_copy', 'passport_photo']
            
            if file_type not in valid_file_types:
                return Response({
                    'success': False,
                    'message': f'Invalid file type. Must be one of: {", ".join(valid_file_types)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Delete file
            setattr(staff, file_type, None)
            staff.save()
            
            logger.info(f"✅ File {file_type} deleted for staff {staff.staff_id}")
            
            return Response({
                'success': True,
                'message': f'File {file_type} deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ File deletion failed: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'File deletion failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get staff statistics and insights.
        
        Returns:
            Response: Comprehensive statistics about staff
        """
        try:
            logger.info(f"📊 GENERATING STAFF STATISTICS")
            
            # =====================
            # OVERALL STATISTICS
            # =====================
            
            total_staff = Staff.objects.count()
            active_staff = Staff.objects.filter(is_active=True).count()
            inactive_staff = total_staff - active_staff
            
            # =====================
            # DEPARTMENT STATISTICS
            # =====================
            
            department_stats = {}
            for dept_code, dept_name in Staff.DEPARTMENT_CHOICES:
                count = Staff.objects.filter(department=dept_code).count()
                if count > 0:
                    department_stats[dept_name] = count
            
            # =====================
            # EMPLOYMENT TYPE STATISTICS
            # =====================
            
            employment_stats = {}
            for emp_code, emp_name in Staff.EMPLOYMENT_TYPE_CHOICES:
                count = Staff.objects.filter(employment_type=emp_code).count()
                if count > 0:
                    employment_stats[emp_name] = count
            
            # =====================
            # RECENT HIRES
            # =====================
            
            thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
            recent_hires = Staff.objects.filter(
                employment_date__gte=thirty_days_ago
            ).count()
            
            # =====================
            # LEAVE STATISTICS
            # =====================
            
            staff_on_leave = Staff.objects.filter(is_on_leave=True).count()
            
            # =====================
            # SALARY STATISTICS
            # =====================
            
            try:
                salary_stats = Staff.objects.aggregate(
                    avg_salary=Avg('basic_salary'),
                    total_salary=Sum('basic_salary'),
                    min_salary=Min('basic_salary'),
                    max_salary=Max('basic_salary')
                )
            except:
                salary_stats = {
                    'avg_salary': 0,
                    'total_salary': 0,
                    'min_salary': 0,
                    'max_salary': 0
                }
            
            logger.info(f"✅ Statistics generated")
            
            return Response({
                'success': True,
                'stats': {
                    'total': total_staff,
                    'active': active_staff,
                    'inactive': inactive_staff,
                    'on_leave': staff_on_leave,
                    'recent_hires': recent_hires,
                    'by_department': department_stats,
                    'by_employment_type': employment_stats,
                    'salary': {
                        'average': float(salary_stats['avg_salary'] or 0),
                        'total': float(salary_stats['total_salary'] or 0),
                        'min': float(salary_stats['min_salary'] or 0),
                        'max': float(salary_stats['max_salary'] or 0)
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"❌ Error generating statistics: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Failed to generate statistics',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple staff records in bulk.
        
        Body (JSON):
        {
            "staff": [
                {
                    "user_id": 1,
                    "department": "academic",
                    "position_title": "Teacher",
                    ...
                },
                ...
            ]
        }
        
        Returns:
            Response: Created staff count and errors
        """
        try:
            logger.info(f"➕ BULK CREATING STAFF")
            
            staff_data_list = request.data.get('staff', [])
            
            if not staff_data_list:
                return Response({
                    'success': False,
                    'message': 'staff list is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            created = []
            errors = []
            
            with transaction.atomic():
                for i, staff_data in enumerate(staff_data_list):
                    try:
                        user_id = staff_data.get('user_id')
                        
                        if not user_id:
                            errors.append({
                                'index': i,
                                'error': 'user_id is required'
                            })
                            continue
                        
                        # Get user
                        user = User.objects.get(id=user_id)
                        
                        # Check if user already has staff profile
                        if Staff.objects.filter(user=user).exists():
                            errors.append({
                                'index': i,
                                'error': f'User {user_id} already has staff profile'
                            })
                            continue
                        
                        # Create staff
                        staff_obj = Staff.objects.create(
                            user=user,
                            **{k: v for k, v in staff_data.items() if k != 'user_id'}
                        )
                        
                        # Create permissions
                        StaffPermission.objects.create(staff=staff_obj)
                        
                        # Create teacher profile if applicable
                        if user.role in ['teacher', 'form_teacher', 'subject_teacher',
                                        'head', 'hm', 'principal', 'vice_principal']:
                            TeacherProfile.objects.create(staff=staff_obj)
                        
                        created.append(staff_obj)
                        
                    except User.DoesNotExist:
                        errors.append({
                            'index': i,
                            'error': f'User {staff_data.get("user_id")} not found'
                        })
                    except Exception as e:
                        errors.append({
                            'index': i,
                            'error': str(e)
                        })
            
            logger.info(f"✅ Bulk create complete: {len(created)} created, {len(errors)} errors")
            
            return Response({
                'success': len(errors) == 0,
                'created': len(created),
                'errors': len(errors),
                'staff': StaffListSerializer(created, many=True, context=self.get_serializer_context()).data,
                'error_details': errors
            }, status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"❌ Bulk create failed: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Bulk create failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

# =====================
# SEPARATE FUNCTION-BASED VIEW FOR PASSWORD UPDATE
# (to fix the import error in urls.py)
# =====================

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def update_staff_password(request, pk):
    """
    Update staff password - Separate function-based view
    Endpoint: POST /api/staff/<id>/update-password/
    """
    try:
        staff = Staff.objects.select_related('user').get(pk=pk)
        
        # Check permissions
        if not (request.user.is_staff or request.user.role in ['head', 'hm', 'principal', 'vice_principal']):
            return Response({
                'success': False,
                'error': 'You do not have permission to reset passwords'
            }, status=status.HTTP_403_FORBIDDEN)
        
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Validation
        if not new_password:
            return Response({
                'success': False,
                'error': 'New password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not confirm_password:
            return Response({
                'success': False,
                'error': 'Password confirmation is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'success': False,
                'error': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        user = staff.user
        user.set_password(new_password)
        user.save()
        
        print(f"✅ Password updated for {user.get_full_name()}")
        
        return Response({
            'success': True,
            'message': f'Password updated successfully for {user.get_full_name()}'
        }, status=status.HTTP_200_OK)
        
    except Staff.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Staff member not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"❌ Password update error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =====================
# STAFF MANAGEMENT VIEWS (REST OF THE FILE REMAINS THE SAME)
# =====================

class StaffListView(generics.ListAPIView):
    """
    List all staff with filtering and search
    
    GET /api/staff/
    
    Filters: department, employment_type, is_active, is_on_leave
    Search: name, email, staff_id, position_title
    Ordering: name, department, employment_date
    
    Permissions: Admin/Principal/Accountant/Secretary
    """
    
    serializer_class = StaffListSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewAllStaff]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['department', 'employment_type', 'is_active', 'is_on_leave', 'is_on_probation']
    search_fields = [
        'user__first_name', 'user__last_name',
        'user__email', 'staff_id', 'employee_number',
        'position_title', 'user__registration_number'
    ]
    ordering_fields = ['user__first_name', 'department', 'employment_date', 'created_at']
    ordering = ['user__first_name']
    
    def get_queryset(self):
        """Filter staff based on user permissions"""
        user = self.request.user
        
        # Admin/Principal can see all staff
        if user.role in ['head', 'principal', 'vice_principal'] or user.is_staff:
            return Staff.objects.select_related('user').all()
        
        # Accountant/Secretary can see all staff
        if user.role in ['accountant', 'secretary']:
            return Staff.objects.select_related('user').all()
        
        # Teachers can see other teaching staff
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            return Staff.objects.filter(
                user__role__in=['teacher', 'form_teacher', 'subject_teacher',
                               'head', 'principal', 'vice_principal']
            ).select_related('user')
        
        # Other staff can only see themselves
        if user.role in ['librarian', 'laboratory', 'security', 'cleaner']:
            try:
                return Staff.objects.filter(user=user).select_related('user')
            except Staff.DoesNotExist:
                return Staff.objects.none()
        
        return Staff.objects.none()


User = get_user_model()

class StaffCreateView(generics.CreateAPIView):
    """
    Create new staff
    
    POST /api/staff/create/
    
    Required: user_id, department
    Optional: position_title, employment_type, etc.
    
    Permissions: Admin/Principal only
    """
    
    serializer_class = StaffCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageStaff]
    
    def create(self, request, *args, **kwargs):
        """Create staff with transaction"""
        with transaction.atomic():
            # Check if user already has a staff profile
            user_id = request.data.get('user_id')
            
            if user_id:
                try:
                    existing_staff = Staff.objects.filter(user_id=user_id).first()
                    if existing_staff:
                        # Update existing staff instead of creating new
                        serializer = self.get_serializer(existing_staff, data=request.data, partial=True)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                        
                        logger.info(
                            f"Staff updated: {existing_staff.staff_id} ({existing_staff.user.role}) "
                            f"by {request.user.registration_number}"
                        )
                        
                        return Response({
                            'message': 'Staff profile updated successfully',
                            'staff': StaffSerializer(existing_staff, context={'request': request}).data
                        }, status=status.HTTP_200_OK)
                except Exception:
                    pass  # Continue with normal creation
            
            # Normal creation if no existing staff
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            staff = serializer.save()
            
            logger.info(
                f"Staff created: {staff.staff_id} ({staff.user.role}) "
                f"by {request.user.registration_number}"
            )
            
            return Response({
                'message': 'Staff created successfully',
                'staff': StaffSerializer(staff, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
            
class StaffDetailView(generics.RetrieveAPIView):
    """
    Get staff details
    
    GET /api/staff/{id}/
    
    Permissions: Staff can view own, admin can view any
    """
    
    serializer_class = StaffDetailSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewStaffDetails]
    queryset = Staff.objects.select_related('user').prefetch_related(
        'teacher_profile__subjects',
        'teacher_profile__class_levels',
        'teacher_profile__assigned_classes',
        'permissions'
    )
    
    def get_object(self):
        """Get staff with permission checks"""
        # If user is staff, try to return their own profile
        if self.request.user.role not in ['student', 'parent']:
            try:
                staff = self.request.user.staff_profile
                # If no specific ID requested, return own profile
                if not self.kwargs.get('pk'):
                    return staff
                # If requesting own profile, return it
                if str(staff.id) == self.kwargs.get('pk'):
                    return staff
            except Staff.DoesNotExist:
                pass
        
        # Otherwise use the normal lookup
        staff = super().get_object()
        
        # Check object-level permissions
        self.check_object_permissions(self.request, staff)
        
        return staff


class StaffUpdateView(generics.UpdateAPIView):
    """
    Update staff profile
    
    PUT/PATCH /api/staff/{id}/update/
    
    Permissions: Staff can update own (limited), admin can update any
    """
    
    serializer_class = StaffUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditStaffProfile]
    queryset = Staff.objects.select_related('user')
    
    def update(self, request, *args, **kwargs):
        """Update staff with permission checks"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check object-level permissions
        self.check_object_permissions(request, instance)
        
        # Staff cannot edit restricted fields on their own profile
        if request.user.role not in ['head', 'principal', 'vice_principal'] and instance.user == request.user:
            restricted_fields = [
                'staff_id', 'employee_number', 'basic_salary', 'salary_scale',
                'is_active', 'is_on_probation', 'probation_end_date',
                'is_retired', 'retirement_date', 'employment_date',
                'employment_type', 'department', 'performance_rating',
                'last_appraisal_date', 'next_appraisal_date', 'appraisal_notes'
            ]
            
            for field in request.data:
                if field in restricted_fields:
                    return Response({
                        'error': f'You cannot modify the {field} field'
                    }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Staff updated: {instance.staff_id} by {request.user.registration_number}")
        
        return Response({
            'message': 'Staff updated successfully',
            'staff': StaffSerializer(instance, context={'request': request}).data
        })


class StaffDashboardView(APIView):
    """
    Staff dashboard with comprehensive information
    
    GET /api/staff/dashboard/
    
    Permissions: All staff members
    """
    
    permission_classes = [permissions.IsAuthenticated, CanAccessStaffDashboard]
    
    def get(self, request):
        """Get staff dashboard"""
        try:
            staff = request.user.staff_profile
        except Staff.DoesNotExist:
            return Response({
                'error': 'Staff profile not found. Please contact administrator.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get dashboard data
        dashboard_data = self._get_dashboard_data(staff)
        
        return Response({
            'dashboard': dashboard_data
        })
    
    def _get_dashboard_data(self, staff):
        """Get comprehensive dashboard data"""
        from students.models import Student
        from academic.models import Class
        
        data = {
            'staff': StaffSerializer(staff, context={'request': self.request}).data,
            'quick_stats': self._get_quick_stats(staff),
            'recent_activities': self._get_recent_activities(staff),
            'upcoming_events': self._get_upcoming_events(staff),
            'pending_tasks': self._get_pending_tasks(staff),
        }
        
        # Add teacher-specific data if applicable
        if hasattr(staff, 'teacher_profile'):
            data['teacher_stats'] = self._get_teacher_stats(staff.teacher_profile)
        
        return data
    
    def _get_quick_stats(self, staff):
        """Get quick statistics for dashboard"""
        stats = {
            'employment_duration': staff.get_employment_duration(),
            'leave_days_remaining': staff.leave_days_remaining,
            'leave_days_taken': staff.leave_days_taken,
            'annual_leave_days': staff.annual_leave_days,
            'is_on_leave': staff.is_on_leave,
            'performance_rating': float(staff.performance_rating),
            'next_appraisal_date': staff.next_appraisal_date,
        }
        
        # Add teacher-specific stats
        if hasattr(staff, 'teacher_profile'):
            teacher = staff.teacher_profile
            stats.update({
                'workload_percentage': teacher.get_workload_percentage(),
                'workload_status': teacher.get_workload_status(),
                'current_periods': teacher.current_periods_per_week,
                'max_periods': teacher.max_periods_per_week,
                'subjects_count': teacher.subjects.count(),
                'classes_count': teacher.assigned_classes.count() + teacher.assistant_classes.count(),
            })
        
        return stats
    
    def _get_recent_activities(self, staff):
        """Get recent activities"""
        # This would fetch from activity log in production
        activities = []
        
        if staff.last_appraisal_date:
            activities.append({
                'date': staff.last_appraisal_date,
                'activity': 'Performance Appraisal',
                'details': f'Rating: {staff.performanceRating}',
                'type': 'appraisal'
            })
        
        if staff.leave_start_date:
            activities.append({
                'date': staff.leave_start_date,
                'activity': 'Leave Started',
                'details': f'Leave period: {staff.leave_start_date} to {staff.leave_end_date}',
                'type': 'leave'
            })
        
        activities.append({
            'date': timezone.now().date(),
            'activity': 'Profile Update',
            'details': 'Last profile update',
            'type': 'profile'
        })
        
        return activities
    
    def _get_upcoming_events(self, staff):
        """Get upcoming events"""
        # This would fetch from academic calendar in production
        return [
            {
                'date': timezone.now().date() + timezone.timedelta(days=7),
                'title': 'Staff Meeting',
                'description': 'Monthly staff meeting',
                'type': 'meeting'
            },
            {
                'date': timezone.now().date() + timezone.timedelta(days=14),
                'title': 'Professional Development',
                'description': 'Training workshop',
                'type': 'training'
            }
        ]
    
    def _get_pending_tasks(self, staff):
        """Get pending tasks"""
        # This would fetch from task management system in production
        tasks = []
        
        if staff.user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            tasks.append({
                'title': 'Upload Results',
                'description': 'Upload end of term results',
                'priority': 'high',
                'due_date': timezone.now().date() + timezone.timedelta(days=3)
            })
        
        if staff.next_appraisal_date:
            if staff.next_appraisal_date <= timezone.now().date() + timezone.timedelta(days=30):
                tasks.append({
                    'title': 'Prepare for Appraisal',
                    'description': 'Upcoming performance appraisal',
                    'priority': 'medium',
                    'due_date': staff.next_appraisal_date
                })
        
        return tasks
    
    def _get_teacher_stats(self, teacher_profile):
        """Get teacher-specific statistics"""
        from students.models import Student
        
        stats = {
            'students_count': teacher_profile.get_students().count(),
            'class_teacher_students': teacher_profile.get_class_teacher_students().count(),
            'subjects': teacher_profile.get_subjects_list(),
            'class_levels': teacher_profile.get_class_levels_list(),
            'assigned_classes': teacher_profile.get_assigned_classes_list(),
        }
        
        return stats


# =====================
# TEACHER PROFILE VIEWS
# =====================

class TeacherProfileListView(generics.ListAPIView):
    """
    List all teacher profiles
    
    GET /api/staff/teachers/
    
    Permissions: Admin/Principal/Teachers
    """
    
    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTeacherProfile]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    filterset_fields = ['teacher_type', 'stream_specialization']
    search_fields = [
        'staff__user__first_name', 'staff__user__last_name',
        'staff__staff_id', 'staff__user__registration_number'
    ]
    
    def get_queryset(self):
        """Filter teacher profiles based on permissions"""
        user = self.request.user
        
        if user.role in ['head', 'principal', 'vice_principal'] or user.is_staff:
            return TeacherProfile.objects.select_related(
                'staff__user'
            ).prefetch_related(
                'subjects', 'class_levels', 'assigned_classes'
            ).all()
        
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            # Teachers can see other teachers in their department
            try:
                staff = user.staff_profile
                return TeacherProfile.objects.filter(
                    staff__department=staff.department
                ).select_related(
                    'staff__user'
                ).prefetch_related(
                    'subjects', 'class_levels', 'assigned_classes'
                )
            except Staff.DoesNotExist:
                return TeacherProfile.objects.none()
        
        return TeacherProfile.objects.none()


class TeacherProfileCreateView(generics.CreateAPIView):
    """
    Create teacher profile
    
    POST /api/staff/teachers/create/
    
    Required: staff_id, teacher_type
    Optional: subjects, class_levels, etc.
    
    Permissions: Admin/Principal only
    """
    
    serializer_class = TeacherProfileCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTeacherProfile]
    
    def create(self, request, *args, **kwargs):
        """Create teacher profile with transaction"""
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            teacher_profile = serializer.save()
            
            logger.info(
                f"Teacher profile created for {teacher_profile.staff.staff_id} "
                f"by {request.user.registration_number}"
            )
            
            return Response({
                'message': 'Teacher profile created successfully',
                'teacher_profile': TeacherProfileSerializer(teacher_profile).data
            }, status=status.HTTP_201_CREATED)


class TeacherProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update teacher profile
    
    GET/PUT/PATCH /api/staff/teachers/{id}/
    
    Permissions: Teacher can view own, admin can view/update any
    """
    
    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTeacherProfile]
    queryset = TeacherProfile.objects.select_related(
        'staff__user'
    ).prefetch_related(
        'subjects', 'class_levels', 'assigned_classes',
        'assistant_classes', 'hod_subjects'
    )
    
    def get_object(self):
        """Get teacher profile with permission checks"""
        teacher_profile = super().get_object()
        
        # Check if user is the teacher themselves
        if teacher_profile.staff.user == self.request.user:
            return teacher_profile
        
        # Check if user has admin permissions
        self.check_object_permissions(self.request, teacher_profile)
        
        return teacher_profile


# =====================
# STAFF PERMISSION VIEWS
# =====================

class StaffPermissionDetailView(generics.RetrieveAPIView):
    """
    Get staff permissions
    
    GET /api/staff/{id}/permissions/
    
    Permissions: Staff can view own, admin can view any
    """
    
    serializer_class = StaffPermissionSerializer
    permission_classes = [permissions.IsAuthenticated, CanManagePermissions]
    
    def get_object(self):
        """Get staff permissions"""
        staff_id = self.kwargs.get('pk')
        staff = get_object_or_404(Staff, pk=staff_id)
        
        # Check permissions
        if staff.user != self.request.user:
            self.check_object_permissions(self.request, staff)
        
        # Get or create permissions
        permissions_obj, created = StaffPermission.objects.get_or_create(staff=staff)
        return permissions_obj


class StaffPermissionUpdateView(APIView):
    """
    Update staff permissions
    
    PUT /api/staff/{id}/permissions/update/
    
    Permissions: Admin/Principal only
    """
    
    permission_classes = [permissions.IsAuthenticated, CanManagePermissions]
    
    def put(self, request, pk):
        """Update staff permissions"""
        staff = get_object_or_404(Staff, pk=pk)
        
        # Check if user can manage permissions for this staff
        self.check_object_permissions(request, staff)
        
        serializer = StaffPermissionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get or create permissions
        permissions_obj, created = StaffPermission.objects.get_or_create(staff=staff)
        
        # Update permissions
        permissions_obj.update_permissions(serializer.validated_data['permissions'])
        
        logger.info(
            f"Permissions updated for staff {staff.staff_id} "
            f"by {request.user.registration_number}"
        )
        
        return Response({
            'message': 'Permissions updated successfully',
            'permissions': StaffPermissionSerializer(permissions_obj).data
        })

# staff/views.py - Add this class

class StaffPasswordResetView(APIView):
    """
    Reset staff password - Only accessible by head/hm
    POST /api/staff/<staff_id>/update-password/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, staff_id):
        try:
            # Check if user has permission (only head/hm)
            if request.user.role not in ['head', 'hm'] and not request.user.is_superuser:
                return Response({
                    'success': False,
                    'message': 'Only Head of School or Head Master can reset passwords'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get the staff member
            try:
                staff = Staff.objects.get(id=staff_id)
            except Staff.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Staff not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get the user
            user = staff.user
            if not user:
                return Response({
                    'success': False,
                    'message': 'Staff has no associated user account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get password data
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')
            
            # Validate
            if not new_password or not confirm_password:
                return Response({
                    'success': False,
                    'message': 'Both password fields are required',
                    'errors': {
                        'new_password': ['This field is required.'],
                        'confirm_password': ['This field is required.']
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if new_password != confirm_password:
                return Response({
                    'success': False,
                    'message': 'Passwords do not match',
                    'errors': {
                        'confirm_password': ['Passwords do not match.']
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if len(new_password) < 5:
                return Response({
                    'success': False,
                    'message': 'Password must be at least 5 characters',
                    'errors': {
                        'new_password': ['Password must be at least 5 characters long.']
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            logger.info(f"Admin {request.user.registration_number} reset password for staff: {staff.staff_id}")
            
            return Response({
                'success': True,
                'message': 'Password reset successfully',
                'staff_id': staff.id,
                'staff_name': user.get_full_name()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error resetting staff password: {str(e)}")
            return Response({
                'success': False,
                'message': 'An error occurred',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =====================
# STAFF ACTIVATION/DEACTIVATION VIEWS
# =====================

class ActivateStaffView(APIView):
    """
    Activate staff member
    
    POST /api/staff/{id}/activate/
    
    Permissions: Admin/Principal only
    """
    
    permission_classes = [permissions.IsAuthenticated, CanActivateDeactivateStaff]
    
    def post(self, request, pk):
        """Activate staff member"""
        staff = get_object_or_404(Staff, pk=pk)
        
        if staff.is_active:
            return Response({
                'error': 'Staff is already active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = StaffActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        staff.is_active = True
        staff.is_on_probation = False
        staff.save()
        
        logger.info(
            f"Staff {staff.staff_id} activated by {request.user.registration_number}"
        )
        
        return Response({
            'message': 'Staff activated successfully',
            'staff': StaffSerializer(staff, context={'request': request}).data
        })


class DeactivateStaffView(APIView):
    """
    Deactivate staff member
    
    POST /api/staff/{id}/deactivate/
    
    Permissions: Admin/Principal only
    """
    
    permission_classes = [permissions.IsAuthenticated, CanActivateDeactivateStaff]
    
    def post(self, request, pk):
        """Deactivate staff member"""
        staff = get_object_or_404(Staff, pk=pk)
        
        # Cannot deactivate self
        if staff.user == request.user:
            return Response({
                'error': 'You cannot deactivate your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not staff.is_active:
            return Response({
                'error': 'Staff is already inactive'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = StaffActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        staff.is_active = False
        staff.save()
        
        logger.info(
            f"Staff {staff.staff_id} deactivated by {request.user.registration_number}"
        )
        
        return Response({
            'message': 'Staff deactivated successfully',
            'staff': StaffSerializer(staff, context={'request': request}).data
        })


# =====================
# STAFF RETIREMENT VIEW
# =====================

class RetireStaffView(APIView):
    """
    Retire staff member
    
    POST /api/staff/{id}/retire/
    
    Permissions: Admin/Principal only
    """
    
    permission_classes = [permissions.IsAuthenticated, CanRetireStaff]
    
    def post(self, request, pk):
        """Retire staff member"""
        staff = get_object_or_404(Staff, pk=pk)
        
        if staff.is_retired:
            return Response({
                'error': 'Staff is already retired'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = StaffRetirementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        staff.is_retired = True
        staff.is_active = False
        staff.retirement_date = serializer.validated_data['retirement_date']
        staff.save()
        
        logger.info(
            f"Staff {staff.staff_id} retired by {request.user.registration_number}"
        )
        
        return Response({
            'message': 'Staff retired successfully',
            'staff': StaffSerializer(staff, context={'request': request}).data
        })


# =====================
# STAFF SALARY VIEWS
# =====================

class UpdateStaffSalaryView(APIView):
    """
    Update staff salary
    
    POST /api/staff/{id}/update-salary/
    
    Permissions: Admin/Principal/Accountant only
    """
    
    permission_classes = [permissions.IsAuthenticated, CanViewSalaryInfo]
    
    def post(self, request, pk):
        """Update staff salary"""
        staff = get_object_or_404(Staff, pk=pk)
        
        # Check if user can update salary
        if not (request.user.role in ['head', 'principal', 'vice_principal', 'accountant'] or 
                request.user.is_staff):
            return Response({
                'error': 'You do not have permission to update salaries'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = StaffSalaryUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_salary = staff.basic_salary
        staff.basic_salary = serializer.validated_data['basic_salary']
        staff.salary_scale = serializer.validated_data.get('salary_scale', staff.salary_scale)
        staff.salary_step = serializer.validated_data.get('salary_step', staff.salary_step)
        staff.save()
        
        logger.info(
            f"Salary updated for staff {staff.staff_id}: "
            f"₦{old_salary} -> ₦{staff.basic_salary} "
            f"by {request.user.registration_number}"
        )
        
        return Response({
            'message': 'Salary updated successfully',
            'old_salary': float(old_salary),
            'new_salary': float(staff.basic_salary),
            'salary_scale': staff.salary_scale,
            'salary_step': staff.salary_step
        })


class StaffSalaryView(APIView):
    """
    Get staff salary information
    
    GET /api/staff/{id}/salary/
    
    Permissions: Staff can view own, admin/accountant can view any
    """
    
    permission_classes = [permissions.IsAuthenticated, CanViewSalaryInfo]
    
    def get(self, request, pk=None):
        """Get staff salary"""
        if pk is None and request.user.role not in ['student', 'parent']:
            # Staff viewing own salary
            try:
                staff = request.user.staff_profile
            except Staff.DoesNotExist:
                return Response({
                    'error': 'Staff profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Viewing specific staff salary
            staff = get_object_or_404(Staff, pk=pk)
            
            # Check permissions
            if not self._can_view_salary(request.user, staff):
                return Response({
                    'error': 'You do not have permission to view salary for this staff'
                }, status=status.HTTP_403_FORBIDDEN)
        
        return Response({
            'salary_info': {
                'basic_salary': float(staff.basic_salary),
                'salary_scale': staff.salary_scale,
                'salary_step': staff.salary_step,
                'salary_breakdown': staff.get_salary_breakdown(),
                'monthly_salary': float(staff.get_monthly_salary()),
            }
        })
    
    def _can_view_salary(self, user, staff):
        """Check if user can view salary for staff"""
        # Staff can view their own salary
        if staff.user == user:
            return True
        
        # Admin/Accountant can view all salaries
        if user.role in ['head', 'principal', 'vice_principal', 'accountant'] or user.is_staff:
            return True
        
        return False


# =====================
# STAFF STATISTICS VIEW
# =====================

class StaffStatisticsView(APIView):
    """
    Get staff statistics for dashboard
    
    GET /api/staff/statistics/
    
    Permissions: Admin/Principal/Accountant
    """
    
    permission_classes = [permissions.IsAuthenticated, CanViewStaffStatistics]
    
    def get(self, request):
        """Get comprehensive staff statistics"""
        try:
            # =====================
            # OVERALL STATISTICS
            # =====================
            total_staff = Staff.objects.count() or 0
            active_staff = Staff.objects.filter(is_active=True).count() or 0
            inactive_staff = total_staff - active_staff
            
            # Teaching staff roles
            teaching_roles = ['teacher', 'form_teacher', 'subject_teacher', 
                            'head', 'principal', 'vice_principal']
            teaching_staff = Staff.objects.filter(
                user__role__in=teaching_roles
            ).count() or 0
            
            # Non-teaching staff roles
            non_teaching_roles = ['accountant', 'secretary', 'librarian', 
                                 'laboratory', 'security', 'cleaner']
            non_teaching_staff = Staff.objects.filter(
                user__role__in=non_teaching_roles
            ).count() or 0
            
            # Admin staff
            admin_staff = Staff.objects.filter(
                user__role__in=['head', 'principal', 'vice_principal']
            ).count() or 0
            
            # =====================
            # DEPARTMENT DISTRIBUTION
            # =====================
            department_distribution = []
            try:
                dept_data = Staff.objects.values(
                    'department'
                ).annotate(
                    count=Count('id')
                ).order_by('department')
                
                for item in dept_data:
                    department_distribution.append({
                        'department': item['department'],
                        'department_display': dict(Staff.DEPARTMENT_CHOICES).get(item['department'], item['department']),
                        'count': item['count'] or 0
                    })
            except Exception as e:
                logger.error(f"Error getting department distribution: {str(e)}")
            
            # =====================
            # EMPLOYMENT TYPE DISTRIBUTION
            # =====================
            employment_type_distribution = []
            try:
                emp_data = Staff.objects.values(
                    'employment_type'
                ).annotate(
                    count=Count('id')
                ).order_by('employment_type')
                
                for item in emp_data:
                    employment_type_distribution.append({
                        'employment_type': item['employment_type'],
                        'employment_type_display': dict(Staff.EMPLOYMENT_TYPE_CHOICES).get(item['employment_type'], item['employment_type']),
                        'count': item['count'] or 0
                    })
            except Exception as e:
                logger.error(f"Error getting employment type distribution: {str(e)}")
            
            # =====================
            # FINANCIAL STATISTICS
            # =====================
            try:
                salary_stats = Staff.objects.filter(
                    is_active=True
                ).aggregate(
                    avg_salary=Avg('basic_salary'),
                    total_salary=Sum('basic_salary'),
                    min_salary=models.Min('basic_salary'),
                    max_salary=models.Max('basic_salary')
                )
                
                avg_salary = float(salary_stats['avg_salary'] or 0)
                total_salary = float(salary_stats['total_salary'] or 0)
                min_salary = float(salary_stats['min_salary'] or 0)
                max_salary = float(salary_stats['max_salary'] or 0)
                
            except Exception as e:
                logger.error(f"Error getting salary statistics: {str(e)}")
                avg_salary = total_salary = min_salary = max_salary = 0.0
            
            # =====================
            # LEAVE MANAGEMENT
            # =====================
            try:
                leave_stats = Staff.objects.filter(
                    is_active=True
                ).aggregate(
                    total_leave_days=Sum('annual_leave_days'),
                    avg_leave_days=Avg('annual_leave_days'),
                    total_leave_taken=Sum('leave_days_taken')
                )
                
                total_leave_days = leave_stats['total_leave_days'] or 0
                avg_leave_days = float(leave_stats['avg_leave_days'] or 0)
                total_leave_taken = leave_stats['total_leave_taken'] or 0
                
                # Calculate utilization rate safely
                if total_leave_days > 0:
                    leave_utilization_rate = round((total_leave_taken / total_leave_days) * 100, 2)
                else:
                    leave_utilization_rate = 0.0
                    
            except Exception as e:
                logger.error(f"Error getting leave statistics: {str(e)}")
                total_leave_days = avg_leave_days = total_leave_taken = leave_utilization_rate = 0
            
            # =====================
            # PERFORMANCE STATISTICS
            # =====================
            try:
                performance_stats = Staff.objects.filter(
                    is_active=True
                ).aggregate(
                    avg_performance=Avg('performance_rating'),
                    min_performance=models.Min('performance_rating'),
                    max_performance=models.Max('performance_rating')
                )
                
                avg_performance = float(performance_stats['avg_performance'] or 0)
                min_performance = float(performance_stats['min_performance'] or 0)
                max_performance = float(performance_stats['max_performance'] or 0)
                
            except Exception as e:
                logger.error(f"Error getting performance statistics: {str(e)}")
                avg_performance = min_performance = max_performance = 0.0
            
            # =====================
            # ADDITIONAL STATISTICS
            # =====================
            try:
                # Recent hires (last 90 days)
                ninety_days_ago = timezone.now() - timezone.timedelta(days=90)
                recent_hires = Staff.objects.filter(
                    employment_date__gte=ninety_days_ago
                ).count() or 0
                
                # Staff on leave
                staff_on_leave = Staff.objects.filter(is_on_leave=True).count() or 0
                
                # Retired staff
                retired_staff = Staff.objects.filter(is_retired=True).count() or 0
                
            except Exception as e:
                logger.error(f"Error getting additional statistics: {str(e)}")
                recent_hires = staff_on_leave = retired_staff = 0
            
            # =====================
            # TEACHER-SPECIFIC STATISTICS
            # =====================
            teacher_stats = {}
            try:
                teacher_count = TeacherProfile.objects.count() or 0
                if teacher_count > 0:
                    teacher_stats = {
                        'total_teachers': teacher_count,
                        'by_type': self._get_teacher_type_distribution(),
                        'avg_workload': self._get_average_teacher_workload(),
                        'stream_distribution': self._get_teacher_stream_distribution(),
                        'subjects_distribution': self._get_subjects_distribution()
                    }
            except Exception as e:
                logger.error(f"Error getting teacher statistics: {str(e)}")
            
            # =====================
            # PERFORMANCE DISTRIBUTION
            # =====================
            performance_distribution = []
            try:
                performance_distribution = self._get_performance_distribution()
            except Exception as e:
                logger.error(f"Error getting performance distribution: {str(e)}")
            
            # =====================
            # BUILD FINAL RESPONSE
            # =====================
            response_data = {
                'overall': {
                    'total_staff': total_staff,
                    'active_staff': active_staff,
                    'inactive_staff': inactive_staff,
                    'teaching_staff': teaching_staff,
                    'non_teaching_staff': non_teaching_staff,
                    'admin_staff': admin_staff,
                    'recent_hires': recent_hires,
                    'staff_on_leave': staff_on_leave,
                    'retired_staff': retired_staff,
                    'active_percentage': round((active_staff / total_staff * 100), 2) if total_staff > 0 else 0
                },
                'demographics': {
                    'department_distribution': department_distribution,
                    'employment_type_distribution': employment_type_distribution,
                    'role_distribution': {
                        'teaching': teaching_staff,
                        'non_teaching': non_teaching_staff,
                        'admin': admin_staff
                    }
                },
                'financial': {
                    'avg_salary': avg_salary,
                    'total_salary': total_salary,
                    'min_salary': min_salary,
                    'max_salary': max_salary,
                    'salary_range': f"₦{min_salary:,.2f} - ₦{max_salary:,.2f}" if max_salary > 0 else "No data"
                },
                'leave_management': {
                    'total_leave_days': total_leave_days,
                    'avg_leave_days': avg_leave_days,
                    'total_leave_taken': total_leave_taken,
                    'leave_utilization_rate': leave_utilization_rate,
                    'leave_utilization_percentage': f"{leave_utilization_rate}%"
                },
                'performance': {
                    'avg_performance': avg_performance,
                    'min_performance': min_performance,
                    'max_performance': max_performance,
                    'performance_range': f"{min_performance:.1f} - {max_performance:.1f}",
                    'performance_distribution': performance_distribution
                },
                'teacher_statistics': teacher_stats,
                'metadata': {
                    'generated_at': timezone.now().isoformat(),
                    'staff_count': total_staff,
                    'is_data_available': total_staff > 0
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Critical error in StaffStatisticsView: {str(e)}", exc_info=True)
            return Response({
                'error': 'Unable to generate staff statistics',
                'detail': str(e) if settings.DEBUG else 'Internal server error',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_performance_distribution(self):
        """Get performance rating distribution"""
        distribution = []
        for rating in range(0, 6):  # 0 to 5
            count = Staff.objects.filter(
                performance_rating__gte=float(rating),
                performance_rating__lt=float(rating + 1),
                is_active=True
            ).count()
            distribution.append({
                'rating_range': f'{rating}-{rating + 1}',
                'range_label': f'{rating} to {rating + 1} stars',
                'count': count,
                'percentage': round((count / Staff.objects.filter(is_active=True).count() * 100), 2) if Staff.objects.filter(is_active=True).count() > 0 else 0
            })
        return distribution
    
    def _get_teacher_type_distribution(self):
        """Get teacher type distribution"""
        try:
            teacher_types = TeacherProfile.objects.values(
                'teacher_type'
            ).annotate(
                count=Count('id')
            ).order_by('teacher_type')
            
            result = []
            for item in teacher_types:
                result.append({
                    'teacher_type': item['teacher_type'],
                    'teacher_type_display': dict(TeacherProfile.TEACHER_TYPE_CHOICES).get(item['teacher_type'], item['teacher_type']),
                    'count': item['count'] or 0
                })
            return result
        except Exception as e:
            logger.error(f"Error getting teacher type distribution: {str(e)}")
            return []
    
    def _get_average_teacher_workload(self):
        """Get average teacher workload"""
        try:
            workload_stats = TeacherProfile.objects.aggregate(
                avg_workload=Avg('current_periods_per_week'),
                total_teachers=Count('id')
            )
            return {
                'avg_periods_per_week': float(workload_stats['avg_workload'] or 0),
                'total_teachers': workload_stats['total_teachers'] or 0
            }
        except Exception as e:
            logger.error(f"Error getting teacher workload: {str(e)}")
            return {'avg_periods_per_week': 0, 'total_teachers': 0}
    
    def _get_teacher_stream_distribution(self):
        """Get teacher stream specialization distribution"""
        try:
            stream_data = TeacherProfile.objects.values(
                'stream_specialization'
            ).annotate(
                count=Count('id')
            ).order_by('stream_specialization')
            
            result = []
            for item in stream_data:
                result.append({
                    'stream': item['stream_specialization'],
                    'stream_display': dict(TeacherProfile.STREAM_CHOICES).get(item['stream_specialization'], item['stream_specialization']),
                    'count': item['count'] or 0
                })
            return result
        except Exception as e:
            logger.error(f"Error getting teacher stream distribution: {str(e)}")
            return []
    
    def _get_subjects_distribution(self):
        """Get subjects distribution among teachers"""
        try:
            # This assumes you have a Subject model with a ManyToMany relationship to TeacherProfile
            from django.db.models import Count
            from academic.models import Subject
            
            subject_distribution = Subject.objects.annotate(
                teacher_count=Count('teachers')
            ).filter(
                teacher_count__gt=0
            ).values('name', 'code', 'teacher_count').order_by('-teacher_count')[:10]
            
            return list(subject_distribution)
        except Exception as e:
            logger.error(f"Error getting subjects distribution: {str(e)}")
            return []


# STAFF SEARCH VIEW
# =====================

class StaffSearchView(generics.ListAPIView):
    """
    Search staff with advanced filtering
    
    GET /api/staff/search/
    
    Permissions: Admin/Principal/Accountant/Secretary/Teachers
    """
    
    serializer_class = StaffListSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewAllStaff]
    
    def get_queryset(self):
        """Advanced staff search"""
        queryset = Staff.objects.select_related('user')
        
        # Get query parameters
        name = self.request.query_params.get('name', '')
        staff_id = self.request.query_params.get('staff_id', '')
        department = self.request.query_params.get('department', '')
        employment_type = self.request.query_params.get('employment_type', '')
        role = self.request.query_params.get('role', '')
        is_active = self.request.query_params.get('is_active', '')
        is_on_leave = self.request.query_params.get('is_on_leave', '')
        
        # Apply filters
        if name:
            queryset = queryset.filter(
                Q(user__first_name__icontains=name) |
                Q(user__last_name__icontains=name)
            )
        
        if staff_id:
            queryset = queryset.filter(staff_id__icontains=staff_id)
        
        if department and department != 'all':
            queryset = queryset.filter(department=department)
        
        if employment_type and employment_type != 'all':
            queryset = queryset.filter(employment_type=employment_type)
        
        if role and role != 'all':
            queryset = queryset.filter(user__role=role)
        
        if is_active:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        
        if is_on_leave:
            queryset = queryset.filter(is_on_leave=(is_on_leave.lower() == 'true'))
        
        # Apply permission-based filtering
        user = self.request.user
        
        # Non-admin users have limited access
        if user.role not in ['head', 'principal', 'vice_principal', 'accountant', 'secretary']:
            if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
                # Teachers can only see other teaching staff
                queryset = queryset.filter(
                    user__role__in=['teacher', 'form_teacher', 'subject_teacher',
                                   'head', 'principal', 'vice_principal']
                )
            else:
                # Other staff can only see themselves
                queryset = queryset.filter(user=user)
        
        return queryset.order_by('user__first_name')


# =====================
# BULK STAFF CREATION VIEW
# =====================

class BulkStaffCreateView(APIView):
    """
    Create multiple staff in bulk
    
    POST /api/staff/bulk-create/
    
    Permissions: Admin/Principal only
    """
    
    permission_classes = [permissions.IsAuthenticated, CanManageStaff]
    
    def post(self, request):
        """Create multiple staff from bulk data"""
        serializer = BulkStaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        staff_list = serializer.validated_data['staff_list']
        created = []
        errors = []
        
        with transaction.atomic():
            for i, staff_data in enumerate(staff_list):
                try:
                    # Extract user data
                    user_data = staff_data.pop('user')
                    
                    # Check if user already exists
                    if User.objects.filter(email=user_data['email']).exists():
                        errors.append({
                            'index': i,
                            'error': f'User with email {user_data["email"]} already exists'
                        })
                        continue
                    
                    # Create user
                    user = User.objects.create_user(**user_data)
                    
                    # Create staff
                    staff = Staff.objects.create(user=user, **staff_data)
                    
                    # Create default permissions
                    StaffPermission.objects.create(staff=staff)
                    
                    # Create teacher profile if user has teaching role
                    if user.role in ['teacher', 'form_teacher', 'subject_teacher',
                                    'head', 'principal', 'vice_principal']:
                        TeacherProfile.objects.create(staff=staff)
                    
                    created.append(staff)
                    
                except Exception as e:
                    errors.append({
                        'index': i,
                        'error': str(e)
                    })
        
        return Response({
            'created_count': len(created),
            'failed_count': len(errors),
            'staff': StaffListSerializer(created, many=True).data,
            'errors': errors
        }, status=status.HTTP_201_CREATED)
        
        
        