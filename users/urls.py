"""
URL configuration for the users app.
"""

from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, CustomTokenObtainPairView, LogoutView,
    UserProfileView, AdminResetPasswordView, UserListView,
    UserDetailView, VerifyUserView, DeactivateUserView,
    ActivateUserView, UpdateUserRoleView, AdminDashboardView, 
    AdminDirectPasswordResetView, check_user_exists,
    ActivityViewSet, LogActivityView, AdminResetPasswordView
)

# Router for standard CRUD operations
# IMPORTANT: Disable format suffix to avoid conflicts
router = DefaultRouter()
router.include_format_suffixes = False  # Add this line

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User checks
    path('check-user-exists/', check_user_exists, name='check_user_exists'),
    
    # Profile management
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    path('admin/reset-password/', AdminResetPasswordView.as_view(), name='admin-reset-password'),
    
    # # Password management
    # path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    # path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    # path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    
    # Admin endpoints
    path('admin/reset-password/', AdminResetPasswordView.as_view(), name='admin_reset_password'),
    path('admin/users/', UserListView.as_view(), name='user_list'),
    path('admin/users/<str:registration_number>/', UserDetailView.as_view(), name='user_detail'),
    path('admin/verify/<str:registration_number>/', VerifyUserView.as_view(), name='verify_user'),
    path('admin/deactivate/<str:registration_number>/', DeactivateUserView.as_view(), name='deactivate_user'),
    path('admin/activate/<str:registration_number>/', ActivateUserView.as_view(), name='activate_user'),
    path('admin/update-role/<str:registration_number>/', UpdateUserRoleView.as_view(), name='update_user_role'),
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/direct-reset-password/', AdminDirectPasswordResetView.as_view(), name='admin_direct_reset_password'),
    
    # Activity custom endpoints (must come BEFORE router.urls to avoid conflicts)
    path('activities/recent/', ActivityViewSet.as_view({'get': 'recent'}), name='recent_activities'),
    path('activities/statistics/', ActivityViewSet.as_view({'get': 'statistics'}), name='activity_statistics'),
    path('activities/unread-count/', ActivityViewSet.as_view({'get': 'unread_count'}), name='unread_count'),
    path('activities/mark-all-read/', ActivityViewSet.as_view({'post': 'mark_all_read'}), name='mark_all_read'),
    path('activities/log/', LogActivityView.as_view(), name='log_activity'),
    path('activities/user/<int:user_id>/', ActivityViewSet.as_view({'get': 'user_activities'}), name='user_activities'),
    path('activities/<uuid:pk>/mark-read/', ActivityViewSet.as_view({'post': 'mark_read'}), name='mark_read'),
]

# Include router URLs for standard CRUD (list, retrieve, etc.)
urlpatterns += router.urls