"""
Views for Results App - UPDATED FOR class_level VERSION
"""

from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Max, Min, Count, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
import json

from .models import (
    StudentResult, SubjectScore, PsychomotorSkills, 
    AffectiveDomains, ResultPublishing
)
from .serializers import (
    StudentResultSerializer, SubjectScoreSerializer,
    PsychomotorSkillsSerializer, AffectiveDomainsSerializer,
    ResultPublishingSerializer, BulkResultUploadSerializer,
    SubjectScoreBulkSerializer, StudentResultListSerializer,
    SubjectScoreListSerializer, ReportCardSerializer
)

# Import only the permissions that actually exist
from .permissions import (
    CanViewResults, CanManageResults, CanPublishResults,
    CanApproveResults, StudentResultPermission,
    CanAccessResultStatistics, CanBulkUploadResults
)

# Import related models
from students.models import Student
from academic.models import AcademicSession, AcademicTerm, ClassLevel, Subject
from users.models import User


# ============================================
# STUDENT RESULT VIEWSET
# ============================================

class StudentResultViewSet(viewsets.ModelViewSet):
    """ViewSet for managing student results"""
    
    queryset = StudentResult.objects.select_related(
        'student', 'student__user', 'session', 'term', 
        'class_level', 'class_teacher', 'headmaster', 'created_by'
    ).prefetch_related(
        'subject_scores', 'subject_scores__subject',
        'psychomotor_skills', 'affective_domains'
    ).order_by('-created_at')
    
    serializer_class = StudentResultSerializer
    permission_classes = [IsAuthenticated, CanManageResults]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'student', 'session', 'term', 'class_level',
        'is_published', 'is_promoted', 'overall_grade'
    ]
    search_fields = [
        'student__user__first_name', 'student__user__last_name',
        'student__user__registration_number', 'student__admission_number'
    ]
    ordering_fields = [
        'overall_total_score', 'percentage', 'position_in_class',
        'created_at', 'updated_at'
    ]
    
    def get_permissions(self):
        """Override permissions for specific actions"""
        if self.action in ['list', 'retrieve', 'download_report', 'student_self_results']:
            return [IsAuthenticated(), CanViewResults()]
        elif self.action in ['bulk_upload']:
            return [IsAuthenticated(), CanBulkUploadResults()]
        elif self.action in ['publish', 'approve_result']:
            return [IsAuthenticated(), CanApproveResults()]
        elif self.action in ['add_subject_scores']:
            return [IsAuthenticated(), CanManageResults()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return StudentResultListSerializer
        elif self.action == 'download_report':
            return ReportCardSerializer
        return super().get_serializer_class()
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Students can only see their own published results
        if user.role == 'student':
            try:
                student = user.student_profile
                return queryset.filter(student=student, is_published=True)
            except:
                return StudentResult.objects.none()
        
        # Parents can see their children's published results
        elif user.role == 'parent':
            try:
                parent_profile = user.parent_profile
                children = parent_profile.children.all()
                return queryset.filter(student__in=children, is_published=True)
            except:
                return StudentResult.objects.none()
        
        # Teachers can see results of their classes only
        elif user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            # Get classes where user is class teacher
            try:
                teacher_profile = user.staff_profile.teacher_profile
                assigned_class_levels = teacher_profile.assigned_class_levels.all()
                return queryset.filter(class_level__in=assigned_class_levels)
            except:
                # Fallback: check if user is class teacher
                return queryset.filter(Q(class_teacher=user) | Q(headmaster=user))
        
        # Accountants and secretaries can view all results
        elif user.role in ['accountant', 'secretary']:
            return queryset
        
        # Admin roles see all results
        elif user.role in ['head', 'hm', 'principal', 'vice_principal']:
            return queryset
        
        return StudentResult.objects.none()
    
    def perform_create(self, serializer):
        """Set created_by user when creating result"""
        serializer.save(created_by=self.request.user)
    
    def check_object_permissions(self, request, obj):
        """Check if user has permission to access this specific result"""
        user = request.user
        
        # Admin roles have full access
        if user.role in ['head', 'hm', 'principal', 'vice_principal']:
            return
        
        # Students can only access their own published results
        if user.role == 'student':
            try:
                student_profile = user.student_profile
                if obj.student != student_profile or not obj.is_published:
                    self.permission_denied(request, message='Not authorized to access this result')
            except:
                self.permission_denied(request, message='Student profile not found')
        
        # Parents can only access their children's published results
        elif user.role == 'parent':
            try:
                parent_profile = user.parent_profile
                if obj.student not in parent_profile.children.all() or not obj.is_published:
                    self.permission_denied(request, message='Not authorized to access this result')
            except:
                self.permission_denied(request, message='Parent profile not found')
        
        # Teachers can only access results for their classes
        elif user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            try:
                teacher_profile = user.staff_profile.teacher_profile
                if obj.class_level not in teacher_profile.assigned_class_levels.all():
                    self.permission_denied(request, message='Not authorized to access this result')
            except:
                # Check if user is the class teacher
                if obj.class_teacher != user and obj.headmaster != user:
                    self.permission_denied(request, message='Not authorized to access this result')
    
    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """Get results for a specific student"""
        student_id = request.query_params.get('student_id')
        admission_number = request.query_params.get('admission_number')
        registration_number = request.query_params.get('registration_number')
        
        if not any([student_id, admission_number, registration_number]):
            return Response(
                {'error': 'Please provide student_id, admission_number, or registration_number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find student
        student = None
        if student_id:
            student = get_object_or_404(Student, pk=student_id)
        elif admission_number:
            student = get_object_or_404(Student, admission_number=admission_number)
        elif registration_number:
            student = get_object_or_404(Student, user__registration_number=registration_number)
        
        # Check permissions
        user = request.user
        if user.role == 'student':
            # Student can only see their own results
            try:
                student_profile = user.student_profile
                if student != student_profile:
                    return Response(
                        {'error': 'Not authorized to view these results'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except:
                return Response(
                    {'error': 'Student profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif user.role == 'parent':
            # Parent can only see their children's results
            try:
                parent_profile = user.parent_profile
                if student not in parent_profile.children.all():
                    return Response(
                        {'error': 'Not authorized to view these results'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except:
                return Response(
                    {'error': 'Parent profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        results = self.get_queryset().filter(student=student)
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_class_level(self, request):
        """Get all results for a specific class level, session, and term"""
        class_level_id = request.query_params.get('class_level_id')
        session_id = request.query_params.get('session_id')
        term_id = request.query_params.get('term_id')
        
        if not all([class_level_id, session_id, term_id]):
            return Response(
                {'error': 'class_level_id, session_id, and term_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        class_level = get_object_or_404(ClassLevel, pk=class_level_id)
        session = get_object_or_404(AcademicSession, pk=session_id)
        term = get_object_or_404(AcademicTerm, pk=term_id)
        
        # Check if user has permission to view this class level's results
        user = request.user
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            try:
                teacher_profile = user.staff_profile.teacher_profile
                if class_level not in teacher_profile.assigned_class_levels.all():
                    return Response(
                        {'error': 'Not authorized to view results for this class level'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except:
                # Check if user is class teacher
                if class_level.class_teacher != user:
                    return Response(
                        {'error': 'Not authorized to view results for this class level'},
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        results = self.get_queryset().filter(
            class_level=class_level,
            session=session,
            term=term
        )
        
        # Add class level statistics
        statistics = {
            'total_students': results.count(),
            'average_percentage': results.aggregate(Avg('percentage'))['percentage__avg'] or 0,
            'highest_score': results.aggregate(Max('overall_total_score'))['overall_total_score__max'] or 0,
            'lowest_score': results.aggregate(Min('overall_total_score'))['overall_total_score__min'] or 0,
            'grade_distribution': results.values('overall_grade').annotate(count=Count('id')),
            'promoted_count': results.filter(is_promoted=True).count(),
            'published_count': results.filter(is_published=True).count()
        }
        
        serializer = self.get_serializer(results, many=True)
        return Response({
            'results': serializer.data,
            'statistics': statistics,
            'class_level_info': {
                'class_level_name': class_level.name,
                'session': session.name,
                'term': term.name
            }
        })
    
    @action(detail=True, methods=['post'])
    def add_subject_scores(self, request, pk=None):
        """Add multiple subject scores to a result"""
        result = self.get_object()
        serializer = SubjectScoreBulkSerializer(data=request.data, many=True)
        
        if serializer.is_valid():
            subject_scores = []
            errors = []
            
            for subject_data in serializer.validated_data:
                try:
                    subject = Subject.objects.get(code=subject_data['subject_code'])
                    
                    # Check if subject score already exists
                    existing_score = SubjectScore.objects.filter(
                        result=result,
                        subject=subject
                    ).first()
                    
                    if existing_score:
                        # Update existing score
                        existing_score.ca_score = subject_data['ca_score']
                        existing_score.exam_score = subject_data['exam_score']
                        existing_score.observation_conduct = subject_data.get('observation_conduct', '')
                        existing_score.subject_remark = subject_data.get('subject_remark', '')
                        existing_score.teacher_comment = subject_data.get('teacher_comment', '')
                        existing_score.save()
                        subject_scores.append(existing_score)
                    else:
                        # Create new score
                        score = SubjectScore.objects.create(
                            result=result,
                            subject=subject,
                            ca_score=subject_data['ca_score'],
                            exam_score=subject_data['exam_score'],
                            observation_conduct=subject_data.get('observation_conduct', ''),
                            subject_remark=subject_data.get('subject_remark', ''),
                            teacher_comment=subject_data.get('teacher_comment', '')
                        )
                        subject_scores.append(score)
                        
                except Subject.DoesNotExist:
                    errors.append({
                        'subject_code': subject_data['subject_code'],
                        'error': f"Subject not found"
                    })
                except Exception as e:
                    errors.append({
                        'subject_code': subject_data.get('subject_code', 'unknown'),
                        'error': str(e)
                    })
            
            # Recalculate result totals
            result.calculate_totals()
            result.save()
            
            response_data = {
                'message': f'{len(subject_scores)} subject scores processed',
                'result_id': result.id,
                'processed_count': len(subject_scores),
                'error_count': len(errors)
            }
            
            if errors:
                response_data['errors'] = errors
            
            return Response(response_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve_result(self, request, pk=None):
        """Approve and sign off on a result"""
        result = self.get_object()
        user = request.user
        
        # Check if user can approve
        if user.role not in ['head', 'hm', 'principal', 'vice_principal', 'teacher', 'form_teacher']:
            return Response(
                {'error': 'Only administrators and teachers can approve results'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Set approver and date based on role
        today = timezone.now().date()
        
        if user.role in ['head', 'hm']:
            result.headmaster = user
            result.headmaster_signature_date = today
            message = 'Result approved by headmaster'
        elif user.role in ['principal', 'vice_principal']:
            result.headmaster = user
            result.headmaster_signature_date = today
            message = 'Result approved by principal'
        else:
            result.class_teacher = user
            result.class_teacher_signature_date = today
            message = 'Result approved by class teacher'
        
        result.save()
        
        return Response({
            'message': message,
            'approver': user.get_full_name(),
            'role': user.get_role_display(),
            'date': today
        })
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish result to student/parent"""
        result = self.get_object()
        user = request.user
        
        # Check permissions
        if user.role not in ['head', 'hm', 'principal', 'vice_principal']:
            return Response(
                {'error': 'Only administrators can publish results'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        result.is_published = True
        result.save()
        
        return Response({
            'message': 'Result published successfully',
            'result_id': result.id,
            'student': result.student.user.get_full_name() if result.student and result.student.user else '',
            'published_date': timezone.now()
        })
    
    @action(detail=False, methods=['get'])
    def student_self_results(self, request):
        """Get current student's own results"""
        if request.user.role != 'student':
            return Response(
                {'error': 'This endpoint is for students only'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            student = request.user.student_profile
            results = self.get_queryset().filter(student=student)
            
            # Calculate overall statistics
            total_results = results.count()
            average_percentage = results.aggregate(Avg('percentage'))['percentage__avg'] or 0
            best_result = results.order_by('-percentage').first()
            
            statistics = {
                'total_results': total_results,
                'average_percentage': round(average_percentage, 2),
                'best_percentage': best_result.percentage if best_result else 0,
                'best_grade': best_result.overall_grade if best_result else '',
                'best_position': best_result.position_in_class if best_result else None,
                'results_by_term': list(results.values('term__term', 'term__name').annotate(
                    avg_percentage=Avg('percentage'),
                    avg_position=Avg('position_in_class')
                ))
            }
            
            serializer = self.get_serializer(results, many=True)
            return Response({
                'results': serializer.data,
                'statistics': statistics,
                'student': {
                    'name': student.user.get_full_name() if student.user else '',
                    'class_level': student.class_level.name if student.class_level else 'Not assigned',
                    'admission_number': student.admission_number
                }
            })
        
        except Exception as e:
            return Response(
                {'error': f'Error retrieving results: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, JSONParser])
    def bulk_upload(self, request):
        """Bulk upload results from JSON data"""
        serializer = BulkResultUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            session = serializer.validated_data['session_id']
            term = serializer.validated_data['term_id']
            class_level = serializer.validated_data['class_level_id']
            results_data = serializer.validated_data['results_data']
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for result_data in results_data:
                try:
                    # Find student by registration number
                    student = Student.objects.get(
                        user__registration_number=result_data['student_registration_number']
                    )
                    
                    # Check if result already exists
                    result, created = StudentResult.objects.get_or_create(
                        student=student,
                        session=session,
                        term=term,
                        defaults={
                            'class_level': class_level,
                            'created_by': request.user
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    # Add subject scores if provided
                    for subject_score_data in result_data.get('subjects', []):
                        subject_code = subject_score_data.get('subject_code')
                        if subject_code:
                            try:
                                subject = Subject.objects.get(code=subject_code)
                                
                                SubjectScore.objects.update_or_create(
                                    result=result,
                                    subject=subject,
                                    defaults={
                                        'ca_score': subject_score_data.get('ca_score', 0),
                                        'exam_score': subject_score_data.get('exam_score', 0),
                                        'observation_conduct': subject_score_data.get('observation_conduct', ''),
                                        'subject_remark': subject_score_data.get('subject_remark', ''),
                                        'teacher_comment': subject_score_data.get('teacher_comment', '')
                                    }
                                )
                            except Subject.DoesNotExist:
                                errors.append({
                                    'student': result_data['student_registration_number'],
                                    'error': f'Subject not found: {subject_code}'
                                })
                    
                    # Update attendance if provided
                    if 'attendance' in result_data:
                        attendance = result_data['attendance']
                        result.frequency_of_school_opened = attendance.get('frequency', 0)
                        result.no_of_times_present = attendance.get('present', 0)
                        result.no_of_times_absent = attendance.get('absent', 0)
                    
                    # Add comments if provided
                    if 'comments' in result_data:
                        comments = result_data['comments']
                        result.class_teacher_comment = comments.get('class_teacher', '')
                        result.headmaster_comment = comments.get('headmaster', '')
                    
                    # Calculate totals
                    result.calculate_totals()
                    result.save()
                    
                except Student.DoesNotExist:
                    errors.append({
                        'student_registration': result_data.get('student_registration_number', 'Unknown'),
                        'error': 'Student not found'
                    })
                except Exception as e:
                    errors.append({
                        'student_registration': result_data.get('student_registration_number', 'Unknown'),
                        'error': str(e)
                    })
            
            return Response({
                'message': 'Bulk upload completed',
                'created': created_count,
                'updated': updated_count,
                'errors': errors,
                'total_processed': len(results_data),
                'success_count': created_count + updated_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def download_report(self, request, pk=None):
        """Generate and download report card"""
        result = self.get_object()
        
        # Check if user has permission to download this report
        user = request.user
        if user.role == 'student':
            try:
                student_profile = user.student_profile
                if result.student != student_profile or not result.is_published:
                    return Response(
                        {'error': 'Not authorized to download this report'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except:
                return Response(
                    {'error': 'Student profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        elif user.role == 'parent':
            try:
                parent_profile = user.parent_profile
                if result.student not in parent_profile.children.all() or not result.is_published:
                    return Response(
                        {'error': 'Not authorized to download this report'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except:
                return Response(
                    {'error': 'Parent profile not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # For teachers and admins, check if they have permission
        elif user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            if result.class_teacher != user and result.headmaster != user:
                return Response(
                    {'error': 'Not authorized to download this report'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Generate report data
        serializer = ReportCardSerializer(result)
        
        # In production, you would generate a PDF here
        # For now, return JSON data
        return Response({
            'message': 'Report card data (PDF generation would happen in production)',
            'report_data': serializer.data,
            'download_url': f'/api/results/{result.id}/report.pdf',  # Placeholder
            'student_name': result.student.user.get_full_name() if result.student and result.student.user else '',
            'class_level': result.class_level.name if result.class_level else '',
            'session': result.session.name if result.session else '',
            'term': result.term.name if result.term else ''
        })
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search results by various criteria"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in student names and admission numbers
        results = self.get_queryset().filter(
            Q(student__user__first_name__icontains=query) |
            Q(student__user__last_name__icontains=query) |
            Q(student__admission_number__icontains=query) |
            Q(student__user__registration_number__icontains=query)
        )
        
        serializer = self.get_serializer(results, many=True)
        return Response({
            'count': results.count(),
            'results': serializer.data,
            'query': query
        })
            
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            # Check if user has permission to delete
            if not request.user.has_perm('results.delete_studentresult'):
                return Response(
                    {"detail": "You do not have permission to delete results."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            self.perform_destroy(instance)
            return Response(
                {"detail": "Result deleted successfully."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================
# SUBJECT SCORE VIEWSET
# ============================================

class SubjectScoreViewSet(viewsets.ModelViewSet):
    """ViewSet for managing individual subject scores"""
    
    queryset = SubjectScore.objects.select_related(
        'result', 'result__student', 'result__student__user', 'subject'
    ).order_by('subject__name')
    
    serializer_class = SubjectScoreSerializer
    permission_classes = [IsAuthenticated, CanManageResults]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['result', 'subject', 'grade']
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Students can only see their own scores from published results
        if user.role == 'student':
            try:
                student = user.student_profile
                return queryset.filter(result__student=student, result__is_published=True)
            except:
                return SubjectScore.objects.none()
        
        # Parents can see their children's scores
        elif user.role == 'parent':
            try:
                parent_profile = user.parent_profile
                children = parent_profile.children.all()
                return queryset.filter(result__student__in=children, result__is_published=True)
            except:
                return SubjectScore.objects.none()
        
        return queryset


# ============================================
# PSYCHOMOTOR SKILLS VIEWSET
# ============================================

class PsychomotorSkillsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing psychomotor skills assessment"""
    
    queryset = PsychomotorSkills.objects.select_related('result', 'result__student')
    serializer_class = PsychomotorSkillsSerializer
    permission_classes = [IsAuthenticated, CanManageResults]
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == 'student':
            try:
                student = user.student_profile
                return queryset.filter(result__student=student, result__is_published=True)
            except:
                return PsychomotorSkills.objects.none()
        
        return queryset


# ============================================
# AFFECTIVE DOMAINS VIEWSET
# ============================================

class AffectiveDomainsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing affective domains assessment"""
    
    queryset = AffectiveDomains.objects.select_related('result', 'result__student')
    serializer_class = AffectiveDomainsSerializer
    permission_classes = [IsAuthenticated, CanManageResults]
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.role == 'student':
            try:
                student = user.student_profile
                return queryset.filter(result__student=student, result__is_published=True)
            except:
                return AffectiveDomains.objects.none()
        
        return queryset


# ============================================
# RESULT PUBLISHING VIEWSET
# ============================================

class ResultPublishingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing result publishing"""
    
    queryset = ResultPublishing.objects.select_related(
        'session', 'term', 'class_level', 'published_by'
    ).order_by('-created_at')
    
    serializer_class = ResultPublishingSerializer
    permission_classes = [IsAuthenticated, CanPublishResults]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['session', 'term', 'class_level', 'is_published']
    
    @action(detail=True, methods=['post'])
    def toggle_publish(self, request, pk=None):
        """Toggle publishing status"""
        publishing = self.get_object()
        user = request.user
        
        if publishing.is_published:
            publishing.unpublish_results()
            message = 'Results unpublished successfully'
        else:
            publishing.publish_results(user)
            message = 'Results published successfully'
        
        return Response({
            'message': message,
            'is_published': publishing.is_published,
            'published_date': publishing.published_date,
            'published_by': publishing.published_by.get_full_name() if publishing.published_by else None
        })
    
    @action(detail=False, methods=['get'])
    def publishing_status(self, request):
        """Get publishing status for all class levels"""
        session_id = request.query_params.get('session_id')
        term_id = request.query_params.get('term_id')
        
        if not session_id or not term_id:
            return Response(
                {'error': 'session_id and term_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = get_object_or_404(AcademicSession, pk=session_id)
        term = get_object_or_404(AcademicTerm, pk=term_id)
        
        # Get all class levels for this session and term
        class_levels = ClassLevel.objects.all()
        
        status_list = []
        for class_level in class_levels:
            try:
                publishing = ResultPublishing.objects.get(
                    session=session,
                    term=term,
                    class_level=class_level
                )
                status_list.append({
                    'class_level_id': class_level.id,
                    'class_level_name': class_level.name,
                    'is_published': publishing.is_published,
                    'published_date': publishing.published_date,
                    'published_by': publishing.published_by.get_full_name() if publishing.published_by else None,
                    'published_by_id': publishing.published_by.id if publishing.published_by else None
                })
            except ResultPublishing.DoesNotExist:
                status_list.append({
                    'class_level_id': class_level.id,
                    'class_level_name': class_level.name,
                    'is_published': False,
                    'published_date': None,
                    'published_by': None,
                    'published_by_id': None
                })
        
        return Response(status_list)


# ============================================
# RESULT STATISTICS VIEW
# ============================================

class ResultStatisticsView(generics.GenericAPIView):
    """View for result statistics and analytics"""
    
    permission_classes = [IsAuthenticated, CanAccessResultStatistics]
    
    def get(self, request):
        """Get overall result statistics"""
        user = request.user
        
        # Base queryset
        results = StudentResult.objects.all()
        subject_scores = SubjectScore.objects.all()
        
        # Apply filters based on user role
        if user.role in ['teacher', 'form_teacher', 'subject_teacher']:
            try:
                teacher_profile = user.staff_profile.teacher_profile
                assigned_class_levels = teacher_profile.assigned_class_levels.all()
                results = results.filter(class_level__in=assigned_class_levels)
                subject_scores = subject_scores.filter(result__class_level__in=assigned_class_levels)
            except:
                # Fallback to classes where user is class teacher
                results = results.filter(Q(class_teacher=user) | Q(headmaster=user))
                subject_scores = subject_scores.filter(Q(result__class_teacher=user) | Q(result__headmaster=user))
        
        # Get basic statistics
        total_results = results.count()
        published_results = results.filter(is_published=True).count()
        
        # Grade distribution
        grade_distribution = list(results.values('overall_grade').annotate(
            count=Count('id')
        ).order_by('overall_grade'))
        
        # Term-wise performance
        term_performance = list(results.values(
            'session__name', 'session__id', 'term__term', 'term__name'
        ).annotate(
            avg_percentage=Avg('percentage'),
            total_students=Count('id'),
            promoted=Count('id', filter=Q(is_promoted=True)),
            published=Count('id', filter=Q(is_published=True))
        ).order_by('session__start_date', 'term__term'))
        
        # Class level-wise averages
        class_level_performance = list(results.values(
            'class_level__name', 'class_level__id', 'session__name', 'term__name'
        ).annotate(
            avg_percentage=Avg('percentage'),
            total_students=Count('id'),
            avg_position=Avg('position_in_class'),
            promoted_count=Count('id', filter=Q(is_promoted=True))
        ).order_by('class_level__order'))
        
        # Subject-wise averages
        subject_stats = list(subject_scores.values(
            'subject__name', 'subject__code', 'subject__id'
        ).annotate(
            avg_score=Avg('total_score'),
            avg_ca=Avg('ca_score'),
            avg_exam=Avg('exam_score'),
            total_students=Count('id', distinct=True),
            avg_grade=Avg('grade')
        ).order_by('subject__name'))
        
        # Calculate overall averages
        overall_avg_percentage = results.aggregate(avg=Avg('percentage'))['avg'] or 0
        overall_avg_position = results.aggregate(avg=Avg('position_in_class'))['avg'] or 0
        promotion_rate = (results.filter(is_promoted=True).count() / total_results * 100) if total_results > 0 else 0
        
        return Response({
            'overall': {
                'total_results': total_results,
                'published_results': published_results,
                'publish_percentage': round((published_results / total_results * 100), 2) if total_results > 0 else 0,
                'average_percentage': round(overall_avg_percentage, 2),
                'average_position': round(overall_avg_position, 2),
                'promotion_rate': round(promotion_rate, 2)
            },
            'grade_distribution': grade_distribution,
            'term_performance': term_performance,
            'class_level_performance': class_level_performance,
            'subject_statistics': subject_stats,
            'user_role': user.role,
            'user_name': user.get_full_name()
        })
    
    def class_level_statistics(self, request):
        """Get statistics for a specific class level"""
        class_level_id = request.query_params.get('class_level_id')
        session_id = request.query_params.get('session_id')
        term_id = request.query_params.get('term_id')
        
        if not all([class_level_id, session_id, term_id]):
            return Response(
                {'error': 'class_level_id, session_id, and term_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        class_level = get_object_or_404(ClassLevel, pk=class_level_id)
        session = get_object_or_404(AcademicSession, pk=session_id)
        term = get_object_or_404(AcademicTerm, pk=term_id)
        
        # Get results for this class level
        results = StudentResult.objects.filter(
            class_level=class_level,
            session=session,
            term=term
        )
        
        if not results.exists():
            return Response({
                'message': 'No results found for this class level',
                'class_level_info': {
                    'name': class_level.name,
                    'session': session.name,
                    'term': term.name
                }
            })
        
        # Calculate detailed statistics
        total_students = results.count()
        
        # Performance statistics
        performance_stats = results.aggregate(
            avg_percentage=Avg('percentage'),
            max_percentage=Max('percentage'),
            min_percentage=Min('percentage'),
            avg_total_score=Avg('overall_total_score'),
            max_total_score=Max('overall_total_score'),
            min_total_score=Min('overall_total_score'),
            promoted_count=Count('id', filter=Q(is_promoted=True)),
            published_count=Count('id', filter=Q(is_published=True))
        )
        
        # Grade distribution
        grade_dist = list(results.values('overall_grade').annotate(
            count=Count('id'),
            percentage=Count('id') * 100.0 / total_students
        ).order_by('overall_grade'))
        
        # Subject-wise statistics
        subject_scores = SubjectScore.objects.filter(result__in=results)
        subject_stats = list(subject_scores.values(
            'subject__name', 'subject__code'
        ).annotate(
            avg_score=Avg('total_score'),
            avg_ca=Avg('ca_score'),
            avg_exam=Avg('exam_score'),
            pass_rate=Count('id', filter=Q(grade__in=['A', 'B', 'C'])) * 100.0 / Count('id'),
            student_count=Count('result__student', distinct=True)
        ).order_by('subject__name'))
        
        # Attendance statistics
        attendance_stats = results.aggregate(
            avg_present=Avg('no_of_times_present'),
            avg_absent=Avg('no_of_times_absent'),
            total_days=Avg('frequency_of_school_opened')
        )
        
        # Calculate attendance percentage
        if attendance_stats['total_days']:
            attendance_stats['avg_attendance_percentage'] = (
                attendance_stats['avg_present'] / attendance_stats['total_days'] * 100
            )
        else:
            attendance_stats['avg_attendance_percentage'] = 0
        
        return Response({
            'class_level_info': {
                'id': class_level.id,
                'name': class_level.name,
                'session': session.name,
                'term': term.name,
                'class_teacher': class_level.class_teacher.get_full_name() if class_level.class_teacher else 'Not assigned'
            },
            'summary': {
                'total_students': total_students,
                'promotion_rate': (performance_stats['promoted_count'] / total_students * 100) if total_students > 0 else 0,
                'publication_rate': (performance_stats['published_count'] / total_students * 100) if total_students > 0 else 0
            },
            'performance': performance_stats,
            'grade_distribution': grade_dist,
            'subject_statistics': subject_stats,
            'attendance': attendance_stats,
            'top_performers': list(results.order_by('-percentage')[:5].values(
                'student__user__first_name', 'student__user__last_name',
                'student__admission_number', 'percentage', 'overall_grade', 'position_in_class'
            ))
        })