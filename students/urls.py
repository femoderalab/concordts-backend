"""URL configuration for the students app."""
from django.urls import path
from .views import (
    StudentListView, StudentCreateView, StudentDetailView, StudentUpdateView,
    StudentDashboardView, UpdateStudentFeeView, PromoteStudentView,
    StudentEnrollmentListView, StudentEnrollmentCreateView,
    StudentAttendanceUpdateView, StudentSearchView,
    StudentStatisticsView, StudentDocumentUploadView,
    StudentCreateWithUserView, StudentDeleteView, SimpleStudentCreateView,
    StudentViewSet, SecretaryFinancialAnalyticsView
)

app_name = "students"

# Manual URL patterns for ViewSet - SIMPLIFIED CORRECT VERSION
student_viewset = StudentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})


# FIXED: Separate viewset for retrieve-only
student_retrieve_viewset = StudentViewSet.as_view({
    'get': 'retrieve'
})

# FIXED: Separate viewset for update-only
student_update_viewset = StudentViewSet.as_view({
    'put': 'full_update',
    'patch': 'full_update'
})

# FIXED: Separate viewset for delete-only
student_delete_viewset = StudentViewSet.as_view({
    'delete': 'destroy'
})

# Separate viewset for password update
student_password_viewset = StudentViewSet.as_view({
    'post': 'update_password'
})

# Separate viewset for file delete
student_file_viewset = StudentViewSet.as_view({
    'delete': 'delete_file'
})

# Separate viewset for stats
student_stats_viewset = StudentViewSet.as_view({
    'get': 'stats'
})

urlpatterns = [
    # =====================
    # VIEWSET ENDPOINTS (FIXED)
    # =====================
    path('api/', student_viewset, name='student-api-list'),
    
    # FIXED: Use retrieve-only for GET requests
    path('api/<int:pk>/', student_retrieve_viewset, name='student-api-detail'),
    
    # Individual actions as separate endpoints
    path('api/<int:pk>/full-update/', 
         student_update_viewset, 
         name='student-api-full-update'),
    
    path('api/<int:pk>/update-password/', 
         student_password_viewset,
         name='student-api-update-password'),
    
    path('api/<int:pk>/delete-file/<str:file_type>/', 
         student_file_viewset,
         name='student-api-delete-file'),
    
    path('api/<int:pk>/delete/', 
         student_delete_viewset,
         name='student-api-delete'),
    
    path('api/stats/', 
         student_stats_viewset,
         name='student-api-stats'),
    
    # =====================
    # ORIGINAL ENDPOINTS (for backward compatibility)
    # =====================
    path('list/', StudentListView.as_view(), name='student-list'),
    path('create/', StudentCreateView.as_view(), name='student-create'),
    path('search/', StudentSearchView.as_view(), name='student-search'),
    path('statistics/', StudentStatisticsView.as_view(), name='student-statistics'),
    path('create-with-user/', StudentCreateWithUserView.as_view(), name='student-create-with-user'),
    path('simple-create/', SimpleStudentCreateView.as_view(), name='student-simple-create'),
    path('<int:pk>/delete/', StudentDeleteView.as_view(), name='student-delete'),
    
    # Individual student operations
    path('<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('<int:pk>/update/', StudentUpdateView.as_view(), name='student-update'),
    path('<int:pk>/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    
    # Fee management
    path('<int:pk>/update-fee/', UpdateStudentFeeView.as_view(), name='student-update-fee'),
    
    # Academic operations
    path('<int:pk>/promote/', PromoteStudentView.as_view(), name='student-promote'),
    path('<int:pk>/attendance/', StudentAttendanceUpdateView.as_view(), name='student-attendance'),
    
    # Document management
    path('<int:pk>/upload-document/', StudentDocumentUploadView.as_view(), name='student-upload-document'),
    
    # Add to your urlpatterns:
    path('api/financial-analytics/', SecretaryFinancialAnalyticsView.as_view(), name='financial-analytics'),
    
    path('dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),

    
    # Student enrollment
    path('enrollments/', StudentEnrollmentListView.as_view(), name='enrollment-list'),
    path('enrollments/create/', StudentEnrollmentCreateView.as_view(), name='enrollment-create'),
]