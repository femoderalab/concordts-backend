# """
# Complete Result/Report Card Models for Nigerian Schools
# """
# from django.db import models
# from django.core.validators import MinValueValidator, MaxValueValidator
# from django.core.exceptions import ValidationError
# from django.utils import timezone
# from decimal import Decimal

# # Import related models directly
# from students.models import Student
# from academic.models import AcademicSession, AcademicTerm, ClassLevel, Subject
# from users.models import User


# class StudentResult(models.Model):
#     """
#     Main Result/Report Card Model
#     Complete term report for a student with all details from the image
#     """
    
#     # Basic Information
#     student = models.ForeignKey(
#         Student,
#         on_delete=models.CASCADE,
#         related_name='results',
#         help_text="Student record"
#     )
    
#     session = models.ForeignKey(
#         AcademicSession,
#         on_delete=models.CASCADE,
#         related_name='student_results'
#     )
    
#     term = models.ForeignKey(
#         AcademicTerm,
#         on_delete=models.CASCADE,
#         related_name='student_results'
#     )
    
#     class_level = models.ForeignKey(
#         ClassLevel,
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         related_name='student_results',
#         help_text="Class level of the student"
#     )
    
#     # ATTENDANCE SECTION
#     frequency_of_school_opened = models.IntegerField(
#         default=0,
#         validators=[MinValueValidator(0)],
#         help_text="Total number of times school opened this term"
#     )
    
#     no_of_times_present = models.IntegerField(
#         default=0,
#         validators=[MinValueValidator(0)],
#         help_text="Number of times student was present"
#     )
    
#     no_of_times_absent = models.IntegerField(
#         default=0,
#         validators=[MinValueValidator(0)],
#         help_text="Number of times student was absent"
#     )
    
#     # DEMOGRAPHIC FEATURES SECTION
#     weight_beginning_of_term = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Weight at beginning of term (kg)"
#     )
    
#     weight_end_of_term = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Weight at end of term (kg)"
#     )
    
#     height_beginning_of_term = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Height at beginning of term (cm)"
#     )
    
#     height_end_of_term = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Height at end of term (cm)"
#     )
    
#     # OVERALL PERFORMANCE (Auto-calculated from subject scores)
#     total_ca_score = models.DecimalField(
#         max_digits=7,
#         decimal_places=2,
#         default=0,
#         help_text="Total CA scores across all subjects"
#     )
    
#     total_exam_score = models.DecimalField(
#         max_digits=7,
#         decimal_places=2,
#         default=0,
#         help_text="Total exam scores across all subjects"
#     )
    
#     overall_total_score = models.DecimalField(
#         max_digits=7,
#         decimal_places=2,
#         default=0,
#         help_text="Grand total of all subjects"
#     )
    
#     total_obtainable = models.DecimalField(
#         max_digits=7,
#         decimal_places=2,
#         default=0,
#         help_text="Total marks obtainable"
#     )
    
#     percentage = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=0,
#         help_text="Overall percentage (%)"
#     )
    
#     average_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=0,
#         help_text="Average score"
#     )
    
#     # POSITION IN CLASS
#     position_in_class = models.IntegerField(
#         null=True,
#         blank=True,
#         help_text="Student's position in class (1st, 2nd, 3rd...)"
#     )
    
#     number_of_pupils_in_class = models.IntegerField(
#         default=0,
#         help_text="Total number of students in class"
#     )
    
#     # OVERALL GRADING (Nigerian Standard)
#     GRADE_CHOICES = [
#         ('A', 'A - Excellent (80-100)'),
#         ('B', 'B - Good (60-79)'),
#         ('C', 'C - Average (50-59)'),
#         ('D', 'D - Below Average (40-49)'),
#         ('E', 'E - Poor (Below 40)'),
#     ]
    
#     overall_grade = models.CharField(
#         max_length=2,
#         choices=GRADE_CHOICES,
#         blank=True,
#         help_text="Overall grade based on percentage"
#     )
    
#     REMARK_CHOICES = [
#         ('excellent', 'Excellent'),
#         ('very_good', 'Very Good'),
#         ('good', 'Good'),
#         ('average', 'Average'),
#         ('below_average', 'Below Average'),
#         ('poor', 'Poor'),
#     ]
    
#     overall_remark = models.CharField(
#         max_length=20,
#         choices=REMARK_CHOICES,
#         blank=True,
#         help_text="Overall remark on performance"
#     )
    
#     # COMMENTS SECTION
#     class_teacher_comment = models.TextField(
#         blank=True,
#         help_text="Class teacher's comment"
#     )
    
#     headmaster_comment = models.TextField(
#         blank=True,
#         help_text="Headmaster/Headmistress comment"
#     )
    
#     # NEXT TERM INFORMATION
#     next_term_begins_on = models.DateField(
#         null=True,
#         blank=True,
#         help_text="Date next term begins"
#     )
    
#     next_term_fees = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="School fees for next term"
#     )
    
#     # PUBLICATION STATUS
#     is_published = models.BooleanField(
#         default=False,
#         help_text="Is result published to student/parent?"
#     )
    
#     is_promoted = models.BooleanField(
#         default=False,
#         help_text="Is student promoted to next class?"
#     )
    
#     # SIGNATURES AND APPROVALS
#     class_teacher = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='results_as_class_teacher'
#     )
    
#     headmaster = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='results_as_headmaster'
#     )
    
#     class_teacher_signature_date = models.DateField(null=True, blank=True)
#     headmaster_signature_date = models.DateField(null=True, blank=True)
    
#     # METADATA
#     created_by = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='created_results'
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-session__start_date', '-term__term', 'class_level', 'student']
#         unique_together = ['student', 'session', 'term']
#         verbose_name = 'Student Result'
#         verbose_name_plural = 'Student Results'
#         indexes = [
#             models.Index(fields=['student', 'session', 'term']),
#             models.Index(fields=['class_level', 'session', 'term']),
#             models.Index(fields=['is_published']),
#         ]

#     def __str__(self):
#         return f"{self.student.user.get_full_name()} - {self.class_level.name} - {self.term}"

#     def clean(self):
#         """Validate attendance numbers"""
#         total_days = self.no_of_times_present + self.no_of_times_absent
        
#         if self.frequency_of_school_opened > 0 and total_days != self.frequency_of_school_opened:
#             self.no_of_times_absent = self.frequency_of_school_opened - self.no_of_times_present
    
#     def calculate_totals(self):
#         """
#         Auto-calculate total scores, percentage, average, and grade
#         SAFE version: prevents PK-related admin crash
#         """

#         # If object is not saved yet, skip calculation
#         if not self.pk:
#             self.total_ca_score = 0
#             self.total_exam_score = 0
#             self.overall_total_score = 0
#             self.total_obtainable = 0
#             self.percentage = 0
#             self.average_score = 0
#             self.overall_grade = ''
#             self.overall_remark = ''
#             return

#         subject_scores = self.subject_scores.all()

#         # If no subject scores exist
#         if not subject_scores.exists():
#             self.total_ca_score = 0
#             self.total_exam_score = 0
#             self.overall_total_score = 0
#             self.total_obtainable = 0
#             self.percentage = 0
#             self.average_score = 0
#             self.overall_grade = ''
#             self.overall_remark = ''
#             return

#         # Calculate totals
#         total_ca = sum(score.ca_score or 0 for score in subject_scores)
#         total_exam = sum(score.exam_score or 0 for score in subject_scores)
#         total_score = sum(score.total_score or 0 for score in subject_scores)
#         total_obtainable = sum(score.total_obtainable or 0 for score in subject_scores)

#         self.total_ca_score = total_ca
#         self.total_exam_score = total_exam
#         self.overall_total_score = total_score
#         self.total_obtainable = total_obtainable

#         # Calculate percentage and average
#         if total_obtainable > 0:
#             self.percentage = round((total_score / total_obtainable) * 100, 2)
#             self.average_score = round(total_score / subject_scores.count(), 2)
#         else:
#             self.percentage = 0
#             self.average_score = 0

#         # Determine grade based on Nigerian standard
#         if self.percentage >= 80:
#             self.overall_grade = 'A'
#             self.overall_remark = 'excellent'
#         elif self.percentage >= 60:
#             self.overall_grade = 'B'
#             self.overall_remark = 'good'
#         elif self.percentage >= 50:
#             self.overall_grade = 'C'
#             self.overall_remark = 'average'
#         elif self.percentage >= 40:
#             self.overall_grade = 'D'
#             self.overall_remark = 'below_average'
#         else:
#             self.overall_grade = 'E'
#             self.overall_remark = 'poor'

#     def calculate_position(self):
#         """Calculate student's position in class"""
#         class_results = StudentResult.objects.filter(
#             class_level=self.class_level,
#             session=self.session,
#             term=self.term,
#             overall_total_score__gt=0
#         ).order_by('-overall_total_score', '-percentage')
        
#         # Update total number of students
#         self.number_of_pupils_in_class = class_results.count()
        
#         # Calculate position
#         for position, result in enumerate(class_results, start=1):
#             if result.id == self.id:
#                 self.position_in_class = position
#                 break

        
#     def save(self, *args, **kwargs):
#         self.clean()

#         # FIRST SAVE (create PK)
#         is_new = self.pk is None
#         super().save(*args, **kwargs)

#         # Now object has ID — safe to access relations
#         self.calculate_totals()
#         self.calculate_position()

#         # Update calculated fields only
#         super().save(update_fields=[
#             'total_ca_score',
#             'total_exam_score',
#             'overall_total_score',
#             'total_obtainable',
#             'percentage',
#             'average_score',
#             'overall_grade',
#             'overall_remark',
#             'position_in_class',
#             'number_of_pupils_in_class'
#         ])

# class SubjectScore(models.Model):
#     """
#     Individual Subject Scores
#     Matches the SUBJECTS table in the report card image
#     """
    
#     result = models.ForeignKey(
#         StudentResult,
#         on_delete=models.CASCADE,
#         related_name='subject_scores'
#     )
    
#     subject = models.ForeignKey(
#         Subject,
#         on_delete=models.CASCADE,
#         related_name='subject_scores'
#     )
    
#     # MARK OBTAINABLE (40 CA + 60 EXAM = 100 TOTAL)
#     ca_obtainable = models.IntegerField(
#         default=40,
#         help_text="CA marks obtainable (usually 40)"
#     )
    
#     exam_obtainable = models.IntegerField(
#         default=60,
#         help_text="Exam marks obtainable (usually 60)"
#     )
    
#     total_obtainable = models.IntegerField(
#         default=100,
#         help_text="Total marks obtainable"
#     )
    
#     # SCORES
#     ca_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=0,
#         validators=[MinValueValidator(0), MaxValueValidator(40)],
#         help_text="CA Score (out of 40)"
#     )
    
#     exam_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=0,
#         validators=[MinValueValidator(0), MaxValueValidator(60)],
#         help_text="Exam Score (out of 60)"
#     )
    
#     total_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=0,
#         help_text="Total Score (CA + Exam) out of 100"
#     )
    
#     # TERM SCORES FOR TRACKING
#     first_term_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="First term total score"
#     )
    
#     second_term_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Second term total score"
#     )
    
#     third_term_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         null=True,
#         blank=True,
#         help_text="Third term total score"
#     )
    
#     # AGGREGATED SCORE
#     aggregated_score = models.DecimalField(
#         max_digits=6,
#         decimal_places=2,
#         default=0,
#         help_text="Sum of all term scores"
#     )
    
#     # AVERAGE
#     average_score = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=0,
#         help_text="Average of all terms"
#     )
    
#     # GRADING (Nigerian Standard)
#     GRADE_CHOICES = [
#         ('A', 'A - Excellent (80-100)'),
#         ('B', 'B - Good (60-79)'),
#         ('C', 'C - Average (50-59)'),
#         ('D', 'D - Below Average (40-49)'),
#         ('E', 'E - Poor (Below 40)'),
#     ]
    
#     grade = models.CharField(
#         max_length=2,
#         choices=GRADE_CHOICES,
#         blank=True,
#         help_text="Subject grade"
#     )
    
#     # OBSERVATION ON CONDUCT
#     OBSERVATION_CHOICES = [
#         ('A', 'A'),
#         ('B', 'B'),
#         ('C', 'C'),
#         ('D', 'D'),
#         ('E', 'E'),
#     ]
    
#     observation_conduct = models.CharField(
#         max_length=2,
#         choices=OBSERVATION_CHOICES,
#         blank=True,
#         help_text="Teacher's observation on student conduct in this subject"
#     )
    
#     # Subject-specific remarks
#     SUBJECT_REMARK_CHOICES = [
#         ('honesty', 'Honesty'),
#         ('punctuality', 'Punctuality'),
#         ('attentiveness', 'Attentiveness'),
#         ('politeness', 'Politeness'),
#         ('neatness', 'Neatness'),
#     ]
    
#     subject_remark = models.CharField(
#         max_length=20,
#         choices=SUBJECT_REMARK_CHOICES,
#         blank=True,
#         help_text="Remark on student's attitude in this subject"
#     )
    
#     # Position in subject across class
#     position_in_subject = models.IntegerField(
#         null=True,
#         blank=True,
#         help_text="Student's position in this specific subject"
#     )
    
#     # Teacher's comment
#     teacher_comment = models.TextField(
#         blank=True,
#         help_text="Teacher's comment on performance in this subject"
#     )
    
#     # METADATA
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['subject__name']
#         unique_together = ['result', 'subject']
#         verbose_name = 'Subject Score'
#         verbose_name_plural = 'Subject Scores'
#         indexes = [
#             models.Index(fields=['result', 'subject']),
#         ]

#     def __str__(self):
#         return f"{self.result.student.user.get_full_name()} - {self.subject.name}: {self.total_score}"
    
#     def clean(self):
#         """Validate scores don't exceed obtainable marks"""
#         if self.ca_score > self.ca_obtainable:
#             raise ValidationError(f"CA score cannot exceed {self.ca_obtainable}")
        
#         if self.exam_score > self.exam_obtainable:
#             raise ValidationError(f"Exam score cannot exceed {self.exam_obtainable}")
    
#     def calculate_total_and_grade(self):
#         """Auto-calculate total score and assign grade"""
#         # Calculate total
#         self.total_score = self.ca_score + self.exam_score
        
#         # Assign grade based on Nigerian standard
#         if self.total_score >= 80:
#             self.grade = 'A'
#         elif self.total_score >= 60:
#             self.grade = 'B'
#         elif self.total_score >= 50:
#             self.grade = 'C'
#         elif self.total_score >= 40:
#             self.grade = 'D'
#         else:
#             self.grade = 'E'
        
#         # Update term-specific scores based on current term
#         current_term = self.result.term.term
        
#         if current_term == 'first':
#             self.first_term_score = self.total_score
#         elif current_term == 'second':
#             self.second_term_score = self.total_score
#         elif current_term == 'third':
#             self.third_term_score = self.total_score
        
#         # Calculate aggregated score and average
#         scores = [
#             self.first_term_score or 0,
#             self.second_term_score or 0,
#             self.third_term_score or 0
#         ]
        
#         valid_scores = [s for s in scores if s > 0]
#         self.aggregated_score = sum(scores)
        
#         if valid_scores:
#             self.average_score = round(sum(valid_scores) / len(valid_scores), 2)
#         else:
#             self.average_score = 0
    
#     def save(self, *args, **kwargs):
#         self.clean()
#         self.calculate_total_and_grade()
#         super().save(*args, **kwargs)
        
#         # Recalculate parent result totals
#         self.result.calculate_totals()
#         self.result.save()


# class PsychomotorSkills(models.Model):
#     """
#     PSYCHOMOTOR SKILLS ASSESSMENT
#     From the report card image (5-point rating scale)
#     """
    
#     result = models.OneToOneField(
#         StudentResult,
#         on_delete=models.CASCADE,
#         related_name='psychomotor_skills'
#     )
    
#     # Rating Scale
#     RATING_CHOICES = [
#         (5, '5 - Excellent'),
#         (4, '4 - Good'),
#         (3, '3 - Fair'),
#         (2, '2 - Poor'),
#         (1, '1 - Very Poor'),
#     ]
    
#     # Skills assessment
#     handwriting = models.IntegerField(
#         choices=RATING_CHOICES,
#         default=3,
#         help_text="Handwriting quality"
#     )
    
#     verbal_fluency = models.IntegerField(
#         choices=RATING_CHOICES,
#         default=3,
#         help_text="Verbal fluency and communication"
#     )
    
#     drawing_and_painting = models.IntegerField(
#         choices=RATING_CHOICES,
#         default=3,
#         help_text="Drawing and painting skills"
#     )
    
#     tools_handling = models.IntegerField(
#         choices=RATING_CHOICES,
#         default=3,
#         help_text="Handling of tools and equipment"
#     )
    
#     sports = models.IntegerField(
#         choices=RATING_CHOICES,
#         default=3,
#         help_text="Sports and physical activities"
#     )
    
#     # Additional skills
#     musical_skills = models.IntegerField(
#         choices=RATING_CHOICES,
#         null=True,
#         blank=True,
#         help_text="Musical skills and performance"
#     )
    
#     dancing = models.IntegerField(
#         choices=RATING_CHOICES,
#         null=True,
#         blank=True,
#         help_text="Dancing and rhythmic movement"
#     )
    
#     craft_work = models.IntegerField(
#         choices=RATING_CHOICES,
#         null=True,
#         blank=True,
#         help_text="Craft and handiwork"
#     )
    
#     # Overall psychomotor rating
#     overall_psychomotor_rating = models.DecimalField(
#         max_digits=4,
#         decimal_places=2,
#         default=0,
#         help_text="Average psychomotor rating"
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = 'Psychomotor Skills'
#         verbose_name_plural = 'Psychomotor Skills'
    
#     def __str__(self):
#         return f"Psychomotor Skills - {self.result.student.user.get_full_name()}"
    
#     def calculate_overall_rating(self):
#         """Calculate average psychomotor rating"""
#         ratings = [
#             self.handwriting,
#             self.verbal_fluency,
#             self.drawing_and_painting,
#             self.tools_handling,
#             self.sports,
#         ]
        
#         # Add optional ratings if they exist
#         if self.musical_skills:
#             ratings.append(self.musical_skills)
#         if self.dancing:
#             ratings.append(self.dancing)
#         if self.craft_work:
#             ratings.append(self.craft_work)
        
#         if ratings:
#             self.overall_psychomotor_rating = round(sum(ratings) / len(ratings), 2)
    
#     def save(self, *args, **kwargs):
#         self.calculate_overall_rating()
#         super().save(*args, **kwargs)


# class AffectiveDomains(models.Model):
#     """
#     AFFECTIVE DOMAINS / BEHAVIORAL ASSESSMENT
#     From the report card image with checkboxes (5-point rating)
#     """
    
#     result = models.OneToOneField(
#         StudentResult,
#         on_delete=models.CASCADE,
#         related_name='affective_domains'
#     )
    
#     # Rating Scale
#     RATING_CHOICES = [
#         (5, '5 - Excellent'),
#         (4, '4 - Good'),
#         (3, '3 - Fair'),
#         (2, '2 - Poor'),
#         (1, '1 - Very Poor'),
#     ]
    
#     # Behavioral traits assessment
#     punctuality = models.IntegerField(choices=RATING_CHOICES, default=3)
#     neatness = models.IntegerField(choices=RATING_CHOICES, default=3)
#     politeness = models.IntegerField(choices=RATING_CHOICES, default=3)
#     honesty = models.IntegerField(choices=RATING_CHOICES, default=3)
#     cooperation_with_others = models.IntegerField(choices=RATING_CHOICES, default=3)
#     leadership = models.IntegerField(choices=RATING_CHOICES, default=3)
#     altruism = models.IntegerField(choices=RATING_CHOICES, default=3)
#     emotional_stability = models.IntegerField(choices=RATING_CHOICES, default=3)
#     health = models.IntegerField(choices=RATING_CHOICES, default=3)
#     attitude = models.IntegerField(choices=RATING_CHOICES, default=3)
#     attentiveness = models.IntegerField(choices=RATING_CHOICES, default=3)
#     perseverance = models.IntegerField(choices=RATING_CHOICES, default=3)
#     communication_skill = models.IntegerField(choices=RATING_CHOICES, default=3)
    
#     # Overall affective rating
#     overall_affective_rating = models.DecimalField(
#         max_digits=4,
#         decimal_places=2,
#         default=0,
#         help_text="Average affective rating"
#     )
    
#     # General comment on behavior
#     behavioral_comment = models.TextField(
#         blank=True,
#         help_text="General comment on student's behavior"
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = 'Affective Domain'
#         verbose_name_plural = 'Affective Domains'
    
#     def __str__(self):
#         return f"Affective Domains - {self.result.student.user.get_full_name()}"
    
#     def calculate_overall_rating(self):
#         """Calculate average affective rating"""
#         ratings = [
#             self.punctuality,
#             self.neatness,
#             self.politeness,
#             self.honesty,
#             self.cooperation_with_others,
#             self.leadership,
#             self.altruism,
#             self.emotional_stability,
#             self.health,
#             self.attitude,
#             self.attentiveness,
#             self.perseverance,
#             self.communication_skill,
#         ]
        
#         if ratings:
#             self.overall_affective_rating = round(sum(ratings) / len(ratings), 2)
    
#     def save(self, *args, **kwargs):
#         self.calculate_overall_rating()
#         super().save(*args, **kwargs)


# class ResultPublishing(models.Model):
#     """
#     Result Publishing Control
#     Manage when results are published to students/parents
#     """
    
#     session = models.ForeignKey(
#         AcademicSession,
#         on_delete=models.CASCADE,
#         related_name='result_publishing'
#     )
    
#     term = models.ForeignKey(
#         AcademicTerm,
#         on_delete=models.CASCADE,
#         related_name='result_publishing'
#     )
    
#     # class_level = models.ForeignKey(
#     #     'academic.ClassLevel',
#     #     on_delete=models.CASCADE,
#     #     null=True,
#     #     blank=True,
#     #     related_name='result_publishing'
#     # )
    
#     class_level = models.ForeignKey(
#         'academic.ClassLevel',
#         on_delete=models.CASCADE,
#         related_name='published_results',
#         null=True,  # Make it nullable temporarily
#         blank=True
#     )
        
#     is_published = models.BooleanField(
#         default=False,
#         help_text="Are results published to students/parents?"
#     )
    
#     published_date = models.DateTimeField(
#         null=True,
#         blank=True,
#         help_text="Date and time results were published"
#     )
    
#     published_by = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         help_text="User who published the results"
#     )
    
#     remarks = models.TextField(
#         blank=True,
#         help_text="Publishing remarks or special instructions"
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ['session', 'term', 'class_level']
#         verbose_name = 'Result Publishing'
#         verbose_name_plural = 'Result Publishing'
#         indexes = [
#             models.Index(fields=['session', 'term', 'class_level']),
#             models.Index(fields=['is_published']),
#         ]

#     def __str__(self):
#         class_name = self.class_level.name if self.class_level else "All Classes"
#         return f"{class_name} - {self.term} - {'Published' if self.is_published else 'Not Published'}"
    
#     def publish_results(self, user):
#         """Publish results for this session, term, and class"""
#         self.is_published = True
#         self.published_date = timezone.now()
#         self.published_by = user
        
#         # Update all student results to published
#         results = StudentResult.objects.filter(
#             session=self.session,
#             term=self.term
#         )
        
#         if self.class_level:
#             results = results.filter(class_level=self.class_level)
        
#         results.update(is_published=True)
#         self.save()
    
#     def unpublish_results(self):
#         """Unpublish results for this session, term, and class"""
#         self.is_published = False
#         self.published_date = None
#         self.published_by = None
        
#         # Update all student results to not published
#         results = StudentResult.objects.filter(
#             session=self.session,
#             term=self.term
#         )
        
#         if self.class_level:
#             results = results.filter(class_level=self.class_level)
        
#         results.update(is_published=False)
#         self.save()
        
        

"""
Complete Result/Report Card Models for Nigerian Schools
"""
from django.db import models, connection
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import logging

# Set up logger
logger = logging.getLogger(__name__)

# Import related models directly
from students.models import Student
from academic.models import AcademicSession, AcademicTerm, ClassLevel, Subject
from users.models import User


class StudentResult(models.Model):
    """
    Main Result/Report Card Model
    Complete term report for a student with all details from the image
    """
    
    # Basic Information
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='results',
        help_text="Student record"
    )
    
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='student_results'
    )
    
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        related_name='student_results'
    )
    
    class_level = models.ForeignKey(
        ClassLevel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_results',
        help_text="Class level of the student"
    )
    
    # ATTENDANCE SECTION
    frequency_of_school_opened = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total number of times school opened this term"
    )
    
    no_of_times_present = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of times student was present"
    )
    
    no_of_times_absent = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of times student was absent"
    )
    
    # DEMOGRAPHIC FEATURES SECTION
    weight_beginning_of_term = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight at beginning of term (kg)"
    )
    
    weight_end_of_term = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight at end of term (kg)"
    )
    
    height_beginning_of_term = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height at beginning of term (cm)"
    )
    
    height_end_of_term = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height at end of term (cm)"
    )
    
    # OVERALL PERFORMANCE (Auto-calculated from subject scores)
    total_ca_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        help_text="Total CA scores across all subjects"
    )
    
    total_exam_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        help_text="Total exam scores across all subjects"
    )
    
    overall_total_score = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        help_text="Grand total of all subjects"
    )
    
    total_obtainable = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        help_text="Total marks obtainable"
    )
    
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Overall percentage (%)"
    )
    
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Average score"
    )
    
    # POSITION IN CLASS
    position_in_class = models.IntegerField(
        null=True,
        blank=True,
        help_text="Student's position in class (1st, 2nd, 3rd...)"
    )
    
    number_of_pupils_in_class = models.IntegerField(
        default=0,
        help_text="Total number of students in class"
    )
    
    # OVERALL GRADING (Nigerian Standard)
    GRADE_CHOICES = [
        ('A', 'A - Excellent (80-100)'),
        ('B', 'B - Good (60-79)'),
        ('C', 'C - Average (50-59)'),
        ('D', 'D - Below Average (40-49)'),
        ('E', 'E - Poor (Below 40)'),
    ]
    
    overall_grade = models.CharField(
        max_length=2,
        choices=GRADE_CHOICES,
        blank=True,
        help_text="Overall grade based on percentage"
    )
    
    REMARK_CHOICES = [
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('below_average', 'Below Average'),
        ('poor', 'Poor'),
    ]
    
    overall_remark = models.CharField(
        max_length=20,
        choices=REMARK_CHOICES,
        blank=True,
        help_text="Overall remark on performance"
    )
    
    # COMMENTS SECTION
    class_teacher_comment = models.TextField(
        blank=True,
        help_text="Class teacher's comment"
    )
    
    headmaster_comment = models.TextField(
        blank=True,
        help_text="Headmaster/Headmistress comment"
    )
    
    # NEXT TERM INFORMATION
    next_term_begins_on = models.DateField(
        null=True,
        blank=True,
        help_text="Date next term begins"
    )
    
    next_term_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="School fees for next term"
    )
    
    # PUBLICATION STATUS
    is_published = models.BooleanField(
        default=False,
        help_text="Is result published to student/parent?"
    )
    
    is_promoted = models.BooleanField(
        default=False,
        help_text="Is student promoted to next class?"
    )
    
    # SIGNATURES AND APPROVALS
    class_teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results_as_class_teacher'
    )
    
    headmaster = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='results_as_headmaster'
    )
    
    class_teacher_signature_date = models.DateField(null=True, blank=True)
    headmaster_signature_date = models.DateField(null=True, blank=True)
    
    # METADATA
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_results'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-session__start_date', '-term__term', 'class_level', 'student']
        unique_together = ['student', 'session', 'term']
        verbose_name = 'Student Result'
        verbose_name_plural = 'Student Results'
        indexes = [
            models.Index(fields=['student', 'session', 'term']),
            models.Index(fields=['class_level', 'session', 'term']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        try:
            student_name = self.student.user.get_full_name() if self.student and self.student.user else "Unknown Student"
            class_name = self.class_level.name if self.class_level else "No Class"
            term_name = str(self.term) if self.term else "No Term"
            return f"{student_name} - {class_name} - {term_name}"
        except Exception as e:
            logger.error(f"Error in __str__: {e}")
            return f"StudentResult {self.id}"

    def clean(self):
        """Validate attendance numbers"""
        try:
            total_days = self.no_of_times_present + self.no_of_times_absent
            
            if self.frequency_of_school_opened > 0 and total_days != self.frequency_of_school_opened:
                self.no_of_times_absent = self.frequency_of_school_opened - self.no_of_times_present
        except Exception as e:
            logger.error(f"Error in clean method: {e}")
    
    def safe_get_subject_scores(self):
        """
        Safely get subject scores with error handling
        Returns empty list if any error occurs
        """
        try:
            # Check if the related objects exist and are accessible
            if hasattr(self, 'subject_scores'):
                return list(self.subject_scores.all())
            return []
        except Exception as e:
            logger.error(f"Error getting subject scores for StudentResult {getattr(self, 'id', 'new')}: {e}")
            return []
    
    def calculate_totals(self):
        """
        Auto-calculate total scores, percentage, average, and grade
        ULTRA-SAFE version: prevents ANY database-related crash
        """
        try:
            # If object is not saved yet, skip calculation
            if not self.pk:
                self._reset_calculated_fields()
                return

            # Safely get subject scores
            subject_scores = self.safe_get_subject_scores()

            # If no subject scores exist or error occurred
            if not subject_scores:
                self._reset_calculated_fields()
                return

            # Calculate totals with safe value extraction
            total_ca = 0
            total_exam = 0
            total_score = 0
            total_obtainable = 0
            
            for score in subject_scores:
                try:
                    total_ca += float(score.ca_score or 0)
                    total_exam += float(score.exam_score or 0)
                    total_score += float(score.total_score or 0)
                    total_obtainable += float(score.total_obtainable or 0)
                except (TypeError, ValueError, AttributeError) as e:
                    logger.warning(f"Error processing subject score: {e}")
                    continue

            self.total_ca_score = round(total_ca, 2)
            self.total_exam_score = round(total_exam, 2)
            self.overall_total_score = round(total_score, 2)
            self.total_obtainable = round(total_obtainable, 2)

            # Calculate percentage and average safely
            if total_obtainable > 0 and len(subject_scores) > 0:
                self.percentage = round((total_score / total_obtainable) * 100, 2)
                self.average_score = round(total_score / len(subject_scores), 2)
            else:
                self.percentage = 0
                self.average_score = 0

            # Determine grade based on Nigerian standard
            self._assign_grade_and_remark()

        except Exception as e:
            logger.error(f"Unexpected error in calculate_totals for StudentResult {getattr(self, 'id', 'new')}: {e}")
            self._reset_calculated_fields()
    
    def _reset_calculated_fields(self):
        """Reset all calculated fields to default values"""
        self.total_ca_score = 0
        self.total_exam_score = 0
        self.overall_total_score = 0
        self.total_obtainable = 0
        self.percentage = 0
        self.average_score = 0
        self.overall_grade = ''
        self.overall_remark = ''
    
    def _assign_grade_and_remark(self):
        """Assign grade and remark based on percentage"""
        try:
            percentage = float(self.percentage)
            
            if percentage >= 80:
                self.overall_grade = 'A'
                self.overall_remark = 'excellent'
            elif percentage >= 60:
                self.overall_grade = 'B'
                self.overall_remark = 'good'
            elif percentage >= 50:
                self.overall_grade = 'C'
                self.overall_remark = 'average'
            elif percentage >= 40:
                self.overall_grade = 'D'
                self.overall_remark = 'below_average'
            else:
                self.overall_grade = 'E'
                self.overall_remark = 'poor'
        except (TypeError, ValueError) as e:
            logger.error(f"Error assigning grade: {e}")
            self.overall_grade = ''
            self.overall_remark = ''

    def calculate_position(self):
        """
        Calculate student's position in class
        SAFE version with error handling
        """
        try:
            # Don't calculate if missing required fields
            if not self.pk or not self.class_level or not self.session or not self.term:
                self.position_in_class = None
                self.number_of_pupils_in_class = 0
                return

            # Safely query with error handling
            try:
                class_results = StudentResult.objects.filter(
                    class_level=self.class_level,
                    session=self.session,
                    term=self.term,
                    overall_total_score__gt=0
                ).order_by('-overall_total_score', '-percentage')
                
                # Update total number of students
                self.number_of_pupils_in_class = class_results.count()
                
                # Calculate position
                position_found = False
                for position, result in enumerate(class_results, start=1):
                    if result.id == self.id:
                        self.position_in_class = position
                        position_found = True
                        break
                
                if not position_found:
                    self.position_in_class = None
                    
            except Exception as e:
                logger.error(f"Database error in calculate_position for StudentResult {self.id}: {e}")
                self.position_in_class = None
                self.number_of_pupils_in_class = 0
                
        except Exception as e:
            logger.error(f"Unexpected error in calculate_position for StudentResult {getattr(self, 'id', 'new')}: {e}")
            self.position_in_class = None
            self.number_of_pupils_in_class = 0

    def save(self, *args, **kwargs):
        """
        Overridden save method with robust error handling
        Prevents any database relation errors from crashing the system
        """
        try:
            # Run validation
            try:
                self.clean()
            except Exception as e:
                logger.error(f"Error in clean during save: {e}")

            # Check if this is a new object
            is_new = self.pk is None
            
            # FIRST SAVE (create PK if needed)
            try:
                super().save(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in initial save: {e}")
                # If save failed, re-raise for Django to handle
                raise

            # Now object has ID — try to update calculated fields
            try:
                self.calculate_totals()
            except Exception as e:
                logger.error(f"Error calculating totals after save: {e}")
            
            try:
                self.calculate_position()
            except Exception as e:
                logger.error(f"Error calculating position after save: {e}")

            # Update calculated fields only (if they changed)
            update_fields = kwargs.get('update_fields', None)
            
            # Only update calculated fields if we're not already updating specific fields
            if not update_fields:
                try:
                    super().save(update_fields=[
                        'total_ca_score',
                        'total_exam_score',
                        'overall_total_score',
                        'total_obtainable',
                        'percentage',
                        'average_score',
                        'overall_grade',
                        'overall_remark',
                        'position_in_class',
                        'number_of_pupils_in_class'
                    ])
                except Exception as e:
                    logger.error(f"Error updating calculated fields: {e}")
                    
        except Exception as e:
            logger.error(f"Critical error in save method for StudentResult: {e}")
            # Re-raise only critical errors, log others
            if "relation" in str(e) and "does not exist" in str(e):
                # Log table missing errors but don't crash
                logger.critical(f"Database table missing: {e}")
                # Still try to save without calculated fields
                try:
                    super().save(*args, **kwargs)
                except:
                    pass
            else:
                # For other errors, let Django handle them
                raise


class SubjectScore(models.Model):
    """
    Individual Subject Scores
    Matches the SUBJECTS table in the report card image
    """
    
    result = models.ForeignKey(
        StudentResult,
        on_delete=models.CASCADE,
        related_name='subject_scores'
    )
    
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='subject_scores'
    )
    
    # MARK OBTAINABLE (40 CA + 60 EXAM = 100 TOTAL)
    ca_obtainable = models.IntegerField(
        default=40,
        help_text="CA marks obtainable (usually 40)"
    )
    
    exam_obtainable = models.IntegerField(
        default=60,
        help_text="Exam marks obtainable (usually 60)"
    )
    
    total_obtainable = models.IntegerField(
        default=100,
        help_text="Total marks obtainable"
    )
    
    # SCORES
    ca_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="CA Score (out of 40)"
    )
    
    exam_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        help_text="Exam Score (out of 60)"
    )
    
    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Total Score (CA + Exam) out of 100"
    )
    
    # TERM SCORES FOR TRACKING
    first_term_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="First term total score"
    )
    
    second_term_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Second term total score"
    )
    
    third_term_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Third term total score"
    )
    
    # AGGREGATED SCORE
    aggregated_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Sum of all term scores"
    )
    
    # AVERAGE
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Average of all terms"
    )
    
    # GRADING (Nigerian Standard)
    GRADE_CHOICES = [
        ('A', 'A - Excellent (80-100)'),
        ('B', 'B - Good (60-79)'),
        ('C', 'C - Average (50-59)'),
        ('D', 'D - Below Average (40-49)'),
        ('E', 'E - Poor (Below 40)'),
    ]
    
    grade = models.CharField(
        max_length=2,
        choices=GRADE_CHOICES,
        blank=True,
        help_text="Subject grade"
    )
    
    # OBSERVATION ON CONDUCT
    OBSERVATION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ]
    
    observation_conduct = models.CharField(
        max_length=2,
        choices=OBSERVATION_CHOICES,
        blank=True,
        help_text="Teacher's observation on student conduct in this subject"
    )
    
    # Subject-specific remarks
    SUBJECT_REMARK_CHOICES = [
        ('honesty', 'Honesty'),
        ('punctuality', 'Punctuality'),
        ('attentiveness', 'Attentiveness'),
        ('politeness', 'Politeness'),
        ('neatness', 'Neatness'),
    ]
    
    subject_remark = models.CharField(
        max_length=20,
        choices=SUBJECT_REMARK_CHOICES,
        blank=True,
        help_text="Remark on student's attitude in this subject"
    )
    
    # Position in subject across class
    position_in_subject = models.IntegerField(
        null=True,
        blank=True,
        help_text="Student's position in this specific subject"
    )
    
    # Teacher's comment
    teacher_comment = models.TextField(
        blank=True,
        help_text="Teacher's comment on performance in this subject"
    )
    
    # METADATA
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['subject__name']
        unique_together = ['result', 'subject']
        verbose_name = 'Subject Score'
        verbose_name_plural = 'Subject Scores'
        indexes = [
            models.Index(fields=['result', 'subject']),
        ]

    def __str__(self):
        try:
            student_name = self.result.student.user.get_full_name() if self.result and self.result.student else "Unknown"
            subject_name = self.subject.name if self.subject else "Unknown Subject"
            return f"{student_name} - {subject_name}: {self.total_score}"
        except:
            return f"SubjectScore {self.id}"
    
    def clean(self):
        """Validate scores don't exceed obtainable marks"""
        if self.ca_score > self.ca_obtainable:
            raise ValidationError(f"CA score cannot exceed {self.ca_obtainable}")
        
        if self.exam_score > self.exam_obtainable:
            raise ValidationError(f"Exam score cannot exceed {self.exam_obtainable}")
    
    def calculate_total_and_grade(self):
        """Auto-calculate total score and assign grade"""
        try:
            # Calculate total
            self.total_score = (self.ca_score or 0) + (self.exam_score or 0)
            
            # Assign grade based on Nigerian standard
            total = float(self.total_score)
            if total >= 80:
                self.grade = 'A'
            elif total >= 60:
                self.grade = 'B'
            elif total >= 50:
                self.grade = 'C'
            elif total >= 40:
                self.grade = 'D'
            else:
                self.grade = 'E'
            
            # Update term-specific scores based on current term
            if self.result and self.result.term:
                current_term = self.result.term.term
                
                if current_term == 'first':
                    self.first_term_score = self.total_score
                elif current_term == 'second':
                    self.second_term_score = self.total_score
                elif current_term == 'third':
                    self.third_term_score = self.total_score
            
            # Calculate aggregated score and average
            scores = [
                self.first_term_score or 0,
                self.second_term_score or 0,
                self.third_term_score or 0
            ]
            
            valid_scores = [float(s) for s in scores if s and float(s) > 0]
            self.aggregated_score = sum(float(s) for s in scores)
            
            if valid_scores:
                self.average_score = round(sum(valid_scores) / len(valid_scores), 2)
            else:
                self.average_score = 0
                
        except Exception as e:
            logger.error(f"Error in SubjectScore.calculate_total_and_grade: {e}")
            self.grade = ''
    
    def save(self, *args, **kwargs):
        try:
            self.clean()
            self.calculate_total_and_grade()
            super().save(*args, **kwargs)
            
            # Safely recalculate parent result totals
            if self.result_id:
                try:
                    self.result.calculate_totals()
                    self.result.save(update_fields=[
                        'total_ca_score', 'total_exam_score', 'overall_total_score',
                        'total_obtainable', 'percentage', 'average_score',
                        'overall_grade', 'overall_remark'
                    ])
                except Exception as e:
                    logger.error(f"Error updating parent result: {e}")
                    
        except Exception as e:
            logger.error(f"Error in SubjectScore.save: {e}")
            raise


class PsychomotorSkills(models.Model):
    """
    PSYCHOMOTOR SKILLS ASSESSMENT
    From the report card image (5-point rating scale)
    """
    
    result = models.OneToOneField(
        StudentResult,
        on_delete=models.CASCADE,
        related_name='psychomotor_skills'
    )
    
    # Rating Scale
    RATING_CHOICES = [
        (5, '5 - Excellent'),
        (4, '4 - Good'),
        (3, '3 - Fair'),
        (2, '2 - Poor'),
        (1, '1 - Very Poor'),
    ]
    
    # Skills assessment
    handwriting = models.IntegerField(
        choices=RATING_CHOICES,
        default=3,
        help_text="Handwriting quality"
    )
    
    verbal_fluency = models.IntegerField(
        choices=RATING_CHOICES,
        default=3,
        help_text="Verbal fluency and communication"
    )
    
    drawing_and_painting = models.IntegerField(
        choices=RATING_CHOICES,
        default=3,
        help_text="Drawing and painting skills"
    )
    
    tools_handling = models.IntegerField(
        choices=RATING_CHOICES,
        default=3,
        help_text="Handling of tools and equipment"
    )
    
    sports = models.IntegerField(
        choices=RATING_CHOICES,
        default=3,
        help_text="Sports and physical activities"
    )
    
    # Additional skills
    musical_skills = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text="Musical skills and performance"
    )
    
    dancing = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text="Dancing and rhythmic movement"
    )
    
    craft_work = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text="Craft and handiwork"
    )
    
    # Overall psychomotor rating
    overall_psychomotor_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        help_text="Average psychomotor rating"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Psychomotor Skills'
        verbose_name_plural = 'Psychomotor Skills'
    
    def __str__(self):
        try:
            return f"Psychomotor Skills - {self.result.student.user.get_full_name()}"
        except:
            return f"PsychomotorSkills {self.id}"
    
    def calculate_overall_rating(self):
        """Calculate average psychomotor rating"""
        try:
            ratings = [
                self.handwriting,
                self.verbal_fluency,
                self.drawing_and_painting,
                self.tools_handling,
                self.sports,
            ]
            
            # Add optional ratings if they exist
            if self.musical_skills:
                ratings.append(self.musical_skills)
            if self.dancing:
                ratings.append(self.dancing)
            if self.craft_work:
                ratings.append(self.craft_work)
            
            if ratings:
                self.overall_psychomotor_rating = round(sum(ratings) / len(ratings), 2)
        except Exception as e:
            logger.error(f"Error calculating psychomotor rating: {e}")
            self.overall_psychomotor_rating = 0
    
    def save(self, *args, **kwargs):
        try:
            self.calculate_overall_rating()
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving PsychomotorSkills: {e}")
            raise


class AffectiveDomains(models.Model):
    """
    AFFECTIVE DOMAINS / BEHAVIORAL ASSESSMENT
    From the report card image with checkboxes (5-point rating)
    """
    
    result = models.OneToOneField(
        StudentResult,
        on_delete=models.CASCADE,
        related_name='affective_domains'
    )
    
    # Rating Scale
    RATING_CHOICES = [
        (5, '5 - Excellent'),
        (4, '4 - Good'),
        (3, '3 - Fair'),
        (2, '2 - Poor'),
        (1, '1 - Very Poor'),
    ]
    
    # Behavioral traits assessment
    punctuality = models.IntegerField(choices=RATING_CHOICES, default=3)
    neatness = models.IntegerField(choices=RATING_CHOICES, default=3)
    politeness = models.IntegerField(choices=RATING_CHOICES, default=3)
    honesty = models.IntegerField(choices=RATING_CHOICES, default=3)
    cooperation_with_others = models.IntegerField(choices=RATING_CHOICES, default=3)
    leadership = models.IntegerField(choices=RATING_CHOICES, default=3)
    altruism = models.IntegerField(choices=RATING_CHOICES, default=3)
    emotional_stability = models.IntegerField(choices=RATING_CHOICES, default=3)
    health = models.IntegerField(choices=RATING_CHOICES, default=3)
    attitude = models.IntegerField(choices=RATING_CHOICES, default=3)
    attentiveness = models.IntegerField(choices=RATING_CHOICES, default=3)
    perseverance = models.IntegerField(choices=RATING_CHOICES, default=3)
    communication_skill = models.IntegerField(choices=RATING_CHOICES, default=3)
    
    # Overall affective rating
    overall_affective_rating = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0,
        help_text="Average affective rating"
    )
    
    # General comment on behavior
    behavioral_comment = models.TextField(
        blank=True,
        help_text="General comment on student's behavior"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Affective Domain'
        verbose_name_plural = 'Affective Domains'
    
    def __str__(self):
        try:
            return f"Affective Domains - {self.result.student.user.get_full_name()}"
        except:
            return f"AffectiveDomains {self.id}"
    
    def calculate_overall_rating(self):
        """Calculate average affective rating"""
        try:
            ratings = [
                self.punctuality,
                self.neatness,
                self.politeness,
                self.honesty,
                self.cooperation_with_others,
                self.leadership,
                self.altruism,
                self.emotional_stability,
                self.health,
                self.attitude,
                self.attentiveness,
                self.perseverance,
                self.communication_skill,
            ]
            
            if ratings:
                self.overall_affective_rating = round(sum(ratings) / len(ratings), 2)
        except Exception as e:
            logger.error(f"Error calculating affective rating: {e}")
            self.overall_affective_rating = 0
    
    def save(self, *args, **kwargs):
        try:
            self.calculate_overall_rating()
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error saving AffectiveDomains: {e}")
            raise


class ResultPublishing(models.Model):
    """
    Result Publishing Control
    Manage when results are published to students/parents
    """
    
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='result_publishing'
    )
    
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE,
        related_name='result_publishing'
    )
    
    class_level = models.ForeignKey(
        'academic.ClassLevel',
        on_delete=models.CASCADE,
        related_name='published_results',
        null=True,  # Make it nullable temporarily
        blank=True
    )
        
    is_published = models.BooleanField(
        default=False,
        help_text="Are results published to students/parents?"
    )
    
    published_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time results were published"
    )
    
    published_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who published the results"
    )
    
    remarks = models.TextField(
        blank=True,
        help_text="Publishing remarks or special instructions"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['session', 'term', 'class_level']
        verbose_name = 'Result Publishing'
        verbose_name_plural = 'Result Publishing'
        indexes = [
            models.Index(fields=['session', 'term', 'class_level']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        try:
            class_name = self.class_level.name if self.class_level else "All Classes"
            term_name = str(self.term) if self.term else "No Term"
            return f"{class_name} - {term_name} - {'Published' if self.is_published else 'Not Published'}"
        except:
            return f"ResultPublishing {self.id}"
    
    def publish_results(self, user):
        """Publish results for this session, term, and class"""
        try:
            self.is_published = True
            self.published_date = timezone.now()
            self.published_by = user
            
            # Update all student results to published
            results = StudentResult.objects.filter(
                session=self.session,
                term=self.term
            )
            
            if self.class_level:
                results = results.filter(class_level=self.class_level)
            
            results.update(is_published=True)
            self.save()
        except Exception as e:
            logger.error(f"Error publishing results: {e}")
            raise
    
    def unpublish_results(self):
        """Unpublish results for this session, term, and class"""
        try:
            self.is_published = False
            self.published_date = None
            self.published_by = None
            
            # Update all student results to not published
            results = StudentResult.objects.filter(
                session=self.session,
                term=self.term
            )
            
            if self.class_level:
                results = results.filter(class_level=self.class_level)
            
            results.update(is_published=False)
            self.save()
        except Exception as e:
            logger.error(f"Error unpublishing results: {e}")
            raise