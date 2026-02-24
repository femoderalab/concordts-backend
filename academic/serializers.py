# academic/serializers.py
"""
Updated Serializers for Academic App
Compatible with Nigerian school models - ERROR FREE VERSION
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from .models import (
    AcademicSession, AcademicTerm, Program, ClassLevel, Subject,
    Class, ClassSubject
)


# ============================================
# ACADEMIC SESSION SERIALIZERS
# ============================================

class AcademicSessionSerializer(serializers.ModelSerializer):
    """Serializer for AcademicSession model"""

    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AcademicSession
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'status_display']

    def validate(self, data):
        """Validate session dates"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'
                })
        return data


class AcademicSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for session lists"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AcademicSession
        fields = ['id', 'name', 'start_date', 'end_date', 'status', 'status_display', 'is_current']


# ============================================
# ACADEMIC TERM SERIALIZERS
# ============================================

class AcademicTermSerializer(serializers.ModelSerializer):
    """Serializer for AcademicTerm model"""

    session_info = serializers.SerializerMethodField(read_only=True)
    term_display = serializers.CharField(source='get_term_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = AcademicTerm
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'term_display', 'status_display']

    def get_session_info(self, obj):
        if obj.session:
            return {
                'id': obj.session.id,
                'name': obj.session.name,
                'start_date': obj.session.start_date,
                'end_date': obj.session.end_date,
            }
        return None

    def validate(self, data):
        """Validate term dates"""
        session = data.get('session') or (self.instance.session if self.instance else None)

        if data.get('start_date') and data.get('end_date') and session:
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'
                })

            # Check if dates are within session
            if data['start_date'] < session.start_date or data['end_date'] > session.end_date:
                raise serializers.ValidationError({
                    'dates': 'Term dates must be within session dates'
                })

        return data


class AcademicTermListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for term lists"""
    
    session_name = serializers.CharField(source='session.name', read_only=True)
    term_display = serializers.CharField(source='get_term_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AcademicTerm
        fields = ['id', 'name', 'session', 'session_name', 'term', 'term_display', 
                 'start_date', 'end_date', 'status', 'status_display', 'is_current']


# ============================================
# PROGRAM SERIALIZERS
# ============================================

class ProgramSerializer(serializers.ModelSerializer):
    """Serializer for Program model"""

    program_type_display = serializers.CharField(source='get_program_type_display', read_only=True)

    class Meta:
        model = Program
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'program_type_display']


class ProgramListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for program lists"""
    
    program_type_display = serializers.CharField(source='get_program_type_display', read_only=True)
    
    class Meta:
        model = Program
        fields = ['id', 'name', 'code', 'program_type', 'program_type_display', 
                 'duration_years', 'is_active']


# ============================================
# CLASS LEVEL SERIALIZERS
# ============================================

class ClassLevelSerializer(serializers.ModelSerializer):
    program_info = serializers.SerializerMethodField(read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = ClassLevel
        fields = [
            'id',
            'program',
            'program_info',
            'level',
            'level_display',
            'name',
            'code',
            'order',
            'min_age',
            'max_age',
            'is_active',
        ]

    def get_program_info(self, obj):
        return {
            'id': obj.program.id,
            'name': obj.program.name,
            'code': obj.program.code,
        } if obj.program else None



class ClassLevelListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for class level lists"""
    
    program_name = serializers.CharField(source='program.name', read_only=True)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = ClassLevel
        fields = ['id', 'name', 'code', 'program', 'program_name', 'level', 
                 'level_display', 'order', 'is_active']


# ============================================
# SUBJECT SERIALIZERS
# ============================================

class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model"""

    subject_type_display = serializers.CharField(source='get_subject_type_display', read_only=True)
    stream_display = serializers.CharField(source='get_stream_display', read_only=True)
    availability_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'subject_type_display', 'stream_display', 'availability_info'
        ]

    def get_availability_info(self, obj):
        """Get which class levels this subject is available for"""
        return {
            'creche': obj.available_for_creche,
            'nursery': obj.available_for_nursery,
            'primary': obj.available_for_primary,
            'jss': obj.available_for_jss,
            'sss': obj.available_for_sss,
        }


class SubjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for subject lists"""
    
    subject_type_display = serializers.CharField(source='get_subject_type_display', read_only=True)
    stream_display = serializers.CharField(source='get_stream_display', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'short_name', 'subject_type', 
                 'subject_type_display', 'stream', 'stream_display', 
                 'is_compulsory', 'pass_mark', 'is_active']


# ============================================
# CLASS SERIALIZERS
# ============================================

class ClassSerializer(serializers.ModelSerializer):
    """Serializer for Class model"""

    session_info = serializers.SerializerMethodField(read_only=True)
    term_info = serializers.SerializerMethodField(read_only=True)
    class_level_info = serializers.SerializerMethodField(read_only=True)
    class_teacher_info = serializers.SerializerMethodField(read_only=True)
    stream_display = serializers.CharField(source='get_stream_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_subjects = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Class
        fields = '__all__'
        read_only_fields = [
            'id', 'code', 'slug', 'created_at', 'updated_at',
            'current_enrollment', 'stream_display', 'status_display',
            'assigned_subjects'
        ]

    def get_session_info(self, obj):
        if obj.session:
            return {
                'id': obj.session.id,
                'name': obj.session.name,
                'start_date': obj.session.start_date,
                'end_date': obj.session.end_date,
            }
        return None

    def get_term_info(self, obj):
        if obj.term:
            return {
                'id': obj.term.id,
                'name': obj.term.name,
                'term': obj.term.term,
                'term_display': obj.term.get_term_display(),
                'start_date': obj.term.start_date,
                'end_date': obj.term.end_date,
            }
        return None

    def get_class_level_info(self, obj):
        if obj.class_level:
            program_info = None
            if obj.class_level.program:
                program_info = {
                    'id': obj.class_level.program.id,
                    'name': obj.class_level.program.name,
                    'code': obj.class_level.program.code,
                }
            
            return {
                'id': obj.class_level.id,
                'name': obj.class_level.name,
                'code': obj.class_level.code,
                'level': obj.class_level.level,
                'program': program_info
            }
        return None

    def get_class_teacher_info(self, obj):
        if obj.class_teacher:
            return {
                'id': obj.class_teacher.id,
                'name': obj.class_teacher.get_full_name(),
                'email': obj.class_teacher.email,
            }
        return None

    def get_assigned_subjects(self, obj):
        """Get subjects assigned to this class"""
        try:
            subjects = obj.get_assigned_subjects()
            return SubjectListSerializer(subjects, many=True).data
        except:
            return []

    def validate(self, data):
        """Validate class data"""
        # Ensure term belongs to session
        if data.get('term') and data.get('session'):
            if data['term'].session != data['session']:
                raise serializers.ValidationError({
                    'term': 'Selected term does not belong to the selected session'
                })

        return data


class ClassListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for class lists"""
    
    session_name = serializers.CharField(source='session.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    term_display = serializers.CharField(source='term.get_term_display', read_only=True)
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    class_teacher_name = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stream_display = serializers.CharField(source='get_stream_display', read_only=True)
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'code', 'session', 'session_name', 'term', 'term_name', 'term_display',
            'class_level', 'class_level_name', 'stream', 'stream_display',
            'class_teacher_name', 'current_enrollment', 'max_capacity', 
            'status', 'status_display', 'is_active'
        ]
    
    def get_class_teacher_name(self, obj):
        return obj.class_teacher.get_full_name() if obj.class_teacher else 'Not assigned'


# ============================================
# CLASS SUBJECT ASSIGNMENT SERIALIZERS
# ============================================

class ClassSubjectSerializer(serializers.ModelSerializer):
    """Serializer for ClassSubject model"""

    class_obj_info = serializers.SerializerMethodField(read_only=True)
    subject_info = serializers.SerializerMethodField(read_only=True)
    teacher_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ClassSubject
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_class_obj_info(self, obj):
        if obj.class_obj:
            return {
                'id': obj.class_obj.id,
                'name': obj.class_obj.name,
                'code': obj.class_obj.code,
            }
        return None

    def get_subject_info(self, obj):
        if obj.subject:
            return {
                'id': obj.subject.id,
                'name': obj.subject.name,
                'code': obj.subject.code,
                'subject_type': obj.subject.subject_type,
                'pass_mark': obj.subject.pass_mark,
            }
        return None

    def get_teacher_info(self, obj):
        if obj.teacher:
            return {
                'id': obj.teacher.id,
                'name': obj.teacher.get_full_name(),
                'email': obj.teacher.email,
            }
        return None


class ClassSubjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for class subject lists"""
    
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    teacher_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ClassSubject
        fields = [
            'id', 'class_obj', 'class_name', 'subject', 'subject_name', 'subject_code',
            'teacher', 'teacher_name', 'is_active', 'is_compulsory'
        ]
    
    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() if obj.teacher else 'Not assigned'


# ============================================
# DASHBOARD AND SPECIAL SERIALIZERS
# ============================================

class ClassDashboardSerializer(serializers.Serializer):
    """Serializer for class dashboard data"""

    class_info = ClassSerializer(read_only=True)
    subjects = serializers.SerializerMethodField(read_only=True)
    enrolled_students_count = serializers.IntegerField(read_only=True)
    statistics = serializers.DictField(read_only=True)

    def get_subjects(self, obj):
        """Get subjects offered in this class"""
        try:
            class_subjects = obj['class_info'].class_subjects.filter(is_active=True)
            return ClassSubjectListSerializer(class_subjects, many=True).data
        except:
            return []


class TeacherAssignmentSerializer(serializers.Serializer):
    """Serializer for teacher's class and subject assignments"""

    teacher_info = serializers.SerializerMethodField(read_only=True)
    class_teacher_classes = ClassListSerializer(many=True, read_only=True)
    teaching_assignments = ClassSubjectListSerializer(many=True, read_only=True)
    statistics = serializers.DictField(read_only=True)

    def get_teacher_info(self, obj):
        teacher = obj.get('teacher')
        if teacher:
            return {
                'id': teacher.id,
                'name': teacher.get_full_name(),
                'email': teacher.email,
            }
        return None


class BulkClassSubjectAssignmentSerializer(serializers.Serializer):
    """Serializer for bulk class-subject assignments"""

    assignments = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of assignment objects"
    )

    def validate_assignments(self, value):
        """Validate assignment list"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Assignments must be a list")

        for i, assignment in enumerate(value):
            if not isinstance(assignment, dict):
                raise serializers.ValidationError(f"Assignment at index {i} must be a dictionary")

            required_fields = ['class_id', 'subject_id']
            for field in required_fields:
                if field not in assignment:
                    raise serializers.ValidationError(f"Assignment at index {i} missing required field: {field}")

        return value


class AcademicDashboardSerializer(serializers.Serializer):
    """Serializer for academic dashboard data"""

    current_session = AcademicSessionListSerializer(read_only=True)
    current_term = AcademicTermListSerializer(read_only=True)
    statistics = serializers.DictField(read_only=True)
    recent_classes = ClassListSerializer(many=True, read_only=True)


class ClassStatisticsSerializer(serializers.Serializer):
    """Serializer for class statistics"""

    class_level_statistics = serializers.ListField(read_only=True)
    program_statistics = serializers.ListField(read_only=True)