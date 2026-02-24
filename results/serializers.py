"""
Serializers for Results App - UPDATED FOR class_level
Handles serialization for student results, subject scores, psychomotor skills, etc.
"""

from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import json

from .models import (
    StudentResult, SubjectScore, PsychomotorSkills, 
    AffectiveDomains, ResultPublishing
)

# Import models for related fields
from students.models import Student
from academic.models import AcademicSession, AcademicTerm, ClassLevel, Subject
from users.models import User


# ============================================
# SIMPLE SERIALIZERS FOR RELATED MODELS
# ============================================

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple serializer for User model"""
    
    full_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'registration_number', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()


# class SimpleStudentSerializer(serializers.ModelSerializer):
#     """Simple serializer for Student model"""
    
#     full_name = serializers.SerializerMethodField(read_only=True)
    
#     class Meta:
#         model = Student
#         fields = ['id', 'admission_number', 'user_id', 'full_name', 'class_level']
#         read_only_fields = fields
    
#     def get_full_name(self, obj):
#         return obj.user.get_full_name() if obj.user else ''

class SimpleStudentSerializer(serializers.ModelSerializer):
    """Simple serializer for Student model"""
    
    full_name = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    profile_picture = serializers.SerializerMethodField(read_only=True)
    student_image_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'user_id', 'full_name', 
            'first_name', 'last_name', 'class_level',
            'profile_picture', 'student_image_url', 'student_image'
        ]
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else ''
    
    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else ''
    
    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else ''
    
    def get_profile_picture(self, obj):
        if obj.user and obj.user.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile_picture.url)
        return None
    
    def get_student_image_url(self, obj):
        if hasattr(obj, 'student_image') and obj.student_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.student_image.url)
        return None

class SimpleAcademicSessionSerializer(serializers.ModelSerializer):
    """Simple serializer for AcademicSession model"""
    
    class Meta:
        model = AcademicSession
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current']
        read_only_fields = fields


class SimpleAcademicTermSerializer(serializers.ModelSerializer):
    """Simple serializer for AcademicTerm model"""
    
    term_display = serializers.CharField(source='get_term_display', read_only=True)
    
    class Meta:
        model = AcademicTerm
        fields = ['id', 'name', 'term', 'term_display', 'start_date', 'end_date', 'is_current']
        read_only_fields = fields


class SimpleClassLevelSerializer(serializers.ModelSerializer):
    """Simple serializer for ClassLevel model"""
    
    class Meta:
        model = ClassLevel
        fields = ['id', 'name', 'code', 'level', 'order']
        read_only_fields = fields


class SimpleSubjectSerializer(serializers.ModelSerializer):
    """Simple serializer for Subject model"""
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'short_name', 'subject_type', 'pass_mark']
        read_only_fields = fields


# ============================================
# SUBJECT SCORE SERIALIZERS
# ============================================

class SubjectScoreSerializer(serializers.ModelSerializer):
    """Serializer for individual subject scores"""
    
    subject = SimpleSubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source='subject',
        write_only=True,
        help_text="ID of the subject"
    )
    
    # Read-only calculated fields
    total_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    grade = serializers.CharField(max_length=2, read_only=True)
    aggregated_score = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    average_score = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = SubjectScore
        fields = [
            'id', 'result_id', 'subject', 'subject_id', 
            'ca_obtainable', 'exam_obtainable', 'total_obtainable',
            'ca_score', 'exam_score', 'total_score',
            'first_term_score', 'second_term_score', 'third_term_score',
            'aggregated_score', 'average_score', 'grade',
            'observation_conduct', 'subject_remark', 'position_in_subject', 
            'teacher_comment', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'result_id', 'total_score', 'grade', 
            'aggregated_score', 'average_score', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Validate subject score data"""
        # Validate scores don't exceed obtainable marks
        if 'ca_score' in data and 'ca_obtainable' in data:
            if data['ca_score'] > data['ca_obtainable']:
                raise serializers.ValidationError({
                    'ca_score': f"CA score cannot exceed {data['ca_obtainable']}"
                })
        
        if 'exam_score' in data and 'exam_obtainable' in data:
            if data['exam_score'] > data['exam_obtainable']:
                raise serializers.ValidationError({
                    'exam_score': f"Exam score cannot exceed {data['exam_obtainable']}"
                })
        
        return data
    
    def create(self, validated_data):
        """Create subject score and calculate totals"""
        # Calculate total score
        ca_score = validated_data.get('ca_score', 0)
        exam_score = validated_data.get('exam_score', 0)
        validated_data['total_score'] = ca_score + exam_score
        
        # Create the object
        instance = super().create(validated_data)
        
        # Calculate grade and term scores
        instance.calculate_total_and_grade()
        instance.save()
        
        # Update parent result
        if instance.result:
            instance.result.calculate_totals()
            instance.result.save()
        
        return instance
    
    def update(self, instance, validated_data):
        """Update subject score and recalculate"""
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Calculate total score
        instance.total_score = instance.ca_score + instance.exam_score
        
        # Calculate grade and term scores
        instance.calculate_total_and_grade()
        instance.save()
        
        # Update parent result
        if instance.result:
            instance.result.calculate_totals()
            instance.result.save()
        
        return instance


# ============================================
# PSYCHOMOTOR SKILLS SERIALIZER
# ============================================

class PsychomotorSkillsSerializer(serializers.ModelSerializer):
    """Serializer for psychomotor skills assessment"""
    
    result_id = serializers.IntegerField(source='result.id', read_only=True)
    overall_psychomotor_rating = serializers.DecimalField(
        max_digits=4, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = PsychomotorSkills
        fields = [
            'id', 'result_id', 'handwriting', 'verbal_fluency', 
            'drawing_and_painting', 'tools_handling', 'sports',
            'musical_skills', 'dancing', 'craft_work',
            'overall_psychomotor_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'result_id', 'overall_psychomotor_rating', 
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Create psychomotor skills and calculate rating"""
        instance = super().create(validated_data)
        instance.calculate_overall_rating()
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        """Update psychomotor skills and recalculate rating"""
        instance = super().update(instance, validated_data)
        instance.calculate_overall_rating()
        instance.save()
        return instance


# ============================================
# AFFECTIVE DOMAINS SERIALIZER
# ============================================

class AffectiveDomainsSerializer(serializers.ModelSerializer):
    """Serializer for affective domains assessment"""
    
    result_id = serializers.IntegerField(source='result.id', read_only=True)
    overall_affective_rating = serializers.DecimalField(
        max_digits=4, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = AffectiveDomains
        fields = [
            'id', 'result_id', 'punctuality', 'neatness', 'politeness', 
            'honesty', 'cooperation_with_others', 'leadership', 'altruism',
            'emotional_stability', 'health', 'attitude', 'attentiveness',
            'perseverance', 'communication_skill', 'overall_affective_rating',
            'behavioral_comment', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'result_id', 'overall_affective_rating', 
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Create affective domains and calculate rating"""
        instance = super().create(validated_data)
        instance.calculate_overall_rating()
        instance.save()
        return instance
    
    def update(self, instance, validated_data):
        """Update affective domains and recalculate rating"""
        instance = super().update(instance, validated_data)
        instance.calculate_overall_rating()
        instance.save()
        return instance


# ============================================
# STUDENT RESULT SERIALIZER
# ============================================

class StudentResultSerializer(serializers.ModelSerializer):
    """Main serializer for student results"""
    
    # Basic information with related objects
    student = SimpleStudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        source='student',
        write_only=True,
        help_text="ID of the student"
    )
    
    session = SimpleAcademicSessionSerializer(read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicSession.objects.all(),
        source='session',
        write_only=True,
        help_text="ID of the academic session"
    )
    
    term = SimpleAcademicTermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        source='term',
        write_only=True,
        help_text="ID of the academic term"
    )
    
    class_level = SimpleClassLevelSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        source='class_level',
        write_only=True,
        help_text="ID of the class level"
    )
    
    # User references
    class_teacher = SimpleUserSerializer(read_only=True)
    headmaster = SimpleUserSerializer(read_only=True)
    created_by = SimpleUserSerializer(read_only=True)
    
    # Nested serializers
    subject_scores = SubjectScoreSerializer(many=True, read_only=True)
    psychomotor_skills = PsychomotorSkillsSerializer(read_only=True)
    affective_domains = AffectiveDomainsSerializer(read_only=True)
    
    # Calculated fields
    attendance_percentage = serializers.SerializerMethodField(read_only=True)
    is_promotion_recommended = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = StudentResult
        fields = [
            # Basic information
            'id', 'student', 'student_id', 'session', 'session_id',
            'term', 'term_id', 'class_level', 'class_level_id',
            
            # Attendance
            'frequency_of_school_opened', 'no_of_times_present',
            'no_of_times_absent', 'attendance_percentage',
            
            # Demographic
            'weight_beginning_of_term', 'weight_end_of_term',
            'height_beginning_of_term', 'height_end_of_term',
            
            # Performance (auto-calculated)
            'total_ca_score', 'total_exam_score', 'overall_total_score',
            'total_obtainable', 'percentage', 'average_score',
            
            # Position and grading
            'position_in_class', 'number_of_pupils_in_class',
            'overall_grade', 'overall_remark',
            
            # Comments
            'class_teacher_comment', 'headmaster_comment',
            
            # Next term info
            'next_term_begins_on', 'next_term_fees',
            
            # Status
            'is_published', 'is_promoted', 'is_promotion_recommended',
            
            # Signatures
            'class_teacher', 'headmaster',
            'class_teacher_signature_date', 'headmaster_signature_date',
            
            # Nested data
            'subject_scores', 'psychomotor_skills', 'affective_domains',
            
            # Metadata
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            # Auto-calculated fields
            'total_ca_score', 'total_exam_score', 'overall_total_score',
            'total_obtainable', 'percentage', 'average_score', 
            'overall_grade', 'overall_remark', 'position_in_class', 
            'number_of_pupils_in_class',
            
            # Metadata
            'created_by', 'created_at', 'updated_at'
        ]
    
    def get_attendance_percentage(self, obj):
        """Calculate attendance percentage"""
        if obj.frequency_of_school_opened > 0:
            percentage = (obj.no_of_times_present / obj.frequency_of_school_opened) * 100
            return round(percentage, 2)
        return 0.00
    
    def get_is_promotion_recommended(self, obj):
        """Determine if promotion is recommended based on performance"""
        if obj.percentage >= 50:
            return True
        
        # Check subject failures
        subject_scores = obj.subject_scores.all()
        if not subject_scores:
            return False
        
        fail_count = 0
        for score in subject_scores:
            if score.grade in ['D', 'E']:
                fail_count += 1
        
        # If more than 30% subjects failed, no promotion
        fail_percentage = (fail_count / subject_scores.count()) * 100
        return fail_percentage < 30
    
    def validate(self, data):
        """Validate result data"""
        # Check if student is in the class level
        student = data.get('student')
        class_level = data.get('class_level')
        
        if student and class_level:
            if hasattr(student, 'class_level'):
                if student.class_level != class_level:
                    raise serializers.ValidationError({
                        'student': f"Student is not in class level {class_level.name}"
                    })
        
        # Validate attendance
        freq = data.get('frequency_of_school_opened', 0)
        present = data.get('no_of_times_present', 0)
        absent = data.get('no_of_times_absent', 0)
        
        if present + absent > freq:
            raise serializers.ValidationError({
                'attendance': "Present + Absent cannot exceed frequency of school opened"
            })
        
        return data
    
    def create(self, validated_data):
        """Create a new student result"""
        # Set created_by user from request context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        # Create the result
        instance = super().create(validated_data)
        
        # Calculate totals and position
        instance.calculate_totals()
        
        # Save to trigger position calculation
        instance.save()
        
        return instance
    
    def update(self, instance, validated_data):
        """Update student result"""
        # Update fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Validate attendance
        instance.clean()
        
        # Save to trigger calculations
        instance.save()
        
        return instance


# ============================================
# RESULT PUBLISHING SERIALIZER
# ============================================

class ResultPublishingSerializer(serializers.ModelSerializer):
    """Serializer for result publishing"""
    
    session = SimpleAcademicSessionSerializer(read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicSession.objects.all(),
        source='session',
        write_only=True,
        help_text="ID of the academic session"
    )
    
    term = SimpleAcademicTermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        source='term',
        write_only=True,
        help_text="ID of the academic term"
    )
    
    class_level = SimpleClassLevelSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        source='class_level',
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID of the class level (optional - leave blank for all classes)"
    )
    
    published_by = SimpleUserSerializer(read_only=True)
    
    # Statistics
    total_students = serializers.SerializerMethodField(read_only=True)
    results_published = serializers.SerializerMethodField(read_only=True)
    results_total = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ResultPublishing
        fields = [
            'id', 'session', 'session_id', 'term', 'term_id',
            'class_level', 'class_level_id', 'is_published', 'published_date',
            'published_by', 'remarks', 
            'total_students', 'results_published', 'results_total',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'published_date', 'published_by', 
            'total_students', 'results_published', 'results_total',
            'created_at', 'updated_at'
        ]
    
    def get_total_students(self, obj):
        """Get total students in the class/session"""
        try:
            if obj.class_level:
                # Count students in this class level
                return Student.objects.filter(
                    class_level=obj.class_level,
                    is_active=True
                ).count()
            
            # For all classes, count all active students
            return Student.objects.filter(is_active=True).count()
        except:
            return 0
    
    def get_results_published(self, obj):
        """Get count of published results"""
        try:
            query = StudentResult.objects.filter(
                session=obj.session,
                term=obj.term,
                is_published=True
            )
            
            if obj.class_level:
                query = query.filter(class_level=obj.class_level)
            
            return query.count()
        except:
            return 0
    
    def get_results_total(self, obj):
        """Get total results for this session/term/class"""
        try:
            query = StudentResult.objects.filter(
                session=obj.session,
                term=obj.term
            )
            
            if obj.class_level:
                query = query.filter(class_level=obj.class_level)
            
            return query.count()
        except:
            return 0
    
    def validate(self, data):
        """Validate publishing data"""
        # Check for duplicate publishing entry
        session = data.get('session')
        term = data.get('term')
        class_level = data.get('class_level')
        
        query = ResultPublishing.objects.filter(
            session=session,
            term=term,
            class_level=class_level
        )
        
        # Exclude current instance if updating
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise serializers.ValidationError({
                'duplicate': "A publishing entry already exists for this session, term, and class level"
            })
        
        return data
    
    def create(self, validated_data):
        """Create result publishing entry"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['published_by'] = request.user
        
        return super().create(validated_data)


# ============================================
# BULK OPERATION SERIALIZERS
# ============================================

class BulkResultUploadSerializer(serializers.Serializer):
    """Serializer for bulk result upload via JSON"""
    
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicSession.objects.all(),
        help_text="ID of the academic session"
    )
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTerm.objects.all(),
        help_text="ID of the academic term"
    )
    class_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        help_text="ID of the class level"
    )
    results_data = serializers.JSONField(
        help_text="JSON array of result data"
    )
    
    def validate_results_data(self, value):
        """Validate the results JSON data"""
        if not isinstance(value, list):
            raise serializers.ValidationError("results_data must be a list")
        
        for i, result in enumerate(value):
            if not isinstance(result, dict):
                raise serializers.ValidationError(f"Item at index {i} must be a dictionary")
            
            # Check required fields
            required_fields = ['student_registration_number']
            for field in required_fields:
                if field not in result:
                    raise serializers.ValidationError(f"Item at index {i} missing required field: {field}")
            
            # Validate subjects if provided
            if 'subjects' in result and not isinstance(result['subjects'], list):
                raise serializers.ValidationError(f"Item at index {i}: 'subjects' must be a list")
        
        return value


class SubjectScoreBulkSerializer(serializers.Serializer):
    """Serializer for bulk subject score creation"""
    
    subject_code = serializers.CharField(
        max_length=20,
        help_text="Subject code (e.g., ENG101)"
    )
    ca_score = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        min_value=0, 
        max_value=40,
        help_text="CA score (0-40)"
    )
    exam_score = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        min_value=0, 
        max_value=60,
        help_text="Exam score (0-60)"
    )
    observation_conduct = serializers.CharField(
        max_length=2, 
        required=False, 
        allow_blank=True,
        help_text="Observation on conduct (A-E)"
    )
    subject_remark = serializers.CharField(
        max_length=20, 
        required=False, 
        allow_blank=True,
        help_text="Subject remark"
    )
    teacher_comment = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Teacher's comment"
    )


# ============================================
# LIGHTWEIGHT SERIALIZERS FOR LISTS
# ============================================

class StudentResultListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for student result lists"""
    
    student_name = serializers.SerializerMethodField(read_only=True)
    student_admission = serializers.SerializerMethodField(read_only=True)
    class_level_name = serializers.CharField(source='class_level.name', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    
    class Meta:
        model = StudentResult
        fields = [
            'id', 'student_id', 'student_name', 'student_admission',
            'session_id', 'session_name', 'term_id', 'term_name',
            'class_level_id', 'class_level_name', 'overall_total_score',
            'percentage', 'overall_grade', 'position_in_class',
            'is_published', 'is_promoted', 'created_at'
        ]
        read_only_fields = fields
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student and obj.student.user else ''
    
    def get_student_admission(self, obj):
        return obj.student.admission_number if obj.student else ''


class SubjectScoreListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for subject score lists"""
    
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    
    class Meta:
        model = SubjectScore
        fields = [
            'id', 'result_id', 'subject_id', 'subject_name', 'subject_code',
            'ca_score', 'exam_score', 'total_score', 'grade', 'teacher_comment'
        ]
        read_only_fields = fields


# ============================================
# STATISTICS SERIALIZERS
# ============================================

class ResultStatisticsSerializer(serializers.Serializer):
    """Serializer for result statistics"""
    
    total_results = serializers.IntegerField(read_only=True)
    published_results = serializers.IntegerField(read_only=True)
    publish_percentage = serializers.FloatField(read_only=True)
    
    average_percentage = serializers.FloatField(read_only=True)
    highest_percentage = serializers.FloatField(read_only=True)
    lowest_percentage = serializers.FloatField(read_only=True)
    
    grade_distribution = serializers.DictField(read_only=True)
    term_performance = serializers.ListField(read_only=True)
    class_performance = serializers.ListField(read_only=True)


class StudentPerformanceSerializer(serializers.Serializer):
    """Serializer for individual student performance"""
    
    student_info = serializers.DictField(read_only=True)
    term_results = serializers.ListField(read_only=True)
    subject_performance = serializers.ListField(read_only=True)
    attendance_trend = serializers.ListField(read_only=True)
    overall_statistics = serializers.DictField(read_only=True)


# ============================================
# REPORT CARD SERIALIZER
# ============================================

class ReportCardSerializer(serializers.ModelSerializer):
    """Serializer for generating report cards"""
    
    # Basic info
    student_name = serializers.SerializerMethodField(read_only=True)
    admission_number = serializers.SerializerMethodField(read_only=True)
    class_level_name = serializers.SerializerMethodField(read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    
    # Academic performance
    subject_scores = SubjectScoreListSerializer(many=True, read_only=True)
    
    # Behavioral assessments
    psychomotor_summary = serializers.SerializerMethodField(read_only=True)
    affective_summary = serializers.SerializerMethodField(read_only=True)
    
    # Statistics
    class_position = serializers.SerializerMethodField(read_only=True)
    attendance_summary = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = StudentResult
        fields = [
            # Header
            'id', 'student_name', 'admission_number', 
            'class_level_name', 'session_name', 'term_name',
            
            # Academic
            'subject_scores', 'overall_total_score', 'percentage',
            'overall_grade', 'overall_remark', 'class_position',
            
            # Behavioral
            'psychomotor_summary', 'affective_summary',
            
            # Attendance
            'attendance_summary',
            
            # Comments
            'class_teacher_comment', 'headmaster_comment',
            
            # Next term
            'next_term_begins_on', 'next_term_fees',
            
            # Status
            'is_promoted'
        ]
        read_only_fields = fields
    
    def get_student_name(self, obj):
        return obj.student.user.get_full_name() if obj.student and obj.student.user else ''
    
    def get_admission_number(self, obj):
        return obj.student.admission_number if obj.student else ''
    
    def get_class_level_name(self, obj):
        return obj.class_level.name if obj.class_level else ''
    
    def get_psychomotor_summary(self, obj):
        """Get psychomotor skills summary"""
        try:
            psychomotor = obj.psychomotor_skills
            if psychomotor:
                return {
                    'handwriting': psychomotor.handwriting,
                    'verbal_fluency': psychomotor.verbal_fluency,
                    'sports': psychomotor.sports,
                    'overall': psychomotor.overall_psychomotor_rating
                }
        except:
            pass
        return {}
    
    def get_affective_summary(self, obj):
        """Get affective domains summary"""
        try:
            affective = obj.affective_domains
            if affective:
                return {
                    'punctuality': affective.punctuality,
                    'neatness': affective.neatness,
                    'honesty': affective.honesty,
                    'attitude': affective.attitude,
                    'overall': affective.overall_affective_rating
                }
        except:
            pass
        return {}
    
    def get_class_position(self, obj):
        """Get class position in readable format"""
        if obj.position_in_class:
            suffix = 'th'
            if obj.position_in_class % 10 == 1 and obj.position_in_class != 11:
                suffix = 'st'
            elif obj.position_in_class % 10 == 2 and obj.position_in_class != 12:
                suffix = 'nd'
            elif obj.position_in_class % 10 == 3 and obj.position_in_class != 13:
                suffix = 'rd'
            return f"{obj.position_in_class}{suffix} out of {obj.number_of_pupils_in_class}"
        return "Not available"
    
    def get_attendance_summary(self, obj):
        """Get attendance summary"""
        if obj.frequency_of_school_opened > 0:
            percentage = (obj.no_of_times_present / obj.frequency_of_school_opened) * 100
            return {
                'total_days': obj.frequency_of_school_opened,
                'present': obj.no_of_times_present,
                'absent': obj.no_of_times_absent,
                'percentage': round(percentage, 2)
            }
        return {'total_days': 0, 'present': 0, 'absent': 0, 'percentage': 0}