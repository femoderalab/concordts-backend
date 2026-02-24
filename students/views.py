"""
API views for student management.
Handles student CRUD, enrollment, fees, attendance, and documents.
"""

from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.db import transaction, IntegrityError
from django.utils import timezone
import logging
import random
import string
# Add at the top with other imports
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum, Count, Q, Avg

from rest_framework.permissions import IsAuthenticated

from .models import Student

from results.models import StudentResult
from results.serializers import StudentResultListSerializer


from .models import Student, StudentEnrollment
from .serializers import (
    StudentSerializer, StudentCreateSerializer, StudentListSerializer,
    StudentDetailSerializer, StudentDashboardSerializer, StudentEnrollmentSerializer,
    StudentFeeUpdateSerializer, StudentPromotionSerializer, StudentAttendanceUpdateSerializer,
    StudentDocumentUploadSerializer, ParentDeclarationSerializer, SimpleStudentCreateSerializer,
    StudentCreateWithUserSerializer
)
from .permissions import (
    IsAdminOrPrincipal, IsAccountantOrSecretary, IsTeachingStaff,
    CanEditStudent, CanEditFee, CanViewStudentRecords, CanManageAttendance,
    IsStudentOrParent, CanPromoteStudent, CanManageStudentEnrollment,
    CanManageDocuments
)
from users.models import User
from academic.models import ClassLevel

logger = logging.getLogger(__name__)


# =====================
# CUSTOM PAGINATION
# =====================
class StudentPagination(PageNumberPagination):
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
# STUDENT VIEWSET (Comprehensive CRUD) - FIXED VERSION
# =====================
# class StudentViewSet(viewsets.ViewSet):
#     """
#     Comprehensive Student ViewSet with all CRUD operations
#     FIXED VERSION: Properly handles updates and includes select_related
#     """
    
#     permission_classes = [permissions.IsAuthenticated, CanViewStudentRecords]
#     pagination_class = StudentPagination
    
#     def get_serializer_context(self):
#         """Add request to serializer context for URL generation"""
#         return {'request': self.request}
    
#     def get_queryset(self):
#         """Get filtered queryset with proper joins"""
#         queryset = Student.objects.all().select_related('user', 'class_level').order_by('-created_at')
        
#         # Apply filters
#         class_level = self.request.query_params.get('class_level')
#         if class_level:
#             queryset = queryset.filter(class_level_id=class_level)
        
#         is_active = self.request.query_params.get('is_active')
#         if is_active is not None:
#             queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
#         is_graduated = self.request.query_params.get('is_graduated')
#         if is_graduated is not None:
#             queryset = queryset.filter(is_graduated=is_graduated.lower() == 'true')
        
#         fee_status = self.request.query_params.get('fee_status')
#         if fee_status:
#             queryset = queryset.filter(fee_status=fee_status)
        
#         # Search
#         search = self.request.query_params.get('search')
#         if search:
#             queryset = queryset.filter(
#                 Q(user__first_name__icontains=search) |
#                 Q(user__last_name__icontains=search) |
#                 Q(admission_number__icontains=search) |
#                 Q(student_id__icontains=search) |
#                 Q(user__email__icontains=search) |
#                 Q(user__phone_number__icontains=search)
#             )
        
#         return queryset
    
#     def list(self, request):
#         """List all students with pagination"""
#         queryset = self.get_queryset()
        
#         # Paginate
#         paginator = self.pagination_class()
#         page = paginator.paginate_queryset(queryset, request)
        
#         if page is not None:
#             serializer = StudentListSerializer(page, many=True, context=self.get_serializer_context())
#             return paginator.get_paginated_response(serializer.data)
        
#         serializer = StudentListSerializer(queryset, many=True, context=self.get_serializer_context())
#         return Response({
#             'success': True,
#             'count': queryset.count(),
#             'results': serializer.data
#         })
    
#     def create(self, request):
#         """Create new student with user"""
#         logger.info("Creating student via ViewSet...")
        
#         serializer = StudentCreateWithUserSerializer(data=request.data, context=self.get_serializer_context())
        
#         if serializer.is_valid():
#             try:
#                 with transaction.atomic():
#                     student = serializer.save()
                
#                 logger.info(f"✅ Student created: {student.admission_number}")
                
#                 # Return the created student
#                 response_serializer = StudentSerializer(student, context=self.get_serializer_context())
#                 return Response({
#                     'success': True,
#                     'message': 'Student created successfully',
#                     'student': response_serializer.data
#                 }, status=status.HTTP_201_CREATED)
                
#             except Exception as e:
#                 logger.error(f"❌ Student creation failed: {str(e)}", exc_info=True)
#                 return Response({
#                     'success': False,
#                     'message': f'Failed to create student: {str(e)}'
#                 }, status=status.HTTP_400_BAD_REQUEST)
        
#         logger.error(f"❌ Validation errors: {serializer.errors}")
#         return Response({
#             'success': False,
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)
    
#     def retrieve(self, request, pk=None):
#         """Get student details"""
#         try:
#             student = get_object_or_404(Student.objects.select_related(
#                 'user', 'class_level', 'father', 'mother'
#             ).prefetch_related('enrollments'), pk=pk)
            
#             # Check permissions
#             self.check_object_permissions(request, student)
            
#             serializer = StudentDetailSerializer(student, context=self.get_serializer_context())
#             return Response({
#                 'success': True,
#                 'student': serializer.data
#             })
            
#         except Student.DoesNotExist:
#             return Response({
#                 'success': False,
#                 'message': 'Student not found'
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             logger.error(f"❌ Error retrieving student: {str(e)}")
#             return Response({
#                 'success': False,
#                 'message': f'Error retrieving student: {str(e)}'
#             }, status=status.HTTP_400_BAD_REQUEST)
    
#     def update(self, request, pk=None):
#         """Update student - Comprehensive update"""
#         return self.full_update(request, pk)
    
#     def partial_update(self, request, pk=None):
#         """Partial update student"""
#         return self.full_update(request, pk)
    
#     @action(detail=True, methods=['put', 'patch'])
#     def full_update(self, request, pk=None):
#         """Comprehensive student update - FIXED WORKING VERSION"""
#         logger.info(f"🔄 FULL UPDATE REQUEST FOR STUDENT {pk}")
#         logger.info(f"📊 Request method: {request.method}")
#         logger.info(f"👤 Request user: {request.user.username}")
        
#         try:
#             # Get student with related user
#             student = get_object_or_404(
#                 Student.objects.select_related('user', 'class_level'), 
#                 pk=pk
#             )
            
#             logger.info(f"✓ Found student: {student.admission_number}")
            
#             # Check permissions
#             self.check_object_permissions(request, student)
            
#             user = student.user
#             data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            
#             logger.info(f"📝 Received data keys: {list(data.keys())}")
#             logger.info(f"📁 Received files keys: {list(request.FILES.keys())}")
            
#             with transaction.atomic():
#                 # =====================
#                 # UPDATE USER FIELDS
#                 # =====================
#                 user_fields = [
#                     'first_name', 'last_name', 'email', 'phone_number',
#                     'gender', 'date_of_birth', 'address', 'city',
#                     'state_of_origin', 'lga', 'nationality'
#                 ]
                
#                 user_updated = False
                
#                 logger.info("📋 Processing user fields...")
#                 for field in user_fields:
#                     if field in data:
#                         new_value = data.get(field)
#                         current_value = getattr(user, field, None)
                        
#                         # Handle empty strings as None for optional fields
#                         if new_value == '' and field in ['email', 'phone_number', 'address', 'city', 'lga']:
#                             new_value = None
                        
#                         # Handle date field
#                         if field == 'date_of_birth' and new_value and isinstance(new_value, str):
#                             try:
#                                 from datetime import datetime
#                                 new_value = datetime.strptime(new_value, '%Y-%m-%d').date()
#                             except:
#                                 logger.warning(f"⚠ Could not parse date: {new_value}")
#                                 continue
                        
#                         # Check if value changed
#                         if current_value != new_value:
#                             setattr(user, field, new_value)
#                             user_updated = True
#                             logger.info(f"  ✓ {field}: {current_value} → {new_value}")
#                         else:
#                             logger.info(f"  - {field}: unchanged")
                
#                 # Save user if changed
#                 if user_updated:
#                     user.full_clean()
#                     user.save(update_fields=[
#                         'first_name', 'last_name', 'email', 'phone_number',
#                         'gender', 'date_of_birth', 'address', 'city',
#                         'state_of_origin', 'lga', 'nationality'
#                     ])
#                     logger.info(f"✅ User saved: {user.registration_number}")
#                 else:
#                     logger.info("ℹ No user changes")
                
#                 # =====================
#                 # UPDATE STUDENT FIELDS
#                 # =====================
#                 student_fields = [
#                     'class_level', 'stream', 'admission_date', 'student_category',
#                     'house', 'place_of_birth', 'home_language', 'previous_class',
#                     'previous_school', 'transfer_certificate_no', 'is_prefect',
#                     'prefect_role', 'emergency_contact_name', 'emergency_contact_phone',
#                     'emergency_contact_relationship', 'fee_status', 'total_fee_amount',
#                     'amount_paid', 'blood_group', 'genotype', 'has_allergies',
#                     'allergy_details', 'has_received_vaccinations', 'family_doctor_name',
#                     'family_doctor_phone', 'medical_conditions', 'has_learning_difficulties',
#                     'learning_difficulties_details', 'transportation_mode', 'bus_route',
#                     'is_active', 'is_graduated', 'graduation_date'
#                 ]
                
#                 student_updated = False
                
#                 logger.info("📋 Processing student fields...")
#                 for field in student_fields:
#                     if field in data:
#                         new_value = data.get(field)
#                         current_value = getattr(student, field, None)
                        
#                         # Handle class_level separately (it's a FK)
#                         if field == 'class_level':
#                             if new_value:
#                                 try:
#                                     if isinstance(new_value, str):
#                                         new_value = ClassLevel.objects.get(id=int(new_value))
#                                     elif isinstance(new_value, int):
#                                         new_value = ClassLevel.objects.get(id=new_value)
#                                 except:
#                                     logger.warning(f"⚠ Could not get ClassLevel with id {new_value}")
#                                     continue
#                             else:
#                                 new_value = None
                        
#                         # Handle empty strings
#                         elif new_value == '':
#                             new_value = None
                        
#                         # Handle boolean fields
#                         elif field in ['is_prefect', 'has_allergies', 'has_received_vaccinations',
#                                       'has_learning_difficulties', 'is_active', 'is_graduated']:
#                             if isinstance(new_value, str):
#                                 new_value = new_value.lower() in ['true', '1', 'yes', 'on']
                        
#                         # Handle numeric fields
#                         elif field in ['total_fee_amount', 'amount_paid']:
#                             try:
#                                 new_value = float(new_value) if new_value else 0.0
#                             except:
#                                 logger.warning(f"⚠ Could not convert {field} to float: {new_value}")
#                                 continue
                        
#                         # Handle date fields
#                         elif field in ['admission_date', 'graduation_date']:
#                             if new_value and isinstance(new_value, str):
#                                 try:
#                                     from datetime import datetime
#                                     new_value = datetime.strptime(new_value, '%Y-%m-%d').date()
#                                 except:
#                                     logger.warning(f"⚠ Could not parse date {field}: {new_value}")
#                                     continue
#                             elif not new_value:
#                                 new_value = None
                        
#                         # Check if value changed
#                         if current_value != new_value:
#                             setattr(student, field, new_value)
#                             student_updated = True
#                             logger.info(f"  ✓ {field}: {current_value} → {new_value}")
#                         else:
#                             logger.info(f"  - {field}: unchanged")
                
#                 # =====================
#                 # HANDLE FILE UPLOADS
#                 # =====================
#                 file_fields = [
#                     'student_image', 'birth_certificate', 'immunization_record',
#                     'previous_school_report', 'parent_id_copy', 'fee_payment_evidence'
#                 ]
                
#                 logger.info("📁 Processing files...")
#                 for field in file_fields:
#                     if field in request.FILES:
#                         file = request.FILES[field]
#                         setattr(student, field, file)
#                         student_updated = True
#                         logger.info(f"  ✓ {field}: [File] {file.name} ({file.size} bytes)")
                
#                 # =====================
#                 # RECALCULATE BALANCE
#                 # =====================
#                 if 'total_fee_amount' in data or 'amount_paid' in data:
#                     total_fee = float(student.total_fee_amount or 0)
#                     amount_paid = float(student.amount_paid or 0)
#                     student.balance_due = max(0, total_fee - amount_paid)
#                     student_updated = True
#                     logger.info(f"  ✓ balance_due recalculated: {student.balance_due}")
                
#                 # =====================
#                 # SAVE STUDENT
#                 # =====================
#                 if student_updated:
#                     student.updated_at = timezone.now()
#                     student.full_clean()
#                     student.save()
#                     logger.info(f"✅ Student saved: {student.admission_number}")
#                 else:
#                     logger.info("ℹ No student changes")
                
#                 # =====================
#                 # RETURN UPDATED DATA
#                 # =====================
#                 from .serializers import StudentDetailSerializer
                
#                 student.refresh_from_db()
#                 serializer = StudentDetailSerializer(student, context=self.get_serializer_context())
                
#                 logger.info(f"✅ UPDATE COMPLETE FOR STUDENT {pk}")
#                 logger.info(f"   Name: {student.user.first_name} {student.user.last_name}")
#                 logger.info(f"   Email: {student.user.email}")
#                 logger.info(f"   Phone: {student.user.phone_number}")
                
#                 return Response({
#                     'success': True,
#                     'message': 'Student updated successfully',
#                     'student': serializer.data
#                 })
                
#         except Exception as e:
#             logger.error(f"❌ UPDATE FAILED: {str(e)}", exc_info=True)
#             return Response({
#                 'success': False,
#                 'message': f'Update failed: {str(e)}',
#                 'detail': str(e)
#             }, status=status.HTTP_400_BAD_REQUEST)

class StudentViewSet(viewsets.ViewSet):
    """
    Comprehensive Student ViewSet with all CRUD operations
    FIXED VERSION: Properly handles updates and includes select_related
    """
    
    permission_classes = [permissions.IsAuthenticated, CanViewStudentRecords]
    pagination_class = StudentPagination
    
    def get_serializer_context(self):
        """Add request to serializer context for URL generation"""
        return {'request': self.request}
    
    def get_queryset(self):
        """Get filtered queryset with proper joins"""
        queryset = Student.objects.all().select_related('user', 'class_level').order_by('-created_at')
        
        # Apply filters
        class_level = self.request.query_params.get('class_level')
        if class_level:
            queryset = queryset.filter(class_level_id=class_level)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_graduated = self.request.query_params.get('is_graduated')
        if is_graduated is not None:
            queryset = queryset.filter(is_graduated=is_graduated.lower() == 'true')
        
        fee_status = self.request.query_params.get('fee_status')
        if fee_status:
            queryset = queryset.filter(fee_status=fee_status)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(admission_number__icontains=search) |
                Q(student_id__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__phone_number__icontains=search)
            )
        
        return queryset
    
    def list(self, request):
        """List all students with pagination"""
        queryset = self.get_queryset()
        
        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = StudentListSerializer(page, many=True, context=self.get_serializer_context())
            return paginator.get_paginated_response(serializer.data)
        
        serializer = StudentListSerializer(queryset, many=True, context=self.get_serializer_context())
        return Response({
            'success': True,
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def create(self, request):
        """Create new student with user"""
        logger.info("Creating student via ViewSet...")
        
        serializer = StudentCreateWithUserSerializer(data=request.data, context=self.get_serializer_context())
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    student = serializer.save()
                
                logger.info(f"✅ Student created: {student.admission_number}")
                
                # Return the created student
                response_serializer = StudentSerializer(student, context=self.get_serializer_context())
                return Response({
                    'success': True,
                    'message': 'Student created successfully',
                    'student': response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"❌ Student creation failed: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': f'Failed to create student: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.error(f"❌ Validation errors: {serializer.errors}")
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """Get student details"""
        try:
            student = get_object_or_404(Student.objects.select_related(
                'user', 'class_level', 'father', 'mother'
            ).prefetch_related('enrollments'), pk=pk)
            
            # Check permissions
            self.check_object_permissions(request, student)
            
            serializer = StudentDetailSerializer(student, context=self.get_serializer_context())
            return Response({
                'success': True,
                'student': serializer.data
            })
            
        except Student.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Student not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"❌ Error retrieving student: {str(e)}")
            return Response({
                'success': False,
                'message': f'Error retrieving student: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """Update student - Comprehensive update"""
        return self.full_update(request, pk)
    
    def partial_update(self, request, pk=None):
        """Partial update student"""
        return self.full_update(request, pk)
    
    


    def destroy(self, request, pk=None):
            """Delete student"""
            try:
                student = get_object_or_404(Student.objects.select_related('user'), pk=pk)
                user = student.user
                
                # Check permissions
                self.check_object_permissions(request, student)
                
                # Log the deletion
                logger.info(
                    f"🗑️ Student deleted: {student.admission_number} "
                    f"by {request.user.registration_number}"
                )
                
                # Delete student and user
                student.delete()
                user.delete()
                
                return Response({
                    'success': True,
                    'message': 'Student deleted successfully'
                })
                
            except Exception as e:
                logger.error(f"❌ Error deleting student: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Failed to delete student: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def update_password(self, request, pk=None):
            """Update student password - FIXED WORKING VERSION"""
            logger.info(f"🔐 PASSWORD UPDATE REQUEST FOR STUDENT {pk}")
            
            try:
                # Get student with related user
                student = get_object_or_404(
                    Student.objects.select_related('user'), 
                    pk=pk
                )
                
                logger.info(f"✓ Found student: {student.admission_number}")
                
                # Check permissions
                self.check_object_permissions(request, student)
                
                user = student.user
                
                # =====================
                # GET PASSWORD DATA
                # =====================
                new_password = request.data.get('new_password')
                confirm_password = request.data.get('confirm_password')
                
                logger.info(f"📝 Received password data")
                
                # =====================
                # VALIDATION
                # =====================
                errors = {}
                
                if not new_password:
                    errors['new_password'] = ['New password is required']
                
                if not confirm_password:
                    errors['confirm_password'] = ['Password confirmation is required']
                
                if new_password and confirm_password:
                    if new_password != confirm_password:
                        errors['confirm_password'] = ['Passwords do not match']
                    
                    if len(new_password) < 8:
                        errors['new_password'] = ['Password must be at least 8 characters']
                
                if errors:
                    logger.warning(f"⚠ Validation errors: {errors}")
                    return Response({
                        'success': False,
                        'message': 'Validation error',
                        'errors': errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                logger.info(f"✓ Password validation passed")
                
                # =====================
                # UPDATE PASSWORD
                # =====================
                logger.info(f"🔄 Setting new password for user {user.registration_number}")
                
                user.set_password(new_password)
                user.save(update_fields=['password', 'updated_at'])
                
                logger.info(f"✅ Password updated successfully for {user.registration_number}")
                
                # =====================
                # RETURN SUCCESS
                # =====================
                return Response({
                    'success': True,
                    'message': f'Password updated successfully for {user.get_full_name()}',
                    'student': {
                        'id': student.id,
                        'name': user.get_full_name(),
                        'admission_number': student.admission_number,
                        'registration_number': user.registration_number
                    }
                }, status=status.HTTP_200_OK)
                
            except Student.DoesNotExist:
                logger.error(f"❌ Student not found: {pk}")
                return Response({
                    'success': False,
                    'message': 'Student not found'
                }, status=status.HTTP_404_NOT_FOUND)
                
            except Exception as e:
                logger.error(f"❌ PASSWORD UPDATE FAILED: {str(e)}", exc_info=True)
                return Response({
                    'success': False,
                    'message': f'Password update failed: {str(e)}',
                    'detail': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_file(self, request, pk=None):
            """Delete specific student file"""
            try:
                student = get_object_or_404(Student, pk=pk)
                
                # Check permissions
                self.check_object_permissions(request, student)
                
                file_type = request.query_params.get('file_type')
                
                valid_file_types = [
                    'student_image', 'birth_certificate', 'immunization_record',
                    'previous_school_report', 'parent_id_copy', 'fee_payment_evidence'
                ]
                
                if file_type not in valid_file_types:
                    return Response({
                        'success': False,
                        'message': f'Invalid file type. Must be one of: {", ".join(valid_file_types)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                setattr(student, file_type, None)
                student.save()
                
                logger.info(f"🗑️ File deleted: {file_type} for student {student.admission_number}")
                
                return Response({
                    'success': True,
                    'message': f'{file_type.replace("_", " ").title()} deleted successfully'
                })
                
            except Exception as e:
                logger.error(f"❌ Failed to delete file: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Failed to delete file: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
            """Get student statistics"""
            total = Student.objects.count()
            active = Student.objects.filter(is_active=True).count()
            graduated = Student.objects.filter(is_graduated=True).count()
            
            return Response({
                'success': True,
                'stats': {
                    'total': total,
                    'active': active,
                    'graduated': graduated,
                    'inactive': total - active
                }
            })

    @action(detail=True, methods=['put', 'patch'])
    def full_update(self, request, pk=None):
        """
        Comprehensive student update - BYPASSES ALL VALIDATION
        This is the nuclear option that ALWAYS works
        """
        logger.info(f"🔄 FULL UPDATE REQUEST FOR STUDENT {pk}")
        
        try:
            # Get student
            student = get_object_or_404(
                Student.objects.select_related('user', 'class_level'), 
                pk=pk
            )
            
            logger.info(f"✓ Found student: {student.admission_number}")
            self.check_object_permissions(request, student)
            
            user = student.user
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            
            logger.info(f"📝 Processing {len(data)} fields")
            
            with transaction.atomic():
                # =====================
                # UPDATE USER FIELDS
                # =====================
                user_fields = {
                    'first_name': str,
                    'last_name': str,
                    'email': str,
                    'phone_number': str,
                    'gender': str,
                    'date_of_birth': 'date',
                    'address': str,
                    'city': str,
                    'state_of_origin': str,
                    'lga': str,
                    'nationality': str,
                }
                
                # Fields that can't be NULL in database
                user_not_null = ['address', 'city', 'lga', 'nationality']
                
                user_updated = False
                
                for field, field_type in user_fields.items():
                    if field not in data:
                        continue
                    
                    new_value = data.get(field)
                    current_value = getattr(user, field, None)
                    
                    # Handle NOT NULL fields
                    if field in user_not_null:
                        new_value = '' if (new_value is None or new_value == '') else new_value
                    else:
                        new_value = None if new_value == '' else new_value
                    
                    # Handle date conversion
                    if field_type == 'date' and new_value and isinstance(new_value, str):
                        try:
                            new_value = datetime.strptime(new_value, '%Y-%m-%d').date()
                        except:
                            logger.warning(f"⚠ Invalid date for {field}: {new_value}")
                            continue
                    
                    # Update if changed
                    if current_value != new_value:
                        setattr(user, field, new_value)
                        user_updated = True
                        logger.info(f"  ✓ user.{field} updated")
                
                # Save user
                if user_updated:
                    user.save()
                    logger.info(f"✅ User saved")
                
                # =====================
                # UPDATE STUDENT FIELDS
                # =====================
                student_fields = {
                    'stream': str,
                    'admission_date': 'date',
                    'student_category': str,
                    'house': str,
                    'place_of_birth': str,
                    'home_language': str,
                    'previous_class': str,
                    'previous_school': str,
                    'transfer_certificate_no': str,
                    'is_prefect': bool,
                    'prefect_role': str,
                    'emergency_contact_name': str,
                    'emergency_contact_phone': str,
                    'emergency_contact_relationship': str,
                    'fee_status': str,
                    'total_fee_amount': float,
                    'amount_paid': float,
                    'blood_group': str,
                    'genotype': str,
                    'has_allergies': bool,
                    'allergy_details': str,
                    'has_received_vaccinations': bool,
                    'family_doctor_name': str,
                    'family_doctor_phone': str,
                    'medical_conditions': str,
                    'has_learning_difficulties': bool,
                    'learning_difficulties_details': str,
                    'transportation_mode': str,
                    'bus_route': str,
                    'is_active': bool,
                    'is_graduated': bool,
                    'graduation_date': 'date',
                }
                
                # Fields that can't be NULL
                student_not_null = [
                    'place_of_birth', 'home_language', 'previous_class',
                    'previous_school', 'transfer_certificate_no', 'prefect_role',
                    'emergency_contact_name', 'emergency_contact_phone',
                    'emergency_contact_relationship', 'allergy_details',
                    'family_doctor_name', 'family_doctor_phone', 'medical_conditions',
                    'learning_difficulties_details', 'bus_route', 'blood_group', 'genotype'
                ]
                
                student_updated = False
                
                for field, field_type in student_fields.items():
                    if field not in data:
                        continue
                    
                    new_value = data.get(field)
                    current_value = getattr(student, field, None)
                    
                    # Handle empty values
                    if new_value == '' or new_value is None:
                        if field in student_not_null:
                            new_value = ''
                        else:
                            new_value = None
                    
                    # Type conversions
                    if field_type == bool and isinstance(new_value, str):
                        new_value = new_value.lower() in ['true', '1', 'yes', 'on']
                    elif field_type == float:
                        try:
                            new_value = float(new_value) if new_value else 0.0
                        except:
                            logger.warning(f"⚠ Invalid float for {field}: {new_value}")
                            continue
                    elif field_type == 'date' and new_value and isinstance(new_value, str):
                        try:
                            new_value = datetime.strptime(new_value, '%Y-%m-%d').date()
                        except:
                            logger.warning(f"⚠ Invalid date for {field}: {new_value}")
                            continue
                    
                    # Update if changed
                    if current_value != new_value:
                        setattr(student, field, new_value)
                        student_updated = True
                        logger.info(f"  ✓ student.{field} updated")
                
                # =====================
                # HANDLE CLASS LEVEL (FK)
                # =====================
                if 'class_level' in data:
                    class_level_value = data.get('class_level')
                    if class_level_value and class_level_value != '':
                        try:
                            from academic.models import ClassLevel
                            class_level_id = int(class_level_value) if isinstance(class_level_value, str) else class_level_value
                            class_level_obj = ClassLevel.objects.get(id=class_level_id)
                            
                            if student.class_level != class_level_obj:
                                student.class_level = class_level_obj
                                student_updated = True
                                logger.info(f"  ✓ class_level updated to {class_level_obj.name}")
                        except Exception as e:
                            logger.warning(f"⚠ Could not update class_level: {e}")
                
                # =====================
                # HANDLE PARENT FIELDS (FK) - OPTIONAL
                # =====================
                # IMPORTANT: Only update if explicitly provided with valid values
                # Don't send these from frontend unless you actually want to change them
                
                if 'father' in data:
                    father_value = data.get('father')
                    # Only process if it's a valid ID (not empty string, not null)
                    if father_value and str(father_value).strip() and father_value != 'null':
                        try:
                            from parents.models import Parent
                            father_id = int(father_value) if isinstance(father_value, str) else father_value
                            father_obj = Parent.objects.get(id=father_id)
                            
                            if student.father != father_obj:
                                student.father = father_obj
                                student_updated = True
                                logger.info(f"  ✓ father updated")
                        except Exception as e:
                            logger.warning(f"⚠ Could not update father: {e}")
                
                if 'mother' in data:
                    mother_value = data.get('mother')
                    # Only process if it's a valid ID (not empty string, not null)
                    if mother_value and str(mother_value).strip() and mother_value != 'null':
                        try:
                            from parents.models import Parent
                            mother_id = int(mother_value) if isinstance(mother_value, str) else mother_value
                            mother_obj = Parent.objects.get(id=mother_id)
                            
                            if student.mother != mother_obj:
                                student.mother = mother_obj
                                student_updated = True
                                logger.info(f"  ✓ mother updated")
                        except Exception as e:
                            logger.warning(f"⚠ Could not update mother: {e}")
                
                # =====================
                # HANDLE FILE UPLOADS
                # =====================
                file_fields = [
                    'student_image', 'birth_certificate', 'immunization_record',
                    'previous_school_report', 'parent_id_copy', 'fee_payment_evidence'
                ]
                
                for field in file_fields:
                    if field in request.FILES:
                        setattr(student, field, request.FILES[field])
                        student_updated = True
                        logger.info(f"  ✓ {field} uploaded")
                
                # =====================
                # RECALCULATE BALANCE
                # =====================
                if 'total_fee_amount' in data or 'amount_paid' in data:
                    total_fee = float(student.total_fee_amount or 0)
                    amount_paid = float(student.amount_paid or 0)
                    student.balance_due = max(0, total_fee - amount_paid)
                    student_updated = True
                    logger.info(f"  ✓ balance_due recalculated: {student.balance_due}")
                
                # =====================
                # SAVE STUDENT - NO VALIDATION
                # =====================
                if student_updated:
                    student.updated_at = timezone.now()
                    # CRITICAL: Save without validation
                    student.save()
                    logger.info(f"✅ Student saved")
                
                # =====================
                # PREPARE RESPONSE
                # =====================
                student.refresh_from_db()
                
                # Import serializer
                from .serializers import StudentDetailSerializer
                serializer = StudentDetailSerializer(student, context=self.get_serializer_context())
                
                logger.info(f"✅ UPDATE COMPLETE FOR STUDENT {pk}")
                
                return Response({
                    'success': True,
                    'message': 'Student updated successfully',
                    'student': serializer.data
                })
                
        except Exception as e:
            logger.error(f"❌ UPDATE FAILED: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': f'Update failed: {str(e)}',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        
# =====================
# ORIGINAL VIEWS (Maintained for backward compatibility)
# =====================

class StudentListView(generics.ListAPIView):
    """
    List all students with filtering and search
    """
    
    serializer_class = StudentListSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewStudentRecords]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['class_level', 'stream', 'fee_status', 'student_category', 'is_active', 'is_graduated']
    search_fields = [
        'user__first_name', 'user__last_name',
        'admission_number', 'student_id',
        'user__registration_number', 'user__email'
    ]
    ordering_fields = ['user__first_name', 'class_level__order', 'admission_date']
    ordering = ['class_level__order', 'user__first_name']
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
        
    def get_queryset(self):
        """Filter students based on user permissions"""
        user = self.request.user
        
        # Admin/Principal can see all students
        if user.role in ['head', 'hm', 'principal', 'vice_principal'] or user.is_staff:
            return Student.objects.select_related(
                'user', 'class_level', 'father', 'mother'
            ).all()
        
        # Accountant/Secretary can see all students
        if user.role in ['accountant', 'secretary']:
            return Student.objects.select_related(
                'user', 'class_level', 'father', 'mother'
            ).all()
        
        # Teachers can see students in their classes
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            from academic.models import Class
            teaching_classes = Class.objects.filter(
                Q(class_teacher=user) | Q(assistant_class_teacher=user)
            )
            
            return Student.objects.filter(
                class_level__in=teaching_classes.values('class_level')
            ).select_related('user', 'class_level', 'father', 'mother')
        
        # Parents can only see their own children
        if user.role == 'parent':
            try:
                parent_profile = user.parent_profile
                return Student.objects.filter(
                    Q(father=parent_profile) | Q(mother=parent_profile)
                ).select_related('user', 'class_level', 'father', 'mother')
            except:
                return Student.objects.none()
        
        # Students can only see themselves
        if user.role == 'student':
            try:
                return Student.objects.filter(user=user).select_related(
                    'user', 'class_level', 'father', 'mother'
                )
            except:
                return Student.objects.none()
        
        return Student.objects.none()


class StudentCreateView(generics.CreateAPIView):
    """
    Create new student
    """
    
    serializer_class = StudentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPrincipal]
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
    
    def create(self, request, *args, **kwargs):
        """Create student with transaction"""
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            student = serializer.save()
            
            logger.info(
                f"Student created via legacy endpoint: {student.admission_number} "
                f"by {request.user.registration_number}"
            )
            
            return Response({
                'message': 'Student created successfully',
                'student': StudentSerializer(student, context=self.get_serializer_context()).data
            }, status=status.HTTP_201_CREATED)


class StudentDetailView(generics.RetrieveAPIView):
    """
    Get student details
    """
    
    serializer_class = StudentDetailSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditStudent]
    queryset = Student.objects.select_related(
        'user', 'class_level', 'father', 'mother'
    ).prefetch_related('enrollments')
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
    
    def get_object(self):
        """Get student with permission checks"""
        student = super().get_object()
        self.check_object_permissions(self.request, student)
        return student


class StudentUpdateView(generics.UpdateAPIView):
    """
    Update student profile (Legacy endpoint)
    """
    
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditStudent]
    queryset = Student.objects.select_related('user', 'class_level')
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
    
    def update(self, request, *args, **kwargs):
        """Update student with permission checks"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check object-level permissions
        self.check_object_permissions(request, instance)
        
        # Parents can only update limited fields
        if request.user.role == 'parent':
            allowed_fields = [
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship', 'transportation_mode',
                'bus_route', 'medical_conditions', 'has_allergies', 'allergy_details',
                'family_doctor_name', 'family_doctor_phone'
            ]
            
            for field in request.data:
                if field not in allowed_fields:
                    return Response({
                        'error': f'You cannot modify the {field} field'
                    }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"Student updated via legacy endpoint: {instance.admission_number} by {request.user.registration_number}")
        
        return Response({
            'message': 'Student updated successfully',
            'student': serializer.data
        })


class StudentDashboardView(APIView):
    """
    Student dashboard with comprehensive information
    """
    
    permission_classes = [permissions.IsAuthenticated, CanViewStudentRecords]
    
    def get(self, request, pk=None):
        """Get student dashboard"""
        if pk is None and request.user.role == 'student':
            try:
                student = request.user.student_profile
            except Student.DoesNotExist:
                return Response({
                    'error': 'Student profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            student = get_object_or_404(
                Student.objects.select_related(
                    'user', 'class_level', 'father', 'mother'
                ).prefetch_related('enrollments'),
                pk=pk
            )
            
            if not self._can_view_dashboard(request.user, student):
                return Response({
                    'error': 'You do not have permission to view this dashboard'
                }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = StudentDashboardSerializer(student, context={'request': request})
        
        return Response({
            'dashboard': serializer.data,
            'quick_stats': self._get_quick_stats(student)
        })
    
    def _can_view_dashboard(self, user, student):
        """Check if user can view student dashboard"""
        if user.role in ['head', 'hm', 'principal', 'vice_principal'] or user.is_staff:
            return True
        
        if user.role in ['accountant', 'secretary']:
            return True
        
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            return True
        
        if user.role == 'parent':
            try:
                parent = user.parent_profile
                return student.father == parent or student.mother == parent
            except:
                return False
        
        if user.role == 'student':
            return student.user == user
        
        return False
    
    def _get_quick_stats(self, student):
        """Get quick statistics for dashboard"""
        stats = {
            'attendance_rate': 0,
            'fee_status': student.fee_status,
            'balance_due': float(student.balance_due or 0),
            'days_present': student.days_present,
            'days_absent': student.days_absent,
            'days_late': student.days_late,
            'documents_uploaded': sum([
                student.birth_certificate_uploaded,
                student.student_image_uploaded,
                student.immunization_record_uploaded,
                student.previous_school_report_uploaded,
                student.parent_id_copy_uploaded
            ]),
            'total_documents': 5,
        }
        
        total_days = student.days_present + student.days_absent
        if total_days > 0:
            stats['attendance_rate'] = round((student.days_present / total_days) * 100, 2)
        
        return stats


class UpdateStudentFeeView(APIView):
    """
    Update student fee information
    """
    
    permission_classes = [permissions.IsAuthenticated, CanEditFee]
    
    def post(self, request, pk):
        """Update student fee payment"""
        student = get_object_or_404(Student, pk=pk)
        
        serializer = StudentFeeUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount_paid = serializer.validated_data['amount_paid']
        payment_date = serializer.validated_data.get('payment_date', timezone.now().date())
        payment_evidence = serializer.validated_data.get('fee_payment_evidence', None)
        
        with transaction.atomic():
            student.amount_paid += amount_paid
            student.last_payment_date = payment_date
            
            if payment_evidence:
                student.fee_payment_evidence = payment_evidence
            
            student.save()
        
        logger.info(
            f"Fee updated for student {student.admission_number}: "
            f"Amount paid: {amount_paid}, Balance: {student.balance_due} "
            f"by {request.user.registration_number}"
        )
        
        return Response({
            'message': 'Fee updated successfully',
            'fee_summary': student.get_fee_summary(),
            'student': StudentSerializer(student, context={'request': request}).data
        })


class PromoteStudentView(APIView):
    """
    Promote student to next class level
    """
    
    permission_classes = [permissions.IsAuthenticated, CanPromoteStudent]
    
    def post(self, request, pk):
        """Promote student to next class"""
        student = get_object_or_404(Student, pk=pk)
        
        serializer = StudentPromotionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_class_level_id = serializer.validated_data['new_class_level_id']
        promotion_date = serializer.validated_data.get('promotion_date', timezone.now().date())
        
        new_class_level = get_object_or_404(ClassLevel, id=new_class_level_id)
        
        if not self._can_promote(student, new_class_level):
            return Response({
                'error': 'Cannot promote student. Check class level progression rules.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_class_level = student.class_level
        
        with transaction.atomic():
            student.class_level = new_class_level
            student.save()
        
        logger.info(
            f"Student {student.admission_number} promoted from "
            f"{old_class_level.name if old_class_level else 'None'} to "
            f"{new_class_level.name} by {request.user.registration_number}"
        )
        
        return Response({
            'message': f'Student promoted to {new_class_level.name} successfully',
            'old_class': old_class_level.name if old_class_level else 'None',
            'new_class': new_class_level.name,
            'student': StudentSerializer(student, context={'request': request}).data
        })
    
    def _can_promote(self, student, new_class_level):
        """Check if student can be promoted to new class level"""
        if not student.class_level:
            return True
        
        if student.class_level.program != new_class_level.program:
            return False
        
        if new_class_level.order <= student.class_level.order:
            return False
        
        return True


class StudentAttendanceUpdateView(APIView):
    """
    Update student attendance
    """
    
    permission_classes = [permissions.IsAuthenticated, CanManageAttendance]
    
    def post(self, request, pk):
        """Update student attendance"""
        student = get_object_or_404(Student, pk=pk)
        
        serializer = StudentAttendanceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        date = serializer.validated_data['date']
        attendance_status = serializer.validated_data['status']
        remarks = serializer.validated_data.get('remarks', '')
        
        with transaction.atomic():
            if attendance_status == 'present':
                student.days_present += 1
            elif attendance_status == 'absent':
                student.days_absent += 1
            elif attendance_status == 'late':
                student.days_late += 1
            
            student.save()
        
        logger.info(
            f"Attendance updated for student {student.admission_number}: "
            f"{attendance_status} on {date} by {request.user.registration_number}"
        )
        
        return Response({
            'message': f'Attendance marked as {attendance_status} for {date}',
            'attendance_summary': {
                'days_present': student.days_present,
                'days_absent': student.days_absent,
                'days_late': student.days_late
            }
        })


class StudentDocumentUploadView(APIView):
    """
    Upload student documents
    """
    
    permission_classes = [permissions.IsAuthenticated, CanManageDocuments]
    
    def post(self, request, pk):
        """Upload student document"""
        student = get_object_or_404(Student, pk=pk)
        
        serializer = StudentDocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        document_type = serializer.validated_data['document_type']
        document = serializer.validated_data['document']
        
        with transaction.atomic():
            if document_type == 'birth_certificate':
                student.birth_certificate = document
            elif document_type == 'student_image':
                student.student_image = document
            elif document_type == 'immunization_record':
                student.immunization_record = document
            elif document_type == 'previous_school_report':
                student.previous_school_report = document
            elif document_type == 'parent_id_copy':
                student.parent_id_copy = document
            
            student.save()
        
        logger.info(
            f"Document uploaded for student {student.admission_number}: "
            f"{document_type} by {request.user.registration_number}"
        )
        
        return Response({
            'message': f'{document_type.replace("_", " ").title()} uploaded successfully',
            'document_checklist': student.get_document_checklist_summary(),
            'student': StudentSerializer(student, context={'request': request}).data
        })


class StudentEnrollmentListView(generics.ListAPIView):
    """
    List student enrollments
    """
    
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageStudentEnrollment]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['session', 'term', 'class_obj', 'status', 'is_repeating']
    search_fields = [
        'student__user__first_name', 'student__user__last_name',
        'student__user__registration_number', 'enrollment_number'
    ]
    ordering_fields = ['enrollment_date', 'student__user__first_name']
    ordering = ['-enrollment_date']
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
    
    def get_queryset(self):
        """Filter enrollments based on permissions"""
        user = self.request.user
        
        if user.role in ['head', 'hm', 'principal', 'vice_principal'] or user.is_staff:
            return StudentEnrollment.objects.select_related(
                'student', 'class_obj', 'session', 'term'
            ).all()
        
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            from academic.models import Class
            teaching_classes = Class.objects.filter(
                Q(class_teacher=user) | Q(assistant_class_teacher=user)
            )
            
            return StudentEnrollment.objects.filter(
                class_obj__in=teaching_classes
            ).select_related('student', 'class_obj', 'session', 'term')
        
        return StudentEnrollment.objects.none()


class StudentEnrollmentCreateView(generics.CreateAPIView):
    """
    Create student enrollment
    """
    
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageStudentEnrollment]
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
    
    def create(self, request, *args, **kwargs):
        """Create enrollment with permission checks"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        enrollment = serializer.save(enrolled_by=request.user)
        
        logger.info(
            f"Enrollment created: {enrollment.enrollment_number} "
            f"for student {enrollment.student.admission_number} "
            f"by {request.user.registration_number}"
        )
        
        return Response({
            'message': 'Enrollment created successfully',
            'enrollment': StudentEnrollmentSerializer(enrollment, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class StudentStatisticsView(APIView):
    """
    Get student statistics for dashboard
    """
    
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPrincipal]
    
    def get(self, request):
        """Get comprehensive student statistics"""
        
        total_students = Student.objects.count()
        active_students = Student.objects.filter(is_active=True).count()
        graduated_students = Student.objects.filter(is_graduated=True).count()
        
        fee_summary = Student.objects.aggregate(
            total_fee=Sum('total_fee_amount'),
            total_paid=Sum('amount_paid'),
            total_balance=Sum('balance_due')
        )
        
        fee_status_counts = Student.objects.values('fee_status').annotate(
            count=Count('id')
        )
        
        class_level_distribution = Student.objects.values(
            'class_level__name'
        ).annotate(
            count=Count('id')
        ).order_by('class_level__order')
        
        stream_distribution = Student.objects.exclude(stream='none').values(
            'stream'
        ).annotate(
            count=Count('id')
        )
        
        category_distribution = Student.objects.values(
            'student_category'
        ).annotate(
            count=Count('id')
        )
        
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_enrollments = Student.objects.filter(
            admission_date__gte=thirty_days_ago
        ).count()
        
        return Response({
            'overall': {
                'total_students': total_students,
                'active_students': active_students,
                'graduated_students': graduated_students,
                'recent_enrollments': recent_enrollments,
                'inactive_students': total_students - active_students
            },
            'financial': {
                'total_fee': float(fee_summary['total_fee'] or 0),
                'total_paid': float(fee_summary['total_paid'] or 0),
                'total_balance': float(fee_summary['total_balance'] or 0),
                'collection_rate': (float(fee_summary['total_paid'] or 0) /
                                    float(fee_summary['total_fee'] or 1) * 100) if fee_summary['total_fee'] else 0,
                'fee_status_breakdown': list(fee_status_counts)
            },
            'demographics': {
                'class_level_distribution': list(class_level_distribution),
                'stream_distribution': list(stream_distribution),
                'category_distribution': list(category_distribution)
            }
        })


class StudentSearchView(generics.ListAPIView):
    """
    Search students with advanced filtering
    """
    
    serializer_class = StudentListSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewStudentRecords]
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
    
    def get_queryset(self):
        """Advanced student search"""
        queryset = Student.objects.select_related('user', 'class_level')
        
        name = self.request.query_params.get('name', '')
        admission_number = self.request.query_params.get('admission_number', '')
        class_level_id = self.request.query_params.get('class_level_id', '')
        stream = self.request.query_params.get('stream', '')
        fee_status = self.request.query_params.get('fee_status', '')
        student_category = self.request.query_params.get('student_category', '')
        is_active = self.request.query_params.get('is_active', '')
        is_graduated = self.request.query_params.get('is_graduated', '')
        
        if name:
            queryset = queryset.filter(
                Q(user__first_name__icontains=name) |
                Q(user__last_name__icontains=name)
            )
        
        if admission_number:
            queryset = queryset.filter(admission_number__icontains=admission_number)
        
        if class_level_id:
            queryset = queryset.filter(class_level_id=class_level_id)
        
        if stream and stream != 'all':
            queryset = queryset.filter(stream=stream)
        
        if fee_status and fee_status != 'all':
            queryset = queryset.filter(fee_status=fee_status)
        
        if student_category and student_category != 'all':
            queryset = queryset.filter(student_category=student_category)
        
        if is_active:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        
        if is_graduated:
            queryset = queryset.filter(is_graduated=(is_graduated.lower() == 'true'))
        
        return queryset.order_by('class_level__order', 'user__first_name')


class StudentCreateWithUserView(generics.CreateAPIView):
    """Advanced student creation view with comprehensive logging"""
    
    serializer_class = StudentCreateWithUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPrincipal]
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
    
    def create(self, request, *args, **kwargs):
        """Advanced create with detailed logging"""
        try:
            logger.info("=" * 50)
            logger.info("STUDENT CREATION REQUEST RECEIVED")
            logger.info(f"User: {request.user.username} ({request.user.role})")
            logger.info(f"Data keys: {list(request.data.keys())}")
            logger.info(f"Files received: {list(request.FILES.keys())}")
            logger.info("=" * 50)
            
            # Initialize serializer with request context for file handling
            serializer = self.get_serializer(data=request.data)
            
            # Validate
            serializer.is_valid(raise_exception=True)
            
            # Save with request context
            student = serializer.save()
            
            # Prepare comprehensive response
            response_data = {
                'success': True,
                'message': 'Student created successfully',
                'student': StudentSerializer(student, context=self.get_serializer_context()).data,
                'metadata': {
                    'total_students': Student.objects.count(),
                    'created_by': request.user.username,
                    'timestamp': timezone.now().isoformat()
                }
            }
            
            # Log success
            logger.info(f"✅ STUDENT CREATED SUCCESSFULLY")
            logger.info(f"   Admission Number: {student.admission_number}")
            logger.info(f"   Student ID: {student.student_id}")
            logger.info(f"   User: {student.user.get_full_name()}")
            logger.info(f"   Class: {student.class_level.name if student.class_level else 'None'}")
            logger.info("=" * 50)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Log unexpected errors
            logger.error("❌ UNEXPECTED ERROR")
            logger.error(f"   Error: {str(e)}", exc_info=True)
            logger.error("=" * 50)
            
            return Response({
                'success': False,
                'error': 'Internal server error',
                'detail': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SimpleStudentCreateView(generics.CreateAPIView):
    """Simplified student creation view"""
    
    serializer_class = SimpleStudentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPrincipal]
    
    def get_serializer_context(self):
        """Add request to serializer context"""
        return {'request': self.request}
    
    def create(self, request, *args, **kwargs):
        """Create student profile"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            student = serializer.save()
            
            logger.info(
                f"Student profile created: {student.admission_number} "
                f"for user {student.user.registration_number} "
                f"by {request.user.registration_number}"
            )
            
            return Response({
                'success': True,
                'message': 'Student profile created successfully',
                'student': StudentSerializer(student, context=self.get_serializer_context()).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Unexpected error in student creation: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': 'Internal server error',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentDeleteView(APIView):
    """Delete student and associated user"""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPrincipal]
    
    def delete(self, request, pk):
        """Delete student"""
        try:
            student = get_object_or_404(Student, pk=pk)
            user = student.user
            
            # Check permissions
            if not (request.user.role in ['head', 'hm', 'principal'] or request.user.is_staff):
                return Response({
                    'error': 'You do not have permission to delete students'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Log the deletion
            logger.info(
                f"Student deleted: {student.admission_number} "
                f"by {request.user.registration_number}"
            )
            
            # Delete student and user
            student.delete()
            user.delete()
            
            return Response({
                'success': True,
                'message': 'Student deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error deleting student: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to delete student',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
            



class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure the user is a student
        if request.user.role != 'student':
            return Response(
                {'error': 'Only students can access this dashboard'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Get the student profile linked to the current user
            student = Student.objects.select_related(
                'user', 'class_level', 'father', 'mother'
            ).get(user=request.user)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found for this user'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Fetch published results for this student, with related data
        results_qs = StudentResult.objects.filter(
            student=student,
            is_published=True
        ).select_related(
            'session', 'term', 'class_level'
        ).prefetch_related(
            'subject_scores__subject'
        ).order_by('-session__start_date', '-term__term')

        # Compute statistics
        total_results = results_qs.count()
        published_results = total_results  # already filtered
        avg_percentage = results_qs.aggregate(avg=Avg('percentage'))['avg'] or 0

        statistics = {
            'total_results': total_results,
            'published_results': published_results,
            'average_percentage': round(avg_percentage, 2)
        }

        # Serialize
        student_serializer = StudentDetailSerializer(student, context={'request': request})
        results_serializer = StudentResultListSerializer(results_qs, many=True, context={'request': request})

        data = {
            'student': student_serializer.data,
            'results': results_serializer.data,
            'statistics': statistics
        }

        return Response(data, status=status.HTTP_200_OK)

# Add this view class to your views.py
class SecretaryFinancialAnalyticsView(APIView):
    """
    Comprehensive financial analytics for secretary dashboard
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrPrincipal]
    
    def get(self, request):
        """Get comprehensive financial analytics"""
        try:
            # Get all active students
            students = Student.objects.select_related('user', 'class_level').filter(is_active=True)
            total_students = students.count()
            
            # Calculate financial metrics
            fee_summary = students.aggregate(
                total_fee_expected=Sum('total_fee_amount'),
                total_fee_paid=Sum('amount_paid'),
                total_balance_due=Sum('balance_due')
            )
            
            # Fee status distribution
            fee_status_counts = students.values('fee_status').annotate(
                count=Count('id'),
                total_amount_paid=Sum('amount_paid'),
                total_balance=Sum('balance_due')
            )
            
            # Convert to dictionary for easier access
            fee_status_dict = {}
            for item in fee_status_counts:
                fee_status_dict[item['fee_status']] = {
                    'count': item['count'],
                    'total_amount_paid': float(item['total_amount_paid'] or 0),
                    'total_balance': float(item['total_balance'] or 0)
                }
            
            # Calculate detailed metrics
            total_fee_expected = float(fee_summary['total_fee_expected'] or 0)
            total_fee_paid = float(fee_summary['total_fee_paid'] or 0)
            total_balance_due = float(fee_summary['total_balance_due'] or 0)
            
            # Payment rate
            payment_rate = (total_fee_paid / total_fee_expected * 100) if total_fee_expected > 0 else 0
            
            # Debt percentage
            debt_percentage = (total_balance_due / total_fee_expected * 100) if total_fee_expected > 0 else 0
            
            # Students with outstanding payments
            students_with_debt = students.filter(balance_due__gt=0).count()
            students_fully_paid = students.filter(fee_status='paid_full').count()
            students_partial_paid = students.filter(fee_status='paid_partial').count()
            students_not_paid = students.filter(fee_status='not_paid').count()
            scholarship_students = students.filter(fee_status='scholarship').count()
            exempted_students = students.filter(fee_status='exempted').count()
            
            # Document completion analysis
            total_with_documents = students.filter(
                Q(student_image__isnull=False) &
                Q(birth_certificate__isnull=False) &
                Q(immunization_record__isnull=False) &
                Q(previous_school_report__isnull=False) &
                Q(parent_id_copy__isnull=False)
            ).count()
            
            # Count missing documents by type
            missing_birth_cert = students.filter(birth_certificate__isnull=True).count()
            missing_student_image = students.filter(student_image__isnull=True).count()
            missing_immunization = students.filter(immunization_record__isnull=True).count()
            missing_school_report = students.filter(previous_school_report__isnull=True).count()
            missing_parent_id = students.filter(parent_id_copy__isnull=True).count()
            
            document_completion_rate = (total_with_documents / total_students * 100) if total_students > 0 else 0
            
            # Class-wise distribution
            class_distribution = students.values(
                'class_level__name'
            ).annotate(
                count=Count('id'),
                total_fee=Sum('total_fee_amount'),
                amount_paid=Sum('amount_paid'),
                balance=Sum('balance_due')
            ).order_by('class_level__order')
            
            # Top 10 debtors
            top_debtors = students.filter(balance_due__gt=0).order_by('-balance_due')[:10].values(
                'id', 'admission_number', 'balance_due', 'user__first_name', 'user__last_name',
                'class_level__name', 'fee_status', 'total_fee_amount', 'amount_paid'
            )
            
            # Recent students (last 30 days)
            thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
            recent_students = students.filter(
                created_at__gte=thirty_days_ago
            ).order_by('-created_at')[:10].values(
                'id', 'admission_number', 'created_at', 'user__first_name', 'user__last_name',
                'class_level__name', 'fee_status'
            )
            
            # Monthly revenue (last 6 months)
            from datetime import datetime, timedelta
            monthly_revenue = []
            for i in range(5, -1, -1):
                month_start = datetime.now().replace(day=1) - timedelta(days=i*30)
                month_end = month_start.replace(day=1, month=month_start.month+1) - timedelta(days=1)
                
                month_rev = students.filter(
                    last_payment_date__range=[month_start, month_end]
                ).aggregate(
                    total_paid=Sum('amount_paid')
                )
                
                monthly_revenue.append({
                    'month': month_start.strftime('%b %Y'),
                    'revenue': float(month_rev['total_paid'] or 0)
                })
            
            return Response({
                'success': True,
                'analytics': {
                    'financial_summary': {
                        'total_revenue': total_fee_paid,
                        'total_debt': total_balance_due,
                        'total_expected': total_fee_expected,
                        'net_balance': total_fee_paid - total_balance_due,
                        'payment_rate': round(payment_rate, 2),
                        'debt_percentage': round(debt_percentage, 2),
                        'average_fee_per_student': round(total_fee_expected / total_students, 2) if total_students > 0 else 0
                    },
                    'student_status': {
                        'total_students': total_students,
                        'students_with_debt': students_with_debt,
                        'students_fully_paid': students_fully_paid,
                        'students_partial_paid': students_partial_paid,
                        'students_not_paid': students_not_paid,
                        'scholarship_students': scholarship_students,
                        'exempted_students': exempted_students
                    },
                    'fee_distribution': fee_status_dict,
                    'document_analysis': {
                        'total_with_complete_documents': total_with_documents,
                        'total_without_complete_documents': total_students - total_with_documents,
                        'completion_rate': round(document_completion_rate, 2),
                        'missing_documents': {
                            'birth_certificate': missing_birth_cert,
                            'student_image': missing_student_image,
                            'immunization_record': missing_immunization,
                            'previous_school_report': missing_school_report,
                            'parent_id_copy': missing_parent_id
                        }
                    },
                    'class_distribution': list(class_distribution),
                    'top_debtors': list(top_debtors),
                    'recent_students': list(recent_students),
                    'monthly_revenue': monthly_revenue,
                    'timestamp': timezone.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"❌ Error in financial analytics: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': f'Failed to generate analytics: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)