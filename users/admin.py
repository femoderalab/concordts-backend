"""
Admin configuration for User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, Activity  # Add Activity to imports



class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for User model.
    """
    
    # Fields to display in list view
    list_display = (
        'registration_number', 'email', 'first_name', 'last_name', 
        'role', 'is_active', 'is_verified', 'last_login', 'created_at'
    )
    
    # Filter options
    list_filter = (
        'role', 'is_active', 'is_verified', 'gender', 
        'state_of_origin', 'created_at'
    )
    
    # Search fields
    search_fields = (
        'registration_number', 'email', 'first_name', 
        'last_name', 'phone_number'
    )
    
    # Ordering
    ordering = ('-created_at',)
    
    # Fields in detail view
    fieldsets = (
        ('Authentication', {
            'fields': ('registration_number', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'gender', 'date_of_birth')
        }),
        ('Contact Info', {
            'fields': ('phone_number', 'alternative_phone', 'address', 'city', 'state_of_origin', 'lga', 'nationality')
        }),
        ('Account Info', {
            'fields': ('role', 'profile_picture')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'login_count', 'last_login_ip')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    
    # Fields when adding new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'email', 
                'phone_number', 'role', 'password1', 'password2'
            ),
        }),
    )
    
    # Read-only fields
    readonly_fields = (
        'registration_number', 'login_count', 'last_login_ip',
        'created_at', 'updated_at', 'last_login', 'date_joined'
    )
    
    def get_queryset(self, request):
        """
        Custom queryset for admin.
        """
        qs = super().get_queryset(request)
        # Show all users to superusers, others see limited
        if request.user.is_superuser:
            return qs
        return qs
    
    def save_model(self, request, obj, form, change):
        """
        Custom save method to handle password hashing.
        """
        if 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
    
    def user_actions(self, obj):
        """
        Custom action buttons for user list.
        """
        return format_html(
            '''
            <div>
                <a href="/admin/users/user/{}/change/" class="button">Edit</a>
                <a href="/admin/users/user/{}/delete/" class="button">Delete</a>
                {}
            </div>
            ''',
            obj.id, obj.id,
            'Active' if obj.is_active else 'Inactive'
        )
    
    user_actions.short_description = 'Actions'

# Add this to your admin registration
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'action', 'user_name', 'user_role', 'created_at', 'is_read')
    list_filter = ('activity_type', 'is_read', 'is_system', 'created_at')
    search_fields = ('action', 'description', 'user_name', 'target_name')
    readonly_fields = ('created_at', 'updated_at', 'read_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Activity Details', {
            'fields': ('activity_type', 'action', 'description', 'is_system')
        }),
        ('User Information', {
            'fields': ('user', 'user_name', 'user_role')
        }),
        ('Target Information', {
            'fields': ('target_type', 'target_id', 'target_name')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Metadata', {
            'fields': ('metadata', 'ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Register the custom admin
admin.site.register(User, CustomUserAdmin)
