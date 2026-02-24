"""
Complete URL configuration for the academic app
All routes for academic management - ERROR FREE VERSION
"""

from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    # ============================================
    # Academic Structure
    # ============================================

    # Academic Sessions
    path('sessions/', views.AcademicSessionListView.as_view(), name='academic-session-list'),
    path('sessions/create/', views.AcademicSessionCreateView.as_view(), name='academic-session-create'),
    path('sessions/<int:pk>/', views.AcademicSessionDetailView.as_view(), name='academic-session-detail'),
    path('sessions/current/', views.CurrentAcademicSessionView.as_view(), name='current-academic-session'),

    # Academic Terms
    path('terms/', views.AcademicTermListView.as_view(), name='academic-term-list'),
    path('terms/create/', views.AcademicTermCreateView.as_view(), name='academic-term-create'),
    path('terms/<int:pk>/', views.AcademicTermDetailView.as_view(), name='academic-term-detail'),
    path('terms/current/', views.CurrentAcademicTermView.as_view(), name='current-academic-term'),

    # Programs
    path('programs/', views.ProgramListView.as_view(), name='program-list'),
    path('programs/create/', views.ProgramCreateView.as_view(), name='program-create'),
    path('programs/<int:pk>/', views.ProgramDetailView.as_view(), name='program-detail'),

    # Class Levels
    path('class-levels/', views.ClassLevelListView.as_view(), name='class-level-list'),
    path('class-levels/create/', views.ClassLevelCreateView.as_view(), name='class-level-create'),
    path('class-levels/<int:pk>/', views.ClassLevelDetailView.as_view(), name='class-level-detail'),
    path('class-levels/<int:pk>/arms/', views.ClassArmsView.as_view(), name='class-arms-list'),

    # Subjects
    path('subjects/', views.SubjectListView.as_view(), name='subject-list'),
    path('subjects/create/', views.SubjectCreateView.as_view(), name='subject-create'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject-detail'),

    # ============================================
    # Class Management
    # ============================================

    # Classes
    path('classes/', views.ClassListView.as_view(), name='class-list'),
    path('classes/create/', views.ClassCreateView.as_view(), name='class-create'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='class-detail'),
    path('classes/<int:pk>/dashboard/', views.ClassDashboardView.as_view(), name='class-dashboard'),
    path('classes/detailed/', views.ClassDetailedListView.as_view(), name='class-detailed-list'),

    # Class-Subject Assignments
    path('class-subjects/', views.ClassSubjectListView.as_view(), name='class-subject-list'),
    path('class-subjects/create/', views.ClassSubjectCreateView.as_view(), name='class-subject-create'),
    path('class-subjects/<int:pk>/', views.ClassSubjectDetailView.as_view(), name='class-subject-detail'),
    path('class-subjects/bulk-assign/', views.BulkClassSubjectAssignmentView.as_view(), name='class-subject-bulk-assign'),

    # ============================================
    # Teacher Management
    # ============================================

    path('teachers/assignments/', views.TeacherAssignmentsView.as_view(), name='teacher-assignments-current'),
    path('teachers/<int:pk>/assignments/', views.TeacherAssignmentsView.as_view(), name='teacher-assignments'),

    # ============================================
    # Dashboard and Reporting
    # ============================================

    path('dashboard/', views.AcademicDashboardView.as_view(), name='academic-dashboard'),
    path('dashboard/overview/', views.AcademicOverviewView.as_view(), name='academic-overview'),
    path('dashboard/statistics/', views.DetailedStatisticsView.as_view(), name='detailed-statistics'),
    path('statistics/classes/', views.ClassStatisticsView.as_view(), name='class-statistics'),

    # ============================================
    # Bulk Operations
    # ============================================

    path('promotions/bulk/', views.BulkPromotionView.as_view(), name='bulk-promotion'),
    
    

    # ============================================
    # Public Views
    # ============================================

    path('public/structure/', views.PublicAcademicStructureView.as_view(), name='public-structure'),
    path('public/calendar/', views.PublicAcademicCalendarView.as_view(), name='public-calendar'),
    path('public/classes/<int:pk>/', views.PublicClassDetailView.as_view(), name='public-class-detail'),
]