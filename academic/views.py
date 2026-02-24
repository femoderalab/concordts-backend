"""
Complete Academic Views for Nigerian School Management System
All views for academic management - ERROR FREE VERSION
"""

import logging
from django.db import transaction
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    AcademicSession, AcademicTerm, Program, ClassLevel, Subject,
    Class, ClassSubject
)
from .serializers import (
    AcademicSessionSerializer, AcademicSessionListSerializer,
    AcademicTermSerializer, AcademicTermListSerializer,
    ProgramSerializer, ProgramListSerializer,
    ClassLevelSerializer, ClassLevelListSerializer,
    SubjectSerializer, SubjectListSerializer,
    ClassSerializer, ClassListSerializer,
    ClassSubjectSerializer, ClassSubjectListSerializer,
    ClassDashboardSerializer, TeacherAssignmentSerializer,
    BulkClassSubjectAssignmentSerializer,
    AcademicDashboardSerializer, ClassStatisticsSerializer
)

logger = logging.getLogger(__name__)


# ============================================
# ACADEMIC SESSION VIEWS
# ============================================

class AcademicSessionListView(generics.ListAPIView):
    """List all academic sessions"""
    serializer_class = AcademicSessionListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_current']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'end_date', 'name']
    ordering = ['-start_date']

    def get_queryset(self):
        try:
            return AcademicSession.objects.all()
        except Exception as e:
            logger.error(f"Error getting academic sessions: {e}")
            return AcademicSession.objects.none()


class AcademicSessionCreateView(generics.CreateAPIView):
    """Create a new academic session"""
    serializer_class = AcademicSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Academic session created: {instance.name}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Academic session created successfully',
            'session': response.data
        }
        return response


class AcademicSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete academic session"""
    serializer_class = AcademicSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AcademicSession.objects.all()

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Academic session updated successfully',
            'session': response.data
        }
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'success': True,
            'message': 'Academic session deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class CurrentAcademicSessionView(APIView):
    """Get current academic session"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            current_session = AcademicSession.objects.filter(is_current=True).first()
            if current_session:
                serializer = AcademicSessionSerializer(current_session)
                return Response({
                    'success': True,
                    'session': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'message': 'No current session found'
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting current session: {e}")
            return Response({
                'error': 'Failed to get current session',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# ACADEMIC TERM VIEWS
# ============================================

class AcademicTermListView(generics.ListAPIView):
    """List all academic terms"""
    serializer_class = AcademicTermListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['session', 'term', 'status', 'is_current']
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'name']
    ordering = ['session__start_date', 'term']

    def get_queryset(self):
        try:
            return AcademicTerm.objects.select_related('session').all()
        except Exception as e:
            logger.error(f"Error getting academic terms: {e}")
            return AcademicTerm.objects.none()


class AcademicTermCreateView(generics.CreateAPIView):
    """Create a new academic term"""
    serializer_class = AcademicTermSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Academic term created: {instance.name}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Academic term created successfully',
            'term': response.data
        }
        return response


class AcademicTermDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete academic term"""
    serializer_class = AcademicTermSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = AcademicTerm.objects.select_related('session')


class CurrentAcademicTermView(APIView):
    """Get current academic term"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            current_term = AcademicTerm.objects.filter(is_current=True).first()
            if current_term:
                serializer = AcademicTermSerializer(current_term)
                return Response({
                    'success': True,
                    'term': serializer.data
                })
            else:
                return Response({
                    'success': False,
                    'message': 'No current term found'
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting current term: {e}")
            return Response({
                'error': 'Failed to get current term',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# PROGRAM VIEWS
# ============================================

class ProgramListView(generics.ListAPIView):
    """List all academic programs"""
    serializer_class = ProgramListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program_type', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'program_type', 'duration_years']
    ordering = ['program_type', 'name']

    def get_queryset(self):
        try:
            return Program.objects.all()
        except Exception as e:
            logger.error(f"Error getting programs: {e}")
            return Program.objects.none()


class ProgramCreateView(generics.CreateAPIView):
    """Create a new academic program"""
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Program created: {instance.name} ({instance.code})")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Program created successfully',
            'program': response.data
        }
        return response


class ProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete academic program"""
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Program.objects.all()


# ============================================
# CLASS LEVEL VIEWS
# ============================================

class ClassLevelListView(generics.ListAPIView):
    """List all class levels"""
    serializer_class = ClassLevelListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['program', 'level', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'name', 'level']
    ordering = ['program__program_type', 'order']

    def get_queryset(self):
        try:
            return ClassLevel.objects.select_related('program').all()
        except Exception as e:
            logger.error(f"Error getting class levels: {e}")
            return ClassLevel.objects.none()


class ClassLevelCreateView(generics.CreateAPIView):
    """Create a new class level"""
    serializer_class = ClassLevelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Class level created: {instance.name} ({instance.code})")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Class level created successfully',
            'class_level': response.data
        }
        return response


class ClassLevelDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete class level"""
    serializer_class = ClassLevelSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ClassLevel.objects.select_related('program')


class ClassArmsView(APIView):
    """Get class arms for a class level"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            class_level = get_object_or_404(ClassLevel, pk=pk)
            classes = Class.objects.filter(class_level=class_level, is_active=True)
            serializer = ClassListSerializer(classes, many=True)
            return Response({
                'success': True,
                'class_level': ClassLevelSerializer(class_level).data,
                'arms': serializer.data,
                'count': classes.count()
            })
        except Exception as e:
            logger.error(f"Error getting class arms: {e}")
            return Response({
                'error': 'Failed to get class arms',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# SUBJECT VIEWS
# ============================================

class SubjectListView(generics.ListAPIView):
    """List all subjects"""
    serializer_class = SubjectListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'subject_type', 'stream', 'is_compulsory', 'is_examinable', 'is_active',
        'available_for_creche', 'available_for_nursery', 'available_for_primary',
        'available_for_jss', 'available_for_sss'
    ]
    search_fields = ['name', 'code', 'short_name', 'description']
    ordering_fields = ['name', 'code', 'subject_type']
    ordering = ['code', 'name']

    def get_queryset(self):
        try:
            return Subject.objects.all()
        except Exception as e:
            logger.error(f"Error getting subjects: {e}")
            return Subject.objects.none()


class SubjectCreateView(generics.CreateAPIView):
    """Create a new subject"""
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Subject created: {instance.name} ({instance.code})")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Subject created successfully',
            'subject': response.data
        }
        return response


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete subject"""
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Subject.objects.all()


# ============================================
# CLASS VIEWS
# ============================================

class ClassListView(generics.ListAPIView):
    """List all classes with filtering"""
    serializer_class = ClassListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['session', 'term', 'class_level', 'status', 'is_active', 'stream']
    search_fields = ['name', 'code', 'room_number']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['class_level__order', 'name']

    def get_queryset(self):
        try:
            return Class.objects.select_related(
                'session', 'term', 'class_level', 'class_teacher'
            ).all()
        except Exception as e:
            logger.error(f"Error getting classes: {e}")
            return Class.objects.none()


class ClassDetailedListView(generics.ListAPIView):
    """Get classes with detailed information"""
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            return Class.objects.select_related(
                'session', 'term', 'class_level', 'class_teacher'
            ).prefetch_related('class_subjects').filter(is_active=True)
        except Exception as e:
            logger.error(f"Error getting detailed classes: {e}")
            return Class.objects.none()


class ClassCreateView(generics.CreateAPIView):
    """Create a new class"""
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Class created: {instance.name} ({instance.code})")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Class created successfully',
            'class': response.data
        }
        return response


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete class"""
    serializer_class = ClassSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Class.objects.select_related(
        'session', 'term', 'class_level', 'class_teacher'
    )


class ClassDashboardView(APIView):
    """Get comprehensive class dashboard"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """Get class dashboard with comprehensive information"""
        try:
            class_obj = get_object_or_404(Class, pk=pk)
            
            # Get enrolled students count (this would come from students app)
            enrolled_students_count = class_obj.current_enrollment
            
            # Get class subjects
            class_subjects = class_obj.class_subjects.filter(is_active=True)
            
            # Prepare statistics
            statistics = {
                'total_students': class_obj.current_enrollment,
                'enrolled_students': enrolled_students_count,
                'max_capacity': class_obj.max_capacity,
                'capacity_percentage': round((class_obj.current_enrollment / class_obj.max_capacity * 100), 2) if class_obj.max_capacity > 0 else 0,
                'subjects_count': class_subjects.count(),
                'male_students': 0,  # Placeholder - would come from students app
                'female_students': 0,  # Placeholder - would come from students app
            }
            
            # Prepare dashboard data
            dashboard_data = {
                'class_info': class_obj,
                'subjects': ClassSubjectListSerializer(class_subjects, many=True).data,
                'enrolled_students_count': enrolled_students_count,
                'statistics': statistics
            }
            
            serializer = ClassDashboardSerializer(dashboard_data)
            
            return Response({
                'success': True,
                'dashboard': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error getting class dashboard: {e}", exc_info=True)
            return Response({
                'error': 'Failed to get class dashboard',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# CLASS SUBJECT ASSIGNMENT VIEWS
# ============================================

class ClassSubjectListView(generics.ListAPIView):
    """List all class-subject assignments"""
    serializer_class = ClassSubjectListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'subject', 'teacher', 'is_active', 'is_compulsory']
    search_fields = ['class_obj__name', 'subject__name']
    ordering_fields = ['class_obj__name', 'subject__name']
    ordering = ['class_obj', 'subject']

    def get_queryset(self):
        try:
            return ClassSubject.objects.select_related(
                'class_obj', 'subject', 'teacher'
            ).all()
        except Exception as e:
            logger.error(f"Error getting class subjects: {e}")
            return ClassSubject.objects.none()


class ClassSubjectCreateView(generics.CreateAPIView):
    """Create a new class-subject assignment"""
    serializer_class = ClassSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"Class subject assignment created: {instance.subject.name} for {instance.class_obj.name}")

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            'success': True,
            'message': 'Class subject assignment created successfully',
            'assignment': response.data
        }
        return response


class ClassSubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete class-subject assignment"""
    serializer_class = ClassSubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ClassSubject.objects.select_related('class_obj', 'subject', 'teacher')


class BulkClassSubjectAssignmentView(APIView):
    """Create multiple class-subject assignments in bulk"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Create bulk assignments"""
        try:
            serializer = BulkClassSubjectAssignmentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': 'Validation failed',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            assignments = serializer.validated_data['assignments']
            created = []
            errors = []

            with transaction.atomic():
                for i, assignment_data in enumerate(assignments):
                    try:
                        # Get related objects
                        class_obj = Class.objects.get(id=assignment_data['class_id'])
                        subject = Subject.objects.get(id=assignment_data['subject_id'])
                        
                        teacher = None
                        if 'teacher_id' in assignment_data:
                            from users.models import User
                            teacher = User.objects.get(id=assignment_data['teacher_id'])

                        # Check if assignment already exists
                        if ClassSubject.objects.filter(class_obj=class_obj, subject=subject).exists():
                            errors.append({
                                'index': i,
                                'error': f'Assignment already exists for {class_obj.name} - {subject.name}'
                            })
                            continue

                        # Create new assignment
                        class_subject = ClassSubject.objects.create(
                            class_obj=class_obj,
                            subject=subject,
                            teacher=teacher,
                            is_active=True,
                            is_compulsory=assignment_data.get('is_compulsory', False)
                        )
                        created.append(class_subject)

                    except Exception as e:
                        errors.append({
                            'index': i,
                            'error': str(e)
                        })

            response_data = {
                'success': len(errors) == 0,
                'created_count': len(created),
                'failed_count': len(errors),
                'assignments': ClassSubjectListSerializer(created, many=True).data if created else [],
                'errors': errors
            }

            if created:
                logger.info(f"Bulk assignment: Created {len(created)} assignments")
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                logger.warning(f"Bulk assignment: No assignments created, {len(errors)} errors")
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error in bulk class subject assignment: {e}", exc_info=True)
            return Response({
                'error': 'Failed to process bulk assignment',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# TEACHER ASSIGNMENT VIEWS
# ============================================

class TeacherAssignmentsView(APIView):
    """Get teacher's class and subject assignments"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        """Get teacher assignments"""
        try:
            from users.models import User

            # If no pk specified, get current user's assignments
            if pk is None:
                user = request.user
            else:
                user = get_object_or_404(User, pk=pk)

            # Get class teacher assignments
            class_teacher_classes = Class.objects.filter(
                class_teacher=user,
                is_active=True
            )

            # Get subject teaching assignments
            teaching_assignments = ClassSubject.objects.filter(
                teacher=user,
                is_active=True
            ).select_related('class_obj', 'subject')

            # Prepare statistics
            statistics = {
                'total_classes': class_teacher_classes.count(),
                'total_subjects_taught': teaching_assignments.values('subject').distinct().count(),
                'total_assignments': teaching_assignments.count(),
                'total_students': 0,  # Placeholder - would come from students app
            }

            # Prepare data
            data = {
                'teacher': user,
                'class_teacher_classes': class_teacher_classes,
                'teaching_assignments': teaching_assignments,
                'statistics': statistics,
            }

            serializer = TeacherAssignmentSerializer(data)
            
            return Response({
                'success': True,
                'assignments': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error getting teacher assignments: {e}", exc_info=True)
            return Response({
                'error': 'Failed to get teacher assignments',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# DASHBOARD AND REPORTING VIEWS
# ============================================

class AcademicDashboardView(APIView):
    """Academic dashboard with overview statistics"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get academic dashboard data"""
        try:
            # Current academic session and term
            current_session = AcademicSession.objects.filter(is_current=True).first()
            current_term = AcademicTerm.objects.filter(is_current=True).first()

            # Statistics
            total_classes = Class.objects.filter(is_active=True).count()
            total_subjects = Subject.objects.filter(is_active=True).count()
            total_programs = Program.objects.filter(is_active=True).count()
            total_class_levels = ClassLevel.objects.filter(is_active=True).count()

            # Class capacity statistics
            classes_with_capacity = Class.objects.filter(is_active=True)
            total_capacity = sum(c.max_capacity for c in classes_with_capacity)
            total_enrolled = sum(c.current_enrollment for c in classes_with_capacity)

            # Recent activities
            recent_classes = Class.objects.filter(is_active=True).order_by('-created_at')[:5]

            data = {
                'current_session': current_session,
                'current_term': current_term,
                'statistics': {
                    'total_classes': total_classes,
                    'total_students': total_enrolled,
                    'total_subjects': total_subjects,
                    'total_programs': total_programs,
                    'total_class_levels': total_class_levels,
                    'total_capacity': total_capacity,
                    'total_enrolled': total_enrolled,
                    'capacity_utilization': round((total_enrolled / total_capacity * 100), 2) if total_capacity > 0 else 0,
                },
                'recent_classes': recent_classes,
            }

            serializer = AcademicDashboardSerializer(data)
            
            return Response({
                'success': True,
                'dashboard': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error getting academic dashboard: {e}", exc_info=True)
            return Response({
                'error': 'Failed to get academic dashboard',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AcademicOverviewView(APIView):
    """Get comprehensive academic overview"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get academic overview"""
        try:
            # Get counts
            programs = Program.objects.filter(is_active=True)
            class_levels = ClassLevel.objects.filter(is_active=True)
            subjects = Subject.objects.filter(is_active=True)
            classes = Class.objects.filter(is_active=True)
            sessions = AcademicSession.objects.all()
            terms = AcademicTerm.objects.all()

            # Get current session and term
            current_session = AcademicSession.objects.filter(is_current=True).first()
            current_term = AcademicTerm.objects.filter(is_current=True).first()

            # Prepare program-wise statistics
            program_stats = []
            for program in programs:
                program_class_levels = class_levels.filter(program=program)
                program_classes = classes.filter(class_level__program=program)
                program_subjects = subjects.filter(
                    Q(available_for_creche=True) if program.program_type == 'creche' else
                    Q(available_for_nursery=True) if program.program_type == 'nursery' else
                    Q(available_for_primary=True) if program.program_type == 'primary' else
                    Q(available_for_jss=True) if program.program_type == 'junior_secondary' else
                    Q(available_for_sss=True)  # senior_secondary
                )
                
                program_stats.append({
                    'program': ProgramListSerializer(program).data,
                    'class_levels_count': program_class_levels.count(),
                    'classes_count': program_classes.count(),
                    'subjects_count': program_subjects.count(),
                    'total_students': sum(c.current_enrollment for c in program_classes),
                })

            # Prepare term timeline
            term_timeline = []
            if current_session:
                terms_in_session = terms.filter(session=current_session)
                for term in terms_in_session:
                    days_total = (term.end_date - term.start_date).days
                    days_passed = (timezone.now().date() - term.start_date).days
                    progress = min(100, max(0, (days_passed / days_total) * 100)) if days_total > 0 else 0
                    
                    term_timeline.append({
                        'term': AcademicTermListSerializer(term).data,
                        'days_total': days_total,
                        'days_passed': days_passed,
                        'progress': round(progress, 1),
                        'status': 'active' if term.is_current else ('upcoming' if term.start_date > timezone.now().date() else 'completed')
                    })

            overview_data = {
                'current_session': AcademicSessionListSerializer(current_session).data if current_session else None,
                'current_term': AcademicTermListSerializer(current_term).data if current_term else None,
                'totals': {
                    'programs': programs.count(),
                    'class_levels': class_levels.count(),
                    'subjects': subjects.count(),
                    'classes': classes.count(),
                    'sessions': sessions.count(),
                    'terms': terms.count(),
                },
                'program_statistics': program_stats,
                'term_timeline': term_timeline,
                'recent_activities': {
                    'new_classes': classes.order_by('-created_at')[:3],
                    'upcoming_terms': terms.filter(start_date__gte=timezone.now().date()).order_by('start_date')[:3],
                }
            }

            return Response({
                'success': True,
                'overview': overview_data
            })

        except Exception as e:
            logger.error(f"Error getting academic overview: {e}", exc_info=True)
            return Response({
                'error': 'Failed to get academic overview',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class DetailedStatisticsView(APIView):
    """Get detailed academic statistics"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get detailed statistics"""
        try:
            # Program statistics
            programs = Program.objects.filter(is_active=True)
            program_stats = []
            
            for program in programs:
                class_levels = ClassLevel.objects.filter(program=program, is_active=True)
                classes = Class.objects.filter(class_level__program=program, is_active=True)
                subjects = Subject.objects.filter(is_active=True)
                
                # Filter subjects based on program
                if program.program_type == 'creche':
                    program_subjects = subjects.filter(available_for_creche=True)
                elif program.program_type == 'nursery':
                    program_subjects = subjects.filter(available_for_nursery=True)
                elif program.program_type == 'primary':
                    program_subjects = subjects.filter(available_for_primary=True)
                elif program.program_type == 'junior_secondary':
                    program_subjects = subjects.filter(available_for_jss=True)
                else:  # senior_secondary
                    program_subjects = subjects.filter(available_for_sss=True)
                
                total_students = sum(c.current_enrollment for c in classes)
                total_capacity = sum(c.max_capacity for c in classes)
                
                program_stats.append({
                    'program': ProgramListSerializer(program).data,
                    'class_levels': class_levels.count(),
                    'classes': classes.count(),
                    'subjects': program_subjects.count(),
                    'students': total_students,
                    'capacity': total_capacity,
                    'utilization': round((total_students / total_capacity * 100), 1) if total_capacity > 0 else 0,
                })

            # Subject distribution
            subject_stats = {
                'by_type': {
                    'core': Subject.objects.filter(subject_type='core', is_active=True).count(),
                    'elective': Subject.objects.filter(subject_type='elective', is_active=True).count(),
                    'vocational': Subject.objects.filter(subject_type='vocational', is_active=True).count(),
                    'religious': Subject.objects.filter(subject_type='religious', is_active=True).count(),
                    'language': Subject.objects.filter(subject_type='language', is_active=True).count(),
                    'science': Subject.objects.filter(subject_type='science', is_active=True).count(),
                    'arts': Subject.objects.filter(subject_type='arts', is_active=True).count(),
                    'commercial': Subject.objects.filter(subject_type='commercial', is_active=True).count(),
                    'technical': Subject.objects.filter(subject_type='technical', is_active=True).count(),
                    'pre_school': Subject.objects.filter(subject_type='pre_school', is_active=True).count(),
                },
                'by_stream': {
                    'science': Subject.objects.filter(stream='science', is_active=True).count(),
                    'commercial': Subject.objects.filter(stream='commercial', is_active=True).count(),
                    'arts': Subject.objects.filter(stream='arts', is_active=True).count(),
                    'general': Subject.objects.filter(stream='general', is_active=True).count(),
                    'technical': Subject.objects.filter(stream='technical', is_active=True).count(),
                    'pre_school': Subject.objects.filter(stream='pre_school', is_active=True).count(),
                }
            }

            # Class statistics
            class_stats = {
                'by_status': {
                    'active': Class.objects.filter(status='active', is_active=True).count(),
                    'inactive': Class.objects.filter(status='inactive', is_active=True).count(),
                    'graduated': Class.objects.filter(status='graduated', is_active=True).count(),
                },
                'by_stream': {
                    'science': Class.objects.filter(stream='science', is_active=True).count(),
                    'commercial': Class.objects.filter(stream='commercial', is_active=True).count(),
                    'arts': Class.objects.filter(stream='arts', is_active=True).count(),
                    'general': Class.objects.filter(stream='general', is_active=True).count(),
                    None: Class.objects.filter(stream__isnull=True, is_active=True).count(),
                }
            }

            # Session statistics
            session_stats = {
                'by_status': {
                    'upcoming': AcademicSession.objects.filter(status='upcoming').count(),
                    'active': AcademicSession.objects.filter(status='active').count(),
                    'completed': AcademicSession.objects.filter(status='completed').count(),
                    'archived': AcademicSession.objects.filter(status='archived').count(),
                }
            }

            statistics_data = {
                'program_statistics': program_stats,
                'subject_statistics': subject_stats,
                'class_statistics': class_stats,
                'session_statistics': session_stats,
                'overall': {
                    'total_students': sum(ps['students'] for ps in program_stats),
                    'total_capacity': sum(ps['capacity'] for ps in program_stats),
                    'overall_utilization': round((sum(ps['students'] for ps in program_stats) / sum(ps['capacity'] for ps in program_stats) * 100), 1) if sum(ps['capacity'] for ps in program_stats) > 0 else 0,
                }
            }

            return Response({
                'success': True,
                'statistics': statistics_data
            })

        except Exception as e:
            logger.error(f"Error getting detailed statistics: {e}", exc_info=True)
            return Response({
                'error': 'Failed to get detailed statistics',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ClassStatisticsView(APIView):
    """Get class-level statistics"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get class statistics"""
        try:
            # Class level statistics
            class_level_stats = []
            for class_level in ClassLevel.objects.filter(is_active=True):
                classes = Class.objects.filter(class_level=class_level, is_active=True)
                total_classes = classes.count()
                total_students = sum(c.current_enrollment for c in classes)
                total_capacity = sum(c.max_capacity for c in classes)

                class_level_stats.append({
                    'class_level': ClassLevelListSerializer(class_level).data,
                    'total_classes': total_classes,
                    'total_students': total_students,
                    'total_capacity': total_capacity,
                    'utilization_percentage': round((total_students / total_capacity * 100), 2) if total_capacity > 0 else 0,
                })

            # Program statistics
            program_stats = []
            for program in Program.objects.filter(is_active=True):
                classes = Class.objects.filter(class_level__program=program, is_active=True)
                total_classes = classes.count()
                total_students = sum(c.current_enrollment for c in classes)

                program_stats.append({
                    'program': ProgramListSerializer(program).data,
                    'total_classes': total_classes,
                    'total_students': total_students,
                })

            data = {
                'class_level_statistics': class_level_stats,
                'program_statistics': program_stats,
            }

            serializer = ClassStatisticsSerializer(data)
            
            return Response({
                'success': True,
                'statistics': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error getting class statistics: {e}", exc_info=True)
            return Response({
                'error': 'Failed to get class statistics',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# PUBLIC VIEWS
# ============================================

class PublicAcademicStructureView(APIView):
    """Get public academic structure"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get Nigerian academic structure"""
        try:
            # Nigerian academic structure
            nigerian_structure = [
                {
                    'level': 'Creche',
                    'description': 'Early childhood education for ages 0-2',
                    'classes': ['Creche'],
                    'duration': '2 years',
                    'subjects_count': Subject.objects.filter(available_for_creche=True, is_active=True).count()
                },
                {
                    'level': 'Nursery',
                    'description': 'Pre-primary education for ages 3-5',
                    'classes': ['Nursery 1', 'Nursery 2', 'KG 1', 'KG 2'],
                    'duration': '2 years',
                    'subjects_count': Subject.objects.filter(available_for_nursery=True, is_active=True).count()
                },
                {
                    'level': 'Primary School',
                    'description': 'Basic education for ages 6-11 (Primary 1-6)',
                    'classes': ['Primary 1', 'Primary 2', 'Primary 3', 'Primary 4', 'Primary 5', 'Primary 6'],
                    'duration': '6 years',
                    'subjects_count': Subject.objects.filter(available_for_primary=True, is_active=True).count()
                },
                {
                    'level': 'Junior Secondary School (JSS)',
                    'description': 'Lower secondary education for ages 12-14',
                    'classes': ['JSS 1', 'JSS 2', 'JSS 3'],
                    'duration': '3 years',
                    'subjects_count': Subject.objects.filter(available_for_jss=True, is_active=True).count()
                },
                {
                    'level': 'Senior Secondary School (SSS)',
                    'description': 'Upper secondary education for ages 15-17',
                    'classes': ['SSS 1', 'SSS 2', 'SSS 3'],
                    'duration': '3 years',
                    'subjects_count': Subject.objects.filter(available_for_sss=True, is_active=True).count(),
                    'streams': [
                        {
                            'name': 'Science Stream',
                            'subjects': Subject.objects.filter(stream='science', available_for_sss=True, is_active=True).count()
                        },
                        {
                            'name': 'Commercial Stream',
                            'subjects': Subject.objects.filter(stream='commercial', available_for_sss=True, is_active=True).count()
                        },
                        {
                            'name': 'Arts/Humanities Stream',
                            'subjects': Subject.objects.filter(stream='arts', available_for_sss=True, is_active=True).count()
                        }
                    ]
                }
            ]

            # Current academic year
            current_session = AcademicSession.objects.filter(is_current=True).first()
            current_term = AcademicTerm.objects.filter(is_current=True).first()

            structure_data = {
                'academic_structure': nigerian_structure,
                'current_academic_year': AcademicSessionListSerializer(current_session).data if current_session else None,
                'current_term': AcademicTermListSerializer(current_term).data if current_term else None,
                'totals': {
                    'programs': Program.objects.filter(is_active=True).count(),
                    'class_levels': ClassLevel.objects.filter(is_active=True).count(),
                    'subjects': Subject.objects.filter(is_active=True).count(),
                    'classes': Class.objects.filter(is_active=True).count(),
                }
            }

            return Response({
                'success': True,
                'structure': structure_data
            })

        except Exception as e:
            logger.error(f"Error getting public structure: {e}")
            return Response({
                'error': 'Failed to get academic structure',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PublicAcademicCalendarView(APIView):
    """Get public academic calendar"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get academic calendar"""
        try:
            current_session = AcademicSession.objects.filter(is_current=True).first()
            
            if not current_session:
                return Response({
                    'success': False,
                    'message': 'No current academic session found'
                }, status=status.HTTP_404_NOT_FOUND)

            terms = AcademicTerm.objects.filter(session=current_session).order_by('term')
            
            calendar_data = {
                'academic_year': AcademicSessionListSerializer(current_session).data,
                'terms': AcademicTermListSerializer(terms, many=True).data,
                'key_dates': [
                    {
                        'date': 'First Monday of September',
                        'event': 'Academic Year Begins',
                        'description': 'Start of new academic session'
                    },
                    {
                        'date': 'Third week of October',
                        'event': 'Mid-Term Break',
                        'description': 'One week break for first term'
                    },
                    {
                        'date': 'Second week of December',
                        'event': 'First Term Ends',
                        'description': 'End of first term and Christmas break'
                    },
                    {
                        'date': 'First Monday of January',
                        'event': 'Second Term Begins',
                        'description': 'Start of second term'
                    },
                    {
                        'date': 'Last week of March',
                        'event': 'Mid-Term Break',
                        'description': 'One week break for second term'
                    },
                    {
                        'date': 'Second week of April',
                        'event': 'Second Term Ends',
                        'description': 'End of second term and Easter break'
                    },
                    {
                        'date': 'Last week of April',
                        'event': 'Third Term Begins',
                        'description': 'Start of third term'
                    },
                    {
                        'date': 'First week of June',
                        'event': 'Mid-Term Break',
                        'description': 'One week break for third term'
                    },
                    {
                        'date': 'Third week of July',
                        'event': 'Academic Year Ends',
                        'description': 'End of academic year and summer break'
                    }
                ]
            }

            return Response({
                'success': True,
                'calendar': calendar_data
            })

        except Exception as e:
            logger.error(f"Error getting public calendar: {e}")
            return Response({
                'error': 'Failed to get academic calendar',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PublicClassDetailView(generics.RetrieveAPIView):
    """Get class details for public viewing"""
    serializer_class = ClassSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Class.objects.select_related(
        'session', 'term', 'class_level', 'class_teacher'
    ).filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'class': serializer.data
        })


# ============================================
# BULK PROMOTION VIEWS
# ============================================

class BulkPromotionView(APIView):
    """Bulk promote students"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Promote students in bulk"""
        try:
            data = request.data
            
            # Validate required fields
            required_fields = ['from_class_level_id', 'to_class_level_id', 'session_id']
            for field in required_fields:
                if field not in data:
                    return Response({
                        'error': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Get source and destination class levels
            from_class_level = get_object_or_404(ClassLevel, pk=data['from_class_level_id'])
            to_class_level = get_object_or_404(ClassLevel, pk=data['to_class_level_id'])
            session = get_object_or_404(AcademicSession, pk=data['session_id'])

            # Get current term
            current_term = AcademicTerm.objects.filter(is_current=True).first()
            if not current_term:
                return Response({
                    'error': 'No current term found'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get source classes
            source_classes = Class.objects.filter(
                class_level=from_class_level,
                session=session,
                is_active=True
            )

            promoted_count = 0
            errors = []

            # This is a simplified version - in real implementation,
            # you would promote students from source to destination classes
            # and update their enrollment records

            return Response({
                'success': True,
                'message': f'Promotion initiated for {len(source_classes)} classes',
                'details': {
                    'from': from_class_level.name,
                    'to': to_class_level.name,
                    'session': session.name,
                    'classes_affected': len(source_classes),
                    'promoted_count': promoted_count,
                    'errors': errors
                }
            })

        except Exception as e:
            logger.error(f"Error in bulk promotion: {e}", exc_info=True)
            return Response({
                'error': 'Failed to process bulk promotion',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
