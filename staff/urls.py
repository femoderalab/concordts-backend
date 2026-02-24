# # =====================================================================
# # STAFF URL CONFIGURATION - FIXED VERSION
# # File: staff/urls.py
# # =====================================================================

# """
# URL configuration for the staff app - SIMPLIFIED & FIXED VERSION

# The error you had was because:
# 1. We used ViewSet with manual @action(detail=True) destroy
# 2. Router also tries to create destroy endpoint
# 3. Both conflict!

# SOLUTION: Use ModelViewSet which provides destroy() automatically
# Then use @action for other custom endpoints like update_password, delete_file, etc.
# """

# from django.urls import path, include
# from rest_framework.routers import DefaultRouter

# # =====================
# # IMPORT VIEWS
# # =====================

# from .views import (
#     # Main ViewSet (provides list, create, retrieve, update, destroy automatically)
#     StaffViewSet,
    
#     # Class-based views (backward compatibility)
#     StaffListView,
#     StaffCreateView,
#     StaffDetailView,
#     StaffUpdateView,
#     StaffDashboardView,
#     StaffSearchView,
#     StaffStatisticsView,
#     BulkStaffCreateView,
#     update_staff_password,
    
#     # Staff operations
#     ActivateStaffView,
#     DeactivateStaffView,
#     RetireStaffView,
    
#     # Salary management
#     UpdateStaffSalaryView,
#     StaffSalaryView,
    
#     # Permission management
#     StaffPermissionDetailView,
#     StaffPermissionUpdateView,
    
#     # Teacher profile management
#     TeacherProfileListView,
#     TeacherProfileCreateView,
#     TeacherProfileDetailView,
#     StaffPasswordResetView,
# )

# # =====================
# # APP NAME & NAMESPACE
# # =====================

# app_name = 'staff'

# # =====================
# # ROUTER SETUP (RECOMMENDED)
# # =====================

# """
# DefaultRouter automatically creates these endpoints:

# ViewSet Standard Methods (provided by ModelViewSet):
# - GET    /api/                  → list()
# - POST   /api/                  → create()
# - GET    /api/<pk>/             → retrieve()
# - PUT    /api/<pk>/             → update()
# - PATCH  /api/<pk>/             → partial_update()
# - DELETE /api/<pk>/             → destroy()  ← This is automatic!

# Custom @action Methods (detail=True):
# - POST   /api/<pk>/update-password/  → update_password()
# - DELETE /api/<pk>/delete-file/      → delete_file()

# Custom @action Methods (detail=False):
# - GET    /api/stats/            → stats()
# - POST   /api/bulk-create/      → bulk_create()
# """

# router = DefaultRouter()
# router.register(r'api', StaffViewSet, basename='staff-api')

# # =====================
# # URL PATTERNS
# # =====================

# urlpatterns = [
#     # =====================
#     # ROUTER URLS (AUTO-GENERATED)
#     # =====================
#     # This single line provides ALL ViewSet endpoints:
#     # - list, create, retrieve, update, partial_update, destroy
#     # - custom actions: update_password, delete_file, stats, bulk_create
#     path('', include(router.urls)),
    
    
#     # =====================
#     # CLASS-BASED VIEW ENDPOINTS (BACKWARD COMPATIBILITY)
#     # =====================
#     # Keep these if you have existing code using them
    
#     path('list/', 
#          StaffListView.as_view(),
#          name='staff-list'),
    
#     path('create/',
#          StaffCreateView.as_view(),
#          name='staff-create'),
    
#     path('search/',
#          StaffSearchView.as_view(),
#          name='staff-search'),
    
#     path('statistics/',
#          StaffStatisticsView.as_view(),
#          name='staff-statistics'),
    
#     path('bulk-create/',
#          BulkStaffCreateView.as_view(),
#          name='staff-bulk-create'),
    
#     # Staff detail view
#     path('<int:pk>/',
#          StaffDetailView.as_view(),
#          name='staff-detail'),
    
#     # Staff update view
#     path('<int:pk>/update/',
#          StaffUpdateView.as_view(),
#          name='staff-update'),
    
#     # Staff dashboard
#     path('<int:pk>/dashboard/',
#          StaffDashboardView.as_view(),
#          name='staff-dashboard'),
    
    
#     # =====================
#     # STAFF STATUS MANAGEMENT
#     # =====================
    
#     # Activate staff member
#     path('<int:pk>/activate/',
#          ActivateStaffView.as_view(),
#          name='staff-activate'),
    
# #     path('<int:pk>/update-password/', update_staff_password, name='staff-update-password'),

    
#     # Deactivate staff member
#     path('<int:pk>/deactivate/',
#          DeactivateStaffView.as_view(),
#          name='staff-deactivate'),
    
#     # Retire staff member
#     path('<int:pk>/retire/',
#          RetireStaffView.as_view(),
#          name='staff-retire'),
    
    
#     # =====================
#     # SALARY MANAGEMENT
#     # =====================
    
#     # View staff salary
#     path('<int:pk>/salary/',
#          StaffSalaryView.as_view(),
#          name='staff-salary'),
    
#     # Update staff salary
#     path('<int:pk>/update-salary/',
#          UpdateStaffSalaryView.as_view(),
#          name='staff-update-salary'),
    
    
#     # =====================
#     # PERMISSION MANAGEMENT
#     # =====================
    
#     # View staff permissions
#     path('<int:pk>/permissions/',
#          StaffPermissionDetailView.as_view(),
#          name='staff-permissions'),
    
#     # Update staff permissions
#     path('<int:pk>/permissions/update/',
#          StaffPermissionUpdateView.as_view(),
#          name='staff-permissions-update'),
    
#     path('api/<int:staff_id>/update-password/', StaffPasswordResetView.as_view(), name='staff-password-reset'),
    
    
#     # =====================
#     # TEACHER PROFILE MANAGEMENT
#     # =====================
    
#     # List all teacher profiles
#     path('teachers/',
#          TeacherProfileListView.as_view(),
#          name='teacher-list'),
    
#     # Create teacher profile
#     path('teachers/create/',
#          TeacherProfileCreateView.as_view(),
#          name='teacher-create'),
    
#     # Get/Update teacher profile
#     path('teachers/<int:pk>/',
#          TeacherProfileDetailView.as_view(),
#          name='teacher-detail'),
    

#      path('<int:pk>/update-password/', update_staff_password, name='staff-update-password'),


# ]


# # =====================
# # IMPORTANT NOTES
# # =====================

# """
# KEY CHANGES FROM PREVIOUS VERSION:

# 1. Changed from ViewSet to ModelViewSet
#    - ModelViewSet automatically provides: list, create, retrieve, update, partial_update, destroy
#    - ViewSet requires manual implementation of these

# 2. Removed @action(detail=True, methods=['delete']) destroy()
#    - This was conflicting with router's automatic destroy
#    - Now using built-in destroy() from ModelViewSet

# 3. Kept custom @action decorators for:
#    - update_password (POST /api/<pk>/update-password/)
#    - delete_file (DELETE /api/<pk>/delete-file/)
#    - stats (GET /api/stats/)
#    - bulk_create (POST /api/bulk-create/)

# 4. Router automatically handles all the URL patterns
#    - No manual ViewSet.as_view() needed
#    - All @action methods are automatically routed

# ENDPOINTS PROVIDED:

# Standard CRUD (from ModelViewSet):
# - GET    /staff/api/                     - List all staff
# - POST   /staff/api/                     - Create staff
# - GET    /staff/api/<id>/                - Get staff details
# - PUT    /staff/api/<id>/                - Full update
# - PATCH  /staff/api/<id>/                - Partial update
# - DELETE /staff/api/<id>/                - Delete staff ← No more conflict!

# Custom Actions (from @action decorators):
# - POST   /staff/api/<id>/update-password/       - Update password
# - DELETE /staff/api/<id>/delete-file/?file_type=X - Delete file
# - GET    /staff/api/stats/                      - Get statistics
# - POST   /staff/api/bulk-create/                - Bulk create staff

# Class-based Views (backward compatibility):
# - GET    /staff/list/                   - List staff
# - POST   /staff/create/                 - Create staff
# - GET    /staff/<id>/                   - Get staff details
# - And many more...

# TESTING:

# List staff:
#   curl http://localhost:8000/staff/api/

# Get staff:
#   curl http://localhost:8000/staff/api/1/

# Create staff:
#   curl -X POST http://localhost:8000/staff/api/ \
#     -H "Content-Type: application/json" \
#     -d '{"user_id": 1, "department": "academic"}'

# Update staff:
#   curl -X PUT http://localhost:8000/staff/api/1/ \
#     -H "Content-Type: application/json" \
#     -d '{"position_title": "Senior Teacher"}'

# Delete staff:
#   curl -X DELETE http://localhost:8000/staff/api/1/

# Update password:
#   curl -X POST http://localhost:8000/staff/api/1/update-password/ \
#     -H "Content-Type: application/json" \
#     -d '{"new_password": "NewPass123!", "confirm_password": "NewPass123!"}'

# Delete file:
#   curl -X DELETE "http://localhost:8000/staff/api/1/delete-file/?file_type=passport_photo"

# Get statistics:
#   curl http://localhost:8000/staff/api/stats/

# Bulk create:
#   curl -X POST http://localhost:8000/staff/api/bulk-create/ \
#     -H "Content-Type: application/json" \
#     -d '{"staff": [{"user_id": 1, "department": "academic"}, ...]}'
# """


# =====================================================================
# STAFF URL CONFIGURATION - FIXED VERSION
# File: staff/urls.py
# =====================================================================

"""
URL configuration for the staff app - FIXED VERSION
The error was caused by duplicate router registration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# =====================
# IMPORT VIEWS
# =====================
from .views import (
    # Main ViewSet
    StaffViewSet,
    
    # Class-based views
    StaffListView,
    StaffCreateView,
    StaffDetailView,
    StaffUpdateView,
    StaffDashboardView,
    StaffSearchView,
    StaffStatisticsView,
    BulkStaffCreateView,
    update_staff_password,
    
    # Staff operations
    ActivateStaffView,
    DeactivateStaffView,
    RetireStaffView,
    
    # Salary management
    UpdateStaffSalaryView,
    StaffSalaryView,
    
    # Permission management
    StaffPermissionDetailView,
    StaffPermissionUpdateView,
    
    # Teacher profile management
    TeacherProfileListView,
    TeacherProfileCreateView,
    TeacherProfileDetailView,
    
    # Password reset
    StaffPasswordResetView,
)

# =====================
# APP NAME & NAMESPACE
# =====================
app_name = 'staff'

# =====================
# ROUTER SETUP
# =====================
# Create router ONLY ONCE
router = DefaultRouter()
router.register(r'api', StaffViewSet, basename='staff-api')

# =====================
# URL PATTERNS
# =====================
urlpatterns = [
    # =====================
    # ROUTER URLS - ALL AUTOMATIC ENDPOINTS
    # =====================
    # This includes:
    # GET    /api/           - list
    # POST   /api/           - create
    # GET    /api/<pk>/      - retrieve
    # PUT    /api/<pk>/      - update
    # PATCH  /api/<pk>/      - partial_update
    # DELETE /api/<pk>/      - destroy
    # POST   /api/<pk>/update-password/  - custom action
    # DELETE /api/<pk>/delete-file/      - custom action
    # GET    /api/stats/     - custom action
    # POST   /api/bulk-create/ - custom action
    path('', include(router.urls)),
    
    # =====================
    # EXPLICIT PASSWORD RESET ENDPOINT (YOUR NEW ONE)
    # =====================
    path('api/<int:staff_id>/update-password/', 
         StaffPasswordResetView.as_view(), 
         name='staff-password-reset'),
    
    # =====================
    # CLASS-BASED VIEW ENDPOINTS (BACKWARD COMPATIBILITY)
    # =====================
    path('list/', StaffListView.as_view(), name='staff-list'),
    path('create/', StaffCreateView.as_view(), name='staff-create'),
    path('search/', StaffSearchView.as_view(), name='staff-search'),
    path('statistics/', StaffStatisticsView.as_view(), name='staff-statistics'),
    path('bulk-create/', BulkStaffCreateView.as_view(), name='staff-bulk-create'),
    
    # Staff detail view
    path('<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    
    # Staff update view
    path('<int:pk>/update/', StaffUpdateView.as_view(), name='staff-update'),
    
    # Staff dashboard
    path('<int:pk>/dashboard/', StaffDashboardView.as_view(), name='staff-dashboard'),
    
    # =====================
    # STAFF STATUS MANAGEMENT
    # =====================
    path('<int:pk>/activate/', ActivateStaffView.as_view(), name='staff-activate'),
    path('<int:pk>/deactivate/', DeactivateStaffView.as_view(), name='staff-deactivate'),
    path('<int:pk>/retire/', RetireStaffView.as_view(), name='staff-retire'),
    
    # =====================
    # SALARY MANAGEMENT
    # =====================
    path('<int:pk>/salary/', StaffSalaryView.as_view(), name='staff-salary'),
    path('<int:pk>/update-salary/', UpdateStaffSalaryView.as_view(), name='staff-update-salary'),
    
    # =====================
    # PERMISSION MANAGEMENT
    # =====================
    path('<int:pk>/permissions/', StaffPermissionDetailView.as_view(), name='staff-permissions'),
    path('<int:pk>/permissions/update/', StaffPermissionUpdateView.as_view(), name='staff-permissions-update'),
    
    # =====================
    # LEGACY PASSWORD ENDPOINT (if needed)
    # =====================
    path('<int:pk>/update-password/', update_staff_password, name='staff-update-password'),
    
    # =====================
    # TEACHER PROFILE MANAGEMENT
    # =====================
    path('teachers/', TeacherProfileListView.as_view(), name='teacher-list'),
    path('teachers/create/', TeacherProfileCreateView.as_view(), name='teacher-create'),
    path('teachers/<int:pk>/', TeacherProfileDetailView.as_view(), name='teacher-detail'),
]