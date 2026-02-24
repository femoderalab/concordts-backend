# academic/admin.py
"""
Django Admin configuration for Academic models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AcademicSession, AcademicTerm, Program, ClassLevel, 
    Subject, Class, ClassSubject
)


# ============================================
# ACADEMIC SESSION ADMIN
# ============================================

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    """Admin interface for AcademicSession"""
    
    list_display = ['name', 'start_date', 'end_date', 'status_display', 'is_current', 'total_days']
    list_filter = ['status', 'is_current']
    search_fields = ['name', 'description']
    readonly_fields = ['total_days', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'start_date', 'end_date', 'description')
        }),
        ('Status', {
            'fields': ('is_current', 'status')
        }),
        ('Read-only Information', {
            'fields': ('total_days', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['set_as_current', 'mark_as_completed']
    
    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'
    
    def total_days(self, obj):
        if obj.start_date and obj.end_date:
            delta = obj.end_date - obj.start_date
            return f"{delta.days} days"
        return "N/A"
    total_days.short_description = 'Duration'
    
    def set_as_current(self, request, queryset):
        """Set selected sessions as current"""
        for session in queryset:
            session.is_current = True
            session.save()
        self.message_user(request, f'{queryset.count()} session(s) set as current')
    set_as_current.short_description = 'Set as current session'
    
    def mark_as_completed(self, request, queryset):
        """Mark selected sessions as completed"""
        queryset.update(status='completed')
        self.message_user(request, f'{queryset.count()} session(s) marked as completed')
    mark_as_completed.short_description = 'Mark as completed'


# ============================================
# ACADEMIC TERM ADMIN
# ============================================

@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    """Admin interface for AcademicTerm"""
    
    list_display = ['name', 'session', 'term_display', 'start_date', 'end_date', 
                    'status_display', 'is_current', 'total_school_days']
    list_filter = ['session', 'term', 'status', 'is_current']
    search_fields = ['name', 'session__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('session', 'term', 'name', 'start_date', 'end_date')
        }),
        ('Nigerian School Calendar', {
            'fields': ('resumption_date', 'vacation_date', 'total_school_days',
                      'total_teaching_weeks', 'mid_term_break_start', 'mid_term_break_end')
        }),
        ('Status', {
            'fields': ('is_current', 'status')
        }),
        ('Read-only Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['set_as_current_term', 'calculate_school_days']
    
    def term_display(self, obj):
        return obj.get_term_display()
    term_display.short_description = 'Term'
    
    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'
    
    def set_as_current_term(self, request, queryset):
        """Set selected terms as current"""
        for term in queryset:
            term.is_current = True
            term.save()
        self.message_user(request, f'{queryset.count()} term(s) set as current')
    set_as_current_term.short_description = 'Set as current term'
    
    def calculate_school_days(self, request, queryset):
        """Calculate school days for selected terms"""
        for term in queryset:
            # Simple calculation (you can implement more complex logic)
            if term.start_date and term.end_date:
                delta = term.end_date - term.start_date
                # Approximate school days (5 days per week)
                term.total_school_days = (delta.days // 7) * 5
                term.save()
        self.message_user(request, f'Calculated school days for {queryset.count()} term(s)')
    calculate_school_days.short_description = 'Calculate school days'


# ============================================
# PROGRAM ADMIN
# ============================================

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Admin interface for Program"""
    
    list_display = ['name', 'code', 'program_type_display', 'duration_years', 'is_active']
    list_filter = ['program_type', 'is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'program_type', 'description')
        }),
        ('Configuration', {
            'fields': ('duration_years', 'is_active')
        }),
        ('Read-only Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_programs', 'deactivate_programs']
    
    def program_type_display(self, obj):
        return obj.get_program_type_display()
    program_type_display.short_description = 'Program Type'
    
    def activate_programs(self, request, queryset):
        """Activate selected programs"""
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} program(s) activated')
    activate_programs.short_description = 'Activate programs'
    
    def deactivate_programs(self, request, queryset):
        """Deactivate selected programs"""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} program(s) deactivated')
    deactivate_programs.short_description = 'Deactivate programs'


# ============================================
# CLASS LEVEL ADMIN
# ============================================

@admin.register(ClassLevel)
class ClassLevelAdmin(admin.ModelAdmin):
    """Admin interface for ClassLevel"""
    
    list_display = ['name', 'code', 'program', 'level_display', 'order', 
                    'min_age', 'max_age', 'is_active', 'get_students_count']
    list_filter = ['program', 'level', 'is_active']
    search_fields = ['name', 'code', 'program__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('program', 'level', 'name', 'code', 'order')
        }),
        ('Age Configuration', {
            'fields': ('min_age', 'max_age')
        }),
        ('Nigerian School System', {
            'fields': ('has_common_entrance', 'has_bece', 'has_waec_neco')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Read-only Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_levels', 'deactivate_levels']
    
    def level_display(self, obj):
        return obj.get_level_display()
    level_display.short_description = 'Class Level'
    
    def get_students_count(self, obj):
        """Get count of students in this class level"""
        try:
            return obj.students.count()
        except:
            return 0
    get_students_count.short_description = 'Students'
    
    def activate_levels(self, request, queryset):
        """Activate selected class levels"""
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} class level(s) activated')
    activate_levels.short_description = 'Activate class levels'
    
    def deactivate_levels(self, request, queryset):
        """Deactivate selected class levels"""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} class level(s) deactivated')
    deactivate_levels.short_description = 'Deactivate class levels'


# ============================================
# SUBJECT ADMIN
# ============================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface for Subject"""
    
    list_display = ['name', 'code', 'short_name', 'subject_type_display', 
                    'stream_display', 'is_compulsory', 'is_examinable', 'is_active']
    list_filter = ['subject_type', 'stream', 'is_compulsory', 'is_examinable', 'is_active']
    search_fields = ['name', 'code', 'short_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'availability_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'short_name', 'subject_type', 'description')
        }),
        ('Stream Configuration', {
            'fields': ('stream', 'is_compulsory', 'is_examinable', 'has_practical')
        }),
        ('Assessment Configuration', {
            'fields': ('ca_weight', 'exam_weight', 'total_marks', 'pass_mark')
        }),
        ('Class Level Availability', {
            'fields': ('available_for_creche', 'available_for_nursery',
                      'available_for_primary', 'available_for_jss', 'available_for_sss')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Read-only Information', {
            'fields': ('availability_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_subjects', 'deactivate_subjects']
    
    def subject_type_display(self, obj):
        return obj.get_subject_type_display()
    subject_type_display.short_description = 'Subject Type'
    
    def stream_display(self, obj):
        return obj.get_stream_display()
    stream_display.short_description = 'Stream'
    
    def availability_display(self, obj):
        """Display which levels this subject is available for"""
        levels = []
        if obj.available_for_creche:
            levels.append('Creche')
        if obj.available_for_nursery:
            levels.append('Nursery')
        if obj.available_for_primary:
            levels.append('Primary')
        if obj.available_for_jss:
            levels.append('JSS')
        if obj.available_for_sss:
            levels.append('SSS')
        return ', '.join(levels) if levels else 'None'
    availability_display.short_description = 'Available For'
    
    def activate_subjects(self, request, queryset):
        """Activate selected subjects"""
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} subject(s) activated')
    activate_subjects.short_description = 'Activate subjects'
    
    def deactivate_subjects(self, request, queryset):
        """Deactivate selected subjects"""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} subject(s) deactivated')
    deactivate_subjects.short_description = 'Deactivate subjects'


# ============================================
# CLASS ADMIN
# ============================================

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """Admin interface for Class"""
    
    list_display = ['name', 'code', 'session', 'term', 'class_level', 
                    'stream_display', 'class_teacher_display', 'current_enrollment',
                    'max_capacity', 'status_display', 'is_active']
    list_filter = ['session', 'term', 'class_level', 'stream', 'status', 'is_active']
    search_fields = ['name', 'code', 'room_number', 'building']
    readonly_fields = ['created_at', 'updated_at', 'capacity_percentage', 'assigned_subjects_list']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('session', 'term', 'class_level', 'name', 'code')
        }),
        ('Stream & Capacity', {
            'fields': ('stream', 'max_capacity', 'current_enrollment')
        }),
        ('Teachers', {
            'fields': ('class_teacher',)
        }),
        ('Location', {
            'fields': ('room_number', 'building')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Read-only Information', {
            'fields': ('capacity_percentage', 'assigned_subjects_list', 'slug', 
                      'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_classes', 'deactivate_classes']
    
    def stream_display(self, obj):
        return obj.get_stream_display() if obj.stream else 'General'
    stream_display.short_description = 'Stream'
    
    def class_teacher_display(self, obj):
        return obj.class_teacher.get_full_name() if obj.class_teacher else 'Not assigned'
    class_teacher_display.short_description = 'Class Teacher'
    
    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'
    
    def capacity_percentage(self, obj):
        """Calculate capacity percentage"""
        if obj.max_capacity > 0:
            percentage = (obj.current_enrollment / obj.max_capacity) * 100
            color = 'green' if percentage < 80 else 'orange' if percentage < 100 else 'red'
            return format_html(
                '<div style="background-color: {}; padding: 5px; border-radius: 3px; text-align: center;">'
                '{:.1f}% ({} / {})</div>',
                color, percentage, obj.current_enrollment, obj.max_capacity
            )
        return 'N/A'
    capacity_percentage.short_description = 'Capacity'
    
    def assigned_subjects_list(self, obj):
        """Display assigned subjects as HTML list"""
        subjects = obj.get_assigned_subjects()

        if not subjects:
            return "No subjects assigned"

        html = "<ul>"
        for subject in subjects:
            html += f"<li>{subject.name} ({subject.code})</li>"
        html += "</ul>"

        return format_html("{}", html)

    assigned_subjects_list.short_description = 'Assigned Subjects'
    
    def activate_classes(self, request, queryset):
        """Activate selected classes"""
        queryset.update(is_active=True, status='active')
        self.message_user(request, f'{queryset.count()} class(es) activated')
    activate_classes.short_description = 'Activate classes'
    
    def deactivate_classes(self, request, queryset):
        """Deactivate selected classes"""
        queryset.update(is_active=False, status='inactive')
        self.message_user(request, f'{queryset.count()} class(es) deactivated')
    deactivate_classes.short_description = 'Deactivate classes'


# ============================================
# CLASS SUBJECT ADMIN
# ============================================

@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    """Admin interface for ClassSubject"""
    
    list_display = ['class_name', 'subject_name', 'teacher_display', 
                    'is_active', 'is_compulsory']
    list_filter = ['class_obj', 'subject', 'is_active', 'is_compulsory']
    search_fields = ['class_obj__name', 'subject__name', 'teacher__first_name', 'teacher__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Assignment Information', {
            'fields': ('class_obj', 'subject', 'teacher')
        }),
        ('Configuration', {
            'fields': ('is_active', 'is_compulsory')
        }),
        ('Read-only Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_assignments', 'deactivate_assignments']
    
    def class_name(self, obj):
        return obj.class_obj.name
    class_name.short_description = 'Class'
    class_name.admin_order_field = 'class_obj__name'
    
    def subject_name(self, obj):
        return obj.subject.name
    subject_name.short_description = 'Subject'
    subject_name.admin_order_field = 'subject__name'
    
    def teacher_display(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else 'Not assigned'
    teacher_display.short_description = 'Teacher'
    
    def activate_assignments(self, request, queryset):
        """Activate selected assignments"""
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} assignment(s) activated')
    activate_assignments.short_description = 'Activate assignments'
    
    def deactivate_assignments(self, request, queryset):
        """Deactivate selected assignments"""
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} assignment(s) deactivated')
    deactivate_assignments.short_description = 'Deactivate assignments'