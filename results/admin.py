# # results/admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.urls import reverse
# from .models import (
#     StudentResult, SubjectScore, PsychomotorSkills,
#     AffectiveDomains, ResultPublishing
# )


# class SubjectScoreInline(admin.TabularInline):
#     """Inline admin for subject scores"""
#     model = SubjectScore
#     extra = 1
#     fields = ['subject', 'ca_score', 'exam_score', 'total_score', 'grade', 'observation_conduct']
#     readonly_fields = ['total_score', 'grade']
    
#     def has_change_permission(self, request, obj=None):
#         return True
    
#     def has_delete_permission(self, request, obj=None):
#         return True


# class PsychomotorSkillsInline(admin.StackedInline):
#     """Inline admin for psychomotor skills"""
#     model = PsychomotorSkills
#     extra = 1
#     fieldsets = [
#         ('Core Skills', {
#             'fields': [
#                 ('handwriting', 'verbal_fluency'),
#                 ('drawing_and_painting', 'tools_handling'),
#                 'sports'
#             ]
#         }),
#         ('Additional Skills', {
#             'fields': ['musical_skills', 'dancing', 'craft_work'],
#             'classes': ['collapse']
#         })
#     ]
    
#     def has_change_permission(self, request, obj=None):
#         return True


# class AffectiveDomainsInline(admin.StackedInline):
#     """Inline admin for affective domains"""
#     model = AffectiveDomains
#     extra = 1
#     fieldsets = [
#         ('Behavioral Assessment', {
#             'fields': [
#                 ('punctuality', 'neatness', 'politeness'),
#                 ('honesty', 'cooperation_with_others', 'leadership'),
#                 ('altruism', 'emotional_stability', 'health'),
#                 ('attitude', 'attentiveness', 'perseverance'),
#                 'communication_skill'
#             ]
#         })
#     ]
    
#     def has_change_permission(self, request, obj=None):
#         return True


# @admin.register(StudentResult)
# class StudentResultAdmin(admin.ModelAdmin):
#     """Admin for Student Results"""
#     list_display = [
#         'student_name', 'class_name', 'session', 'term',
#         'overall_total_score', 'percentage', 'overall_grade',
#         'position_in_class', 'is_published', 'is_promoted'
#     ]
    
#     list_filter = [
#         'session', 'term', 'class_level', 'overall_grade',
#         'is_published', 'is_promoted', 'created_at'
#     ]
    
#     search_fields = [
#         'student__user__first_name', 'student__user__last_name',
#         'student__admission_number', 'student__student_id'
#     ]
    
#     readonly_fields = [
#         'total_ca_score', 'total_exam_score', 'overall_total_score',
#         'total_obtainable', 'percentage', 'average_score',
#         'overall_grade', 'overall_remark', 'position_in_class',
#         'number_of_pupils_in_class', 'created_at', 'updated_at'
#     ]
    
#     fieldsets = [
#         ('Student Information', {
#             'fields': ['student', 'session', 'term', 'class_level']
#         }),
#         ('Attendance', {
#             'fields': [
#                 ('frequency_of_school_opened', 'no_of_times_present', 'no_of_times_absent')
#             ]
#         }),
#         ('Demographic Features', {
#             'fields': [
#                 ('weight_beginning_of_term', 'weight_end_of_term'),
#                 ('height_beginning_of_term', 'height_end_of_term')
#             ],
#             'classes': ['collapse']
#         }),
#         ('Academic Performance', {
#             'fields': [
#                 ('total_ca_score', 'total_exam_score'),
#                 ('overall_total_score', 'total_obtainable'),
#                 ('percentage', 'average_score'),
#                 ('position_in_class', 'number_of_pupils_in_class'),
#                 ('overall_grade', 'overall_remark')
#             ]
#         }),
#         ('Comments', {
#             'fields': ['class_teacher_comment', 'headmaster_comment']
#         }),
#         ('Next Term Information', {
#             'fields': ['next_term_begins_on', 'next_term_fees'],
#             'classes': ['collapse']
#         }),
#         ('Status & Approvals', {
#             'fields': [
#                 ('is_published', 'is_promoted'),
#                 ('class_teacher', 'class_teacher_signature_date'),
#                 ('headmaster', 'headmaster_signature_date')
#             ]
#         }),
#         ('Metadata', {
#             'fields': ['created_by', 'created_at', 'updated_at'],
#             'classes': ['collapse']
#         })
#     ]
    
#     inlines = [SubjectScoreInline, PsychomotorSkillsInline, AffectiveDomainsInline]
    
#     actions = ['publish_results', 'unpublish_results', 'mark_as_promoted', 'mark_as_not_promoted']
    
#     def student_name(self, obj):
#         """Display student name with link"""
#         url = reverse('admin:students_student_change', args=[obj.student.id])
#         return format_html('<a href="{}">{}</a>', url, obj.student.user.get_full_name())
#     student_name.short_description = 'Student'
#     student_name.admin_order_field = 'student__user__first_name'
    
#     def class_name(self, obj):
#         """Display class name"""
#         return obj.class_level.name
#     class_name.short_description = 'Class'
#     class_name.admin_order_field = 'class_level__name'
    
#     def publish_results(self, request, queryset):
#         """Action to publish selected results"""
#         updated = queryset.update(is_published=True)
#         self.message_user(request, f'{updated} results published successfully.')
#     publish_results.short_description = 'Publish selected results'
    
#     def unpublish_results(self, request, queryset):
#         """Action to unpublish selected results"""
#         updated = queryset.update(is_published=False)
#         self.message_user(request, f'{updated} results unpublished successfully.')
#     unpublish_results.short_description = 'Unpublish selected results'
    
#     def mark_as_promoted(self, request, queryset):
#         """Action to mark students as promoted"""
#         updated = queryset.update(is_promoted=True)
#         self.message_user(request, f'{updated} students marked as promoted.')
#     mark_as_promoted.short_description = 'Mark as promoted'
    
#     def mark_as_not_promoted(self, request, queryset):
#         """Action to mark students as not promoted"""
#         updated = queryset.update(is_promoted=False)
#         self.message_user(request, f'{updated} students marked as not promoted.')
#     mark_as_not_promoted.short_description = 'Mark as not promoted'
    
#     def save_model(self, request, obj, form, change):
#         """Set created_by user on save"""
#         if not obj.pk:
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
        
#     def delete_selected_results(self, request, queryset):
#         # Delete related records first
#         for result in queryset:
#             # Delete subject scores
#             result.subject_scores.all().delete()
#             # Delete psychomotor skills if exists
#             if hasattr(result, 'psychomotor_skills'):
#                 result.psychomotor_skills.delete()
#             # Delete affective domains if exists
#             if hasattr(result, 'affective_domains'):
#                 result.affective_domains.delete()
#             # Delete the result itself
#             result.delete()
        
#         self.message_user(request, f"Successfully deleted {queryset.count()} results.")
    
#     delete_selected_results.short_description = "Delete selected results with all related data"


# @admin.register(SubjectScore)
# class SubjectScoreAdmin(admin.ModelAdmin):
#     """Admin for Subject Scores"""
#     list_display = [
#         'student_name', 'subject', 'ca_score', 'exam_score',
#         'total_score', 'grade', 'observation_conduct'
#     ]
    
#     list_filter = ['subject', 'grade', 'observation_conduct', 'result__session', 'result__term']
    
#     search_fields = [
#         'result__student__user__first_name',
#         'result__student__user__last_name',
#         'subject__name', 'subject__code'
#     ]
    
#     readonly_fields = ['total_score', 'grade', 'aggregated_score', 'average_score']
    
#     fieldsets = [
#         ('Basic Information', {
#             'fields': ['result', 'subject']
#         }),
#         ('Scores', {
#             'fields': [
#                 ('ca_obtainable', 'ca_score'),
#                 ('exam_obtainable', 'exam_score'),
#                 ('total_obtainable', 'total_score')
#             ]
#         }),
#         ('Term Scores', {
#             'fields': ['first_term_score', 'second_term_score', 'third_term_score'],
#             'classes': ['collapse']
#         }),
#         ('Aggregated Data', {
#             'fields': ['aggregated_score', 'average_score', 'grade']
#         }),
#         ('Assessment', {
#             'fields': ['observation_conduct', 'subject_remark', 'position_in_subject']
#         }),
#         ('Teacher Comments', {
#             'fields': ['teacher_comment']
#         })
#     ]
    
#     def student_name(self, obj):
#         """Display student name"""
#         return obj.result.student.user.get_full_name()
#     student_name.short_description = 'Student'
#     student_name.admin_order_field = 'result__student__user__first_name'


# @admin.register(PsychomotorSkills)
# class PsychomotorSkillsAdmin(admin.ModelAdmin):
#     """Admin for Psychomotor Skills"""
#     list_display = ['student_name', 'overall_psychomotor_rating', 'created_at']
    
#     search_fields = [
#         'result__student__user__first_name',
#         'result__student__user__last_name'
#     ]
    
#     readonly_fields = ['overall_psychomotor_rating']
    
#     fieldsets = [
#         ('Result Information', {
#             'fields': ['result']
#         }),
#         ('Core Skills Assessment', {
#             'fields': [
#                 ('handwriting', 'verbal_fluency'),
#                 ('drawing_and_painting', 'tools_handling'),
#                 'sports'
#             ]
#         }),
#         ('Additional Skills Assessment', {
#             'fields': ['musical_skills', 'dancing', 'craft_work']
#         }),
#         ('Overall Rating', {
#             'fields': ['overall_psychomotor_rating']
#         })
#     ]
    
#     def student_name(self, obj):
#         """Display student name"""
#         return obj.result.student.user.get_full_name()
#     student_name.short_description = 'Student'


# @admin.register(AffectiveDomains)
# class AffectiveDomainsAdmin(admin.ModelAdmin):
#     """Admin for Affective Domains"""
#     list_display = ['student_name', 'overall_affective_rating', 'created_at']
    
#     search_fields = [
#         'result__student__user__first_name',
#         'result__student__user__last_name'
#     ]
    
#     readonly_fields = ['overall_affective_rating']
    
#     fieldsets = [
#         ('Result Information', {
#             'fields': ['result']
#         }),
#         ('Behavioral Assessment', {
#             'fields': [
#                 ('punctuality', 'neatness', 'politeness'),
#                 ('honesty', 'cooperation_with_others', 'leadership'),
#                 ('altruism', 'emotional_stability', 'health'),
#                 ('attitude', 'attentiveness', 'perseverance'),
#                 'communication_skill'
#             ]
#         }),
#         ('Comments', {
#             'fields': ['behavioral_comment']
#         }),
#         ('Overall Rating', {
#             'fields': ['overall_affective_rating']
#         })
#     ]
    
#     def student_name(self, obj):
#         """Display student name"""
#         return obj.result.student.user.get_full_name()
#     student_name.short_description = 'Student'


# @admin.register(ResultPublishing)
# class ResultPublishingAdmin(admin.ModelAdmin):
#     """Admin for Result Publishing"""
#     list_display = [
#         'session', 'term', 'class_name', 'is_published',
#         'published_date', 'published_by'
#     ]
    
#     list_filter = ['session', 'term', 'is_published', 'published_date']
    
#     search_fields = [
#         'session__name', 'term__name',
#         'class_level__name', 'published_by__first_name'
#     ]
    
#     readonly_fields = ['published_date']
    
#     fieldsets = [
#         ('Publishing Information', {
#             'fields': ['session', 'term', 'class_level']
#         }),
#         ('Status', {
#             'fields': ['is_published', 'published_date', 'published_by']
#         }),
#         ('Remarks', {
#             'fields': ['remarks']
#         })
#     ]
    
#     actions = ['publish_selected', 'unpublish_selected']
    
#     def class_name(self, obj):
#         """Display class name or 'All Classes'"""
#         return obj.class_level.name if obj.class_level else "All Classes"
#     class_name.short_description = 'Class'
    
#     def publish_selected(self, request, queryset):
#         """Action to publish selected"""
#         for obj in queryset:
#             obj.publish_results(request.user)
#         self.message_user(request, f'{queryset.count()} publishing entries activated.')
#     publish_selected.short_description = 'Publish selected'
    
#     def unpublish_selected(self, request, queryset):
#         """Action to unpublish selected"""
#         for obj in queryset:
#             obj.unpublish_results()
#         self.message_user(request, f'{queryset.count()} publishing entries deactivated.')
#     unpublish_selected.short_description = 'Unpublish selected'


"""
Admin configuration for Results App - UPDATED FOR class_level
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import (
    StudentResult, SubjectScore, PsychomotorSkills,
    AffectiveDomains, ResultPublishing
)


# ============================================
# INLINE ADMIN CLASSES
# ============================================

class SubjectScoreInline(admin.TabularInline):
    """Inline for subject scores in student result admin"""
    model = SubjectScore
    extra = 0
    readonly_fields = ['total_score', 'grade', 'average_score', 'aggregated_score']
    fields = [
        'subject', 'ca_score', 'exam_score', 'total_score', 'grade',
        'observation_conduct', 'subject_remark', 'teacher_comment'
    ]


class PsychomotorSkillsInline(admin.StackedInline):
    """Inline for psychomotor skills"""
    model = PsychomotorSkills
    extra = 0
    can_delete = False
    readonly_fields = ['overall_psychomotor_rating']
    fields = [
        'handwriting', 'verbal_fluency', 'drawing_and_painting',
        'tools_handling', 'sports', 'musical_skills', 'dancing',
        'craft_work', 'overall_psychomotor_rating'
    ]


class AffectiveDomainsInline(admin.StackedInline):
    """Inline for affective domains"""
    model = AffectiveDomains
    extra = 0
    can_delete = False
    readonly_fields = ['overall_affective_rating']
    fields = [
        'punctuality', 'neatness', 'politeness', 'honesty',
        'cooperation_with_others', 'leadership', 'altruism',
        'emotional_stability', 'health', 'attitude', 'attentiveness',
        'perseverance', 'communication_skill', 'behavioral_comment',
        'overall_affective_rating'
    ]


# ============================================
# ADMIN FILTERS
# ============================================

class PublishedFilter(admin.SimpleListFilter):
    """Filter by publication status"""
    title = 'Published Status'
    parameter_name = 'published'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Published'),
            ('no', 'Not Published'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_published=True)
        if self.value() == 'no':
            return queryset.filter(is_published=False)
        return queryset


class PromotedFilter(admin.SimpleListFilter):
    """Filter by promotion status"""
    title = 'Promotion Status'
    parameter_name = 'promoted'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Promoted'),
            ('no', 'Not Promoted'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(is_promoted=True)
        if self.value() == 'no':
            return queryset.filter(is_promoted=False)
        return queryset


class TermFilter(admin.SimpleListFilter):
    """Filter by academic term"""
    title = 'Academic Term'
    parameter_name = 'term'

    def lookups(self, request, model_admin):
        from academic.models import AcademicTerm
        terms = AcademicTerm.objects.filter(is_current=True)
        return [(t.id, t.name) for t in terms]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(term_id=self.value())
        return queryset


class SessionFilter(admin.SimpleListFilter):
    """Filter by academic session"""
    title = 'Academic Session'
    parameter_name = 'session'

    def lookups(self, request, model_admin):
        from academic.models import AcademicSession
        sessions = AcademicSession.objects.filter(is_current=True)
        return [(s.id, s.name) for s in sessions]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(session_id=self.value())
        return queryset


class ClassLevelFilter(admin.SimpleListFilter):
    """Filter by class level"""
    title = 'Class Level'
    parameter_name = 'class_level'

    def lookups(self, request, model_admin):
        from academic.models import ClassLevel
        class_levels = ClassLevel.objects.all().order_by('order')
        return [(cl.id, cl.name) for cl in class_levels]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(class_level_id=self.value())
        return queryset


# ============================================
# MAIN ADMIN CLASSES
# ============================================

@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    """Admin for StudentResult model"""
    
    list_display = [
        'student_info', 'class_level_display', 'session_display',
        'term_display', 'percentage', 'overall_grade', 'position_in_class',
        'is_published', 'is_promoted', 'created_at'
    ]
    
    list_filter = [
        PublishedFilter, PromotedFilter, TermFilter,
        SessionFilter, ClassLevelFilter, 'overall_grade'
    ]
    
    search_fields = [
        'student__user__first_name', 'student__user__last_name',
        'student__admission_number', 'student__user__registration_number'
    ]
    
    readonly_fields = [
        'total_ca_score', 'total_exam_score', 'overall_total_score',
        'total_obtainable', 'percentage', 'average_score', 
        'overall_grade', 'overall_remark', 'position_in_class',
        'number_of_pupils_in_class', 'created_by', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'student', 'session', 'term', 'class_level',
                ('created_by', 'created_at', 'updated_at')
            )
        }),
        ('Attendance', {
            'fields': (
                ('frequency_of_school_opened', 'no_of_times_present', 'no_of_times_absent'),
            )
        }),
        ('Performance Summary', {
            'fields': (
                ('total_ca_score', 'total_exam_score'),
                ('overall_total_score', 'total_obtainable'),
                ('percentage', 'average_score'),
                ('overall_grade', 'overall_remark'),
                ('position_in_class', 'number_of_pupils_in_class'),
            )
        }),
        ('Comments', {
            'fields': (
                'class_teacher_comment', 'headmaster_comment',
            )
        }),
        ('Next Term Information', {
            'fields': (
                'next_term_begins_on', 'next_term_fees',
            )
        }),
        ('Status', {
            'fields': (
                'is_published', 'is_promoted',
            )
        }),
        ('Approvals and Signatures', {
            'fields': (
                ('class_teacher', 'class_teacher_signature_date'),
                ('headmaster', 'headmaster_signature_date'),
            )
        }),
    )
    
    inlines = [SubjectScoreInline, PsychomotorSkillsInline, AffectiveDomainsInline]
    
    actions = ['publish_results', 'unpublish_results', 'promote_students', 'calculate_positions']
    
    def student_info(self, obj):
        """Display student information"""
        if obj.student and obj.student.user:
            return f"{obj.student.user.get_full_name()} ({obj.student.admission_number})"
        return "No Student"
    student_info.short_description = 'Student'
    student_info.admin_order_field = 'student__user__last_name'
    
    def class_level_display(self, obj):
        """Display class level"""
        return obj.class_level.name if obj.class_level else "No Class"
    class_level_display.short_description = 'Class'
    class_level_display.admin_order_field = 'class_level__name'
    
    def session_display(self, obj):
        """Display session"""
        return obj.session.name if obj.session else "No Session"
    session_display.short_description = 'Session'
    session_display.admin_order_field = 'session__name'
    
    def term_display(self, obj):
        """Display term"""
        return obj.term.name if obj.term else "No Term"
    term_display.short_description = 'Term'
    term_display.admin_order_field = 'term__term'
    
    # REMOVED THE BROKEN BADGE METHODS - using simple boolean display instead
    
    def publish_results(self, request, queryset):
        """Admin action to publish selected results"""
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} result(s) published successfully.')
    publish_results.short_description = "Publish selected results"
    
    def unpublish_results(self, request, queryset):
        """Admin action to unpublish selected results"""
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} result(s) unpublished successfully.')
    unpublish_results.short_description = "Unpublish selected results"
    
    def promote_students(self, request, queryset):
        """Admin action to promote selected students"""
        updated = queryset.update(is_promoted=True)
        self.message_user(request, f'{updated} student(s) marked as promoted.')
    promote_students.short_description = "Promote selected students"
    
    def calculate_positions(self, request, queryset):
        """Admin action to recalculate positions"""
        for result in queryset:
            result.calculate_position()
            result.save()
        self.message_user(request, f'Positions recalculated for {queryset.count()} result(s).')
    calculate_positions.short_description = "Recalculate positions"
    
    def save_model(self, request, obj, form, change):
        """Override save to set created_by"""
        if not obj.pk:
            obj.created_by = request.user
        obj.save()
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'student', 'student__user', 'session', 'term', 'class_level',
            'class_teacher', 'headmaster', 'created_by'
        ).prefetch_related('subject_scores')


@admin.register(SubjectScore)
class SubjectScoreAdmin(admin.ModelAdmin):
    """Admin for SubjectScore model"""
    
    list_display = [
        'student_info', 'subject_display', 'total_score', 'grade',
        'ca_score', 'exam_score', 'observation_conduct', 'teacher_comment_short'
    ]
    
    list_filter = ['grade', 'observation_conduct', 'subject_remark', 'subject']
    search_fields = [
        'result__student__user__first_name', 'result__student__user__last_name',
        'subject__name', 'subject__code'
    ]
    
    readonly_fields = ['total_score', 'grade', 'aggregated_score', 'average_score']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('result', 'subject')
        }),
        ('Scores', {
            'fields': (
                ('ca_obtainable', 'ca_score'),
                ('exam_obtainable', 'exam_score'),
                ('total_obtainable', 'total_score'),
            )
        }),
        ('Term Scores', {
            'fields': (
                'first_term_score', 'second_term_score', 'third_term_score',
                'aggregated_score', 'average_score'
            )
        }),
        ('Assessment', {
            'fields': (
                'grade', 'observation_conduct', 'subject_remark',
                'position_in_subject', 'teacher_comment'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def student_info(self, obj):
        """Display student information"""
        if obj.result and obj.result.student and obj.result.student.user:
            return obj.result.student.user.get_full_name()
        return "No Student"
    student_info.short_description = 'Student'
    student_info.admin_order_field = 'result__student__user__last_name'
    
    def subject_display(self, obj):
        """Display subject"""
        return f"{obj.subject.name} ({obj.subject.code})" if obj.subject else "No Subject"
    subject_display.short_description = 'Subject'
    subject_display.admin_order_field = 'subject__name'
    
    def teacher_comment_short(self, obj):
        """Display shortened teacher comment"""
        if obj.teacher_comment:
            if len(obj.teacher_comment) > 50:
                return f"{obj.teacher_comment[:50]}..."
            return obj.teacher_comment
        return "-"
    teacher_comment_short.short_description = 'Teacher Comment'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('result', 'result__student', 'result__student__user', 'subject')


@admin.register(PsychomotorSkills)
class PsychomotorSkillsAdmin(admin.ModelAdmin):
    """Admin for PsychomotorSkills model"""
    
    list_display = [
        'student_info', 'overall_psychomotor_rating',
        'handwriting', 'verbal_fluency', 'sports'
    ]
    
    list_filter = ['handwriting', 'verbal_fluency', 'sports']
    search_fields = [
        'result__student__user__first_name', 'result__student__user__last_name'
    ]
    
    readonly_fields = ['overall_psychomotor_rating']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('result',)
        }),
        ('Skills Assessment', {
            'fields': (
                ('handwriting', 'verbal_fluency', 'drawing_and_painting'),
                ('tools_handling', 'sports', 'musical_skills'),
                ('dancing', 'craft_work'),
            )
        }),
        ('Summary', {
            'fields': ('overall_psychomotor_rating',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def student_info(self, obj):
        """Display student information"""
        if obj.result and obj.result.student and obj.result.student.user:
            return obj.result.student.user.get_full_name()
        return "No Student"
    student_info.short_description = 'Student'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('result', 'result__student', 'result__student__user')


@admin.register(AffectiveDomains)
class AffectiveDomainsAdmin(admin.ModelAdmin):
    """Admin for AffectiveDomains model"""
    
    list_display = [
        'student_info', 'overall_affective_rating',
        'punctuality', 'neatness', 'honesty', 'attitude'
    ]
    
    list_filter = ['punctuality', 'neatness', 'honesty', 'attitude']
    search_fields = [
        'result__student__user__first_name', 'result__student__user__last_name'
    ]
    
    readonly_fields = ['overall_affective_rating']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('result',)
        }),
        ('Behavioral Assessment', {
            'fields': (
                ('punctuality', 'neatness', 'politeness'),
                ('honesty', 'cooperation_with_others', 'leadership'),
                ('altruism', 'emotional_stability', 'health'),
                ('attitude', 'attentiveness', 'perseverance'),
                ('communication_skill',),
            )
        }),
        ('Comments and Summary', {
            'fields': ('behavioral_comment', 'overall_affective_rating')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def student_info(self, obj):
        """Display student information"""
        if obj.result and obj.result.student and obj.result.student.user:
            return obj.result.student.user.get_full_name()
        return "No Student"
    student_info.short_description = 'Student'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('result', 'result__student', 'result__student__user')


@admin.register(ResultPublishing)
class ResultPublishingAdmin(admin.ModelAdmin):
    """Admin for ResultPublishing model"""
    
    list_display = [
        'session_display', 'term_display', 'class_level_display',
        'is_published', 'published_by_display', 'published_date_formatted',
        'results_count', 'created_at'
    ]
    
    list_filter = ['is_published', 'session', 'term', 'class_level']
    search_fields = [
        'session__name', 'term__name', 'class_level__name',
        'published_by__first_name', 'published_by__last_name'
    ]
    
    readonly_fields = ['published_date', 'published_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('session', 'term', 'class_level')
        }),
        ('Publishing Status', {
            'fields': ('is_published', 'published_date', 'published_by', 'remarks')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['publish_results_action', 'unpublish_results_action']
    
    def session_display(self, obj):
        """Display session"""
        return obj.session.name if obj.session else "No Session"
    session_display.short_description = 'Session'
    session_display.admin_order_field = 'session__name'
    
    def term_display(self, obj):
        """Display term"""
        return obj.term.name if obj.term else "No Term"
    term_display.short_description = 'Term'
    term_display.admin_order_field = 'term__name'
    
    def class_level_display(self, obj):
        """Display class level"""
        return obj.class_level.name if obj.class_level else "All Classes"
    class_level_display.short_description = 'Class Level'
    class_level_display.admin_order_field = 'class_level__name'
    
    def published_by_display(self, obj):
        """Display published by"""
        return obj.published_by.get_full_name() if obj.published_by else "Not Published"
    published_by_display.short_description = 'Published By'
    
    def published_date_formatted(self, obj):
        """Format published date"""
        return obj.published_date.strftime("%Y-%m-%d %H:%M") if obj.published_date else "-"
    published_date_formatted.short_description = 'Published Date'
    published_date_formatted.admin_order_field = 'published_date'
    
    def results_count(self, obj):
        """Count of results for this publishing entry"""
        from .models import StudentResult
        count = StudentResult.objects.filter(
            session=obj.session,
            term=obj.term
        )
        if obj.class_level:
            count = count.filter(class_level=obj.class_level)
        return count.count()
    results_count.short_description = 'Results Count'
    
    # REMOVED THE BROKEN BADGE METHOD
    
    def publish_results_action(self, request, queryset):
        """Admin action to publish results"""
        for publishing in queryset:
            publishing.publish_results(request.user)
        self.message_user(request, f'{queryset.count()} publishing record(s) published successfully.')
    publish_results_action.short_description = "Publish selected results"
    
    def unpublish_results_action(self, request, queryset):
        """Admin action to unpublish results"""
        for publishing in queryset:
            publishing.unpublish_results()
        self.message_user(request, f'{queryset.count()} publishing record(s) unpublished successfully.')
    unpublish_results_action.short_description = "Unpublish selected results"
    
    def save_model(self, request, obj, form, change):
        """Override save to handle publishing"""
        if not change and obj.is_published:
            # If creating and marking as published, set published_by
            obj.published_by = request.user
            obj.published_date = timezone.now()
        elif change and 'is_published' in form.changed_data and obj.is_published:
            # If changing to published, update fields
            obj.published_by = request.user
            obj.published_date = timezone.now()
        
        super().save_model(request, obj, form, change)
        
        # Actually publish/unpublish results
        if obj.is_published:
            obj.publish_results(request.user)
        else:
            obj.unpublish_results()
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('session', 'term', 'class_level', 'published_by')