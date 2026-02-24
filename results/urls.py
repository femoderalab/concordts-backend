# results/urls.py
"""
URL configuration for results app - SIMPLE VERSION (No Router)
"""

from django.urls import path
from . import views

urlpatterns = [
    # ============ Student Results ============
    # Basic CRUD
    path('results/', views.StudentResultViewSet.as_view({'get': 'list', 'post': 'create'}), name='result-list'),
    path('results/<int:pk>/', views.StudentResultViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='result-detail'),
    
    # Custom Actions
    path('results/by-student/', views.StudentResultViewSet.as_view({'get': 'by_student'}), name='by-student'),
    path('results/by-class/', views.StudentResultViewSet.as_view({'get': 'by_class'}), name='by-class'),
    path('results/my-results/', views.StudentResultViewSet.as_view({'get': 'student_self_results'}), name='my-results'),
    path('results/search/', views.StudentResultViewSet.as_view({'get': 'search'}), name='search-results'),
    path('results/bulk-upload/', views.StudentResultViewSet.as_view({'post': 'bulk_upload'}), name='bulk-upload'),
    path('results/<int:pk>/add-subject-scores/', views.StudentResultViewSet.as_view({'post': 'add_subject_scores'}), name='add-subject-scores'),
    path('results/<int:pk>/approve/', views.StudentResultViewSet.as_view({'post': 'approve_result'}), name='approve-result'),
    path('results/<int:pk>/publish/', views.StudentResultViewSet.as_view({'post': 'publish'}), name='publish-result'),
    path('results/<int:pk>/download-report/', views.StudentResultViewSet.as_view({'get': 'download_report'}), name='download-report'),
    
    # ============ Subject Scores ============
    path('subject-scores/', views.SubjectScoreViewSet.as_view({'get': 'list', 'post': 'create'}), name='subject-score-list'),
    path('subject-scores/<int:pk>/', views.SubjectScoreViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='subject-score-detail'),
    
    # ============ Psychomotor Skills ============
    path('psychomotor-skills/', views.PsychomotorSkillsViewSet.as_view({'get': 'list', 'post': 'create'}), name='psychomotor-list'),
    path('psychomotor-skills/<int:pk>/', views.PsychomotorSkillsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='psychomotor-detail'),
    
    # ============ Affective Domains ============
    path('affective-domains/', views.AffectiveDomainsViewSet.as_view({'get': 'list', 'post': 'create'}), name='affective-list'),
    path('affective-domains/<int:pk>/', views.AffectiveDomainsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='affective-detail'),
    
    # ============ Result Publishing ============
    path('result-publishing/', views.ResultPublishingViewSet.as_view({'get': 'list', 'post': 'create'}), name='result-publishing-list'),
    path('result-publishing/<int:pk>/', views.ResultPublishingViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='result-publishing-detail'),
    path('result-publishing/<int:pk>/toggle-publish/', views.ResultPublishingViewSet.as_view({'post': 'toggle_publish'}), name='toggle-publish'),
    path('result-publishing/publishing-status/', views.ResultPublishingViewSet.as_view({'get': 'publishing_status'}), name='publishing-status'),
    
    # ============ Statistics ============
    path('statistics/', views.ResultStatisticsView.as_view(), name='result-statistics'),
]