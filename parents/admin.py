# parents/admin.py
"""
Django Admin configuration for Parent model.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Parent


class ParentAdmin(admin.ModelAdmin):
    """Admin interface for Parent model"""
    
    list_display = [
        'get_full_name', 'parent_id', 'parent_type_display',
        'get_email', 'get_phone', 'children_count',
        'is_pta_member', 'is_active', 'is_verified'
    ]
    
    list_filter = [
        'parent_type', 'marital_status', 'is_pta_member',
        'is_active', 'is_verified', 'preferred_communication'
    ]
    
    search_fields = [
        'user__first_name', 'user__last_name', 
        'user__email', 'parent_id', 'occupation', 'employer'
    ]
    
    readonly_fields = [
        'parent_id', 'created_at', 'updated_at',
        'get_children_list', 'get_fee_summary_html'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'user', 'parent_type', 'parent_id',
                ('occupation', 'employer'),
                'employer_address', 'office_phone'
            )
        }),
        ('Family Information', {
            'fields': (
                'marital_status', 'spouse',
                'emergency_contact_name', 'emergency_contact_phone',
                'emergency_contact_relationship'
            )
        }),
        ('Communication Preferences', {
            'fields': (
                'preferred_communication',
                ('receive_sms_alerts', 'receive_email_alerts')
            )
        }),
        ('Financial Information', {
            'fields': (
                'annual_income_range',
                ('bank_name', 'account_name', 'account_number')
            )
        }),
        ('PTA Information', {
            'fields': (
                'is_pta_member', 'pta_position', 'pta_committee'
            )
        }),
        ('Declaration', {
            'fields': (
                'declaration_accepted', 'declaration_date',
                'declaration_signature'
            )
        }),
        ('Status', {
            'fields': (
                'is_active', 'is_verified'
            )
        }),
        ('Read-only Information', {
            'fields': (
                'get_children_list', 'get_fee_summary_html',
                ('created_at', 'updated_at')
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_parents', 'deactivate_parents', 'verify_parents']
    
    def get_full_name(self, obj):
        """Get parent's full name"""
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'user__first_name'
    
    def get_email(self, obj):
        """Get parent's email"""
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_phone(self, obj):
        """Get parent's phone"""
        return obj.user.phone_number
    get_phone.short_description = 'Phone'
    
    def parent_type_display(self, obj):
        """Display parent type"""
        return obj.get_parent_type_display()
    parent_type_display.short_description = 'Parent Type'
    
    def children_count(self, obj):
        """Display number of children"""
        return obj.get_children_count()
    children_count.short_description = 'Children'
    
    def get_children_list(self, obj):
        """Display children as HTML list"""
        children = obj.get_children()
        
        if not children:
            return "No children"

        html = "<ul>"
        for child in children:
            html += f"<li>{child.user.get_full_name()} - {child.admission_number}</li>"
        html += "</ul>"

        return format_html("{}", html)

    get_children_list.short_description = 'Children List'
    
    def get_fee_summary_html(self, obj):
        """Display fee summary as HTML"""
        try:
            summary = obj.get_fee_summary()
            html = f"""
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                <strong>Total Children:</strong> {summary.get('total_children', 0)}<br>
                <strong>Total Fee:</strong> ₦{summary.get('total_fee', 0):,.2f}<br>
                <strong>Total Paid:</strong> ₦{summary.get('paid', 0):,.2f}<br>
                <strong>Balance Due:</strong> ₦{summary.get('balance', 0):,.2f}<br>
                <strong>Percentage Paid:</strong> {summary.get('percentage_paid', 0)}%
            </div>
            """
            return format_html(html)
        except Exception as e:
            return f"Error: {str(e)}"
    get_fee_summary_html.short_description = 'Fee Summary'
    
    def activate_parents(self, request, queryset):
        """Activate selected parents"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} parents activated.')
    activate_parents.short_description = 'Activate selected parents'
    
    def deactivate_parents(self, request, queryset):
        """Deactivate selected parents"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} parents deactivated.')
    deactivate_parents.short_description = 'Deactivate selected parents'
    
    def verify_parents(self, request, queryset):
        """Verify selected parents"""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} parents verified.')
    verify_parents.short_description = 'Verify selected parents'
    
    def save_model(self, request, obj, form, change):
        """Save parent model with auto-generated ID"""
        if not obj.parent_id:
            # Auto-generate parent ID
            import random
            import string
            prefix = "PAR"
            while True:
                random_num = ''.join(random.choices(string.digits, k=6))
                parent_id = f"{prefix}{random_num}"
                if not Parent.objects.filter(parent_id=parent_id).exists():
                    obj.parent_id = parent_id
                    break
        
        # Update user role if needed
        if obj.user.role != 'parent':
            obj.user.role = 'parent'
            obj.user.save()
        
        super().save_model(request, obj, form, change)


admin.site.register(Parent, ParentAdmin)