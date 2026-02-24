# # academic/management/commands/load_nigerian_data.py
# """
# Django management command to load complete Nigerian academic data
# Run: python manage.py load_nigerian_data
# """

# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from datetime import date
# from academic.models import (
#     AcademicSession, AcademicTerm, Program, ClassLevel, Subject
# )


# class Command(BaseCommand):
#     help = 'Load complete Nigerian academic data (sessions, terms, programs, class levels, subjects)'

#     def handle(self, *args, **kwargs):
#         self.stdout.write('Starting to load Nigerian academic data...\n')
        
#         # Load data
#         self.load_sessions()
#         self.load_terms()
#         self.load_programs()
#         self.load_class_levels()
#         self.load_subjects()
        
#         self.stdout.write(self.style.SUCCESS('\n✅ All Nigerian academic data loaded successfully!'))

#     def load_sessions(self):
#         self.stdout.write('Loading Academic Sessions...')
        
#         sessions_data = [
#             {
#                 'name': '2024/2025 Academic Session',
#                 'start_date': date(2024, 9, 16),
#                 'end_date': date(2025, 7, 18),
#                 'is_current': True,
#                 'status': 'active',
#                 'description': 'Current academic session for all classes'
#             },
#             {
#                 'name': '2025/2026 Academic Session',
#                 'start_date': date(2025, 9, 15),
#                 'end_date': date(2026, 7, 17),
#                 'is_current': False,
#                 'status': 'upcoming',
#                 'description': 'Next academic session'
#             },
#         ]
        
#         for data in sessions_data:
#             session, created = AcademicSession.objects.get_or_create(
#                 name=data['name'],
#                 defaults=data
#             )
#             if created:
#                 self.stdout.write(f'  ✓ Created: {session.name}')
#             else:
#                 self.stdout.write(f'  - Already exists: {session.name}')

#     def load_terms(self):
#         self.stdout.write('\nLoading Academic Terms...')
        
#         current_session = AcademicSession.objects.get(name='2024/2025 Academic Session')
        
#         terms_data = [
#             {
#                 'session': current_session,
#                 'term': 'first',
#                 'name': 'First Term 2024/2025',
#                 'start_date': date(2024, 9, 16),
#                 'end_date': date(2024, 12, 20),
#                 'is_current': True,
#                 'status': 'active',
#                 'resumption_date': date(2024, 9, 16),
#                 'vacation_date': date(2024, 12, 20),
#                 'total_school_days': 65,
#                 'total_teaching_weeks': 13,
#                 'mid_term_break_start': date(2024, 10, 28),
#                 'mid_term_break_end': date(2024, 11, 1)
#             },
#             {
#                 'session': current_session,
#                 'term': 'second',
#                 'name': 'Second Term 2024/2025',
#                 'start_date': date(2025, 1, 13),
#                 'end_date': date(2025, 4, 11),
#                 'is_current': False,
#                 'status': 'upcoming',
#                 'resumption_date': date(2025, 1, 13),
#                 'vacation_date': date(2025, 4, 11),
#                 'total_school_days': 60,
#                 'total_teaching_weeks': 12,
#                 'mid_term_break_start': date(2025, 2, 17),
#                 'mid_term_break_end': date(2025, 2, 21)
#             },
#             {
#                 'session': current_session,
#                 'term': 'third',
#                 'name': 'Third Term 2024/2025',
#                 'start_date': date(2025, 4, 28),
#                 'end_date': date(2025, 7, 18),
#                 'is_current': False,
#                 'status': 'upcoming',
#                 'resumption_date': date(2025, 4, 28),
#                 'vacation_date': date(2025, 7, 18),
#                 'total_school_days': 55,
#                 'total_teaching_weeks': 11,
#                 'mid_term_break_start': date(2025, 6, 2),
#                 'mid_term_break_end': date(2025, 6, 6)
#             },
#         ]
        
#         for data in terms_data:
#             term, created = AcademicTerm.objects.get_or_create(
#                 session=data['session'],
#                 term=data['term'],
#                 defaults=data
#             )
#             if created:
#                 self.stdout.write(f'  ✓ Created: {term.name}')
#             else:
#                 self.stdout.write(f'  - Already exists: {term.name}')

#     def load_programs(self):
#         self.stdout.write('\nLoading Programs...')
        
#         programs_data = [
#             {
#                 'name': 'Creche',
#                 'program_type': 'creche',
#                 'code': 'CRE',
#                 'description': 'Early childhood care for children aged 0-2 years',
#                 'duration_years': 2,
#                 'is_active': True
#             },
#             {
#                 'name': 'Nursery',
#                 'program_type': 'nursery',
#                 'code': 'NUR',
#                 'description': 'Pre-primary education for children aged 3-5 years',
#                 'duration_years': 4,
#                 'is_active': True
#             },
#             {
#                 'name': 'Primary School',
#                 'program_type': 'primary',
#                 'code': 'PRI',
#                 'description': 'Basic education from Primary 1 to Primary 6 (Basic 1-6)',
#                 'duration_years': 6,
#                 'is_active': True
#             },
#             {
#                 'name': 'Junior Secondary School',
#                 'program_type': 'junior_secondary',
#                 'code': 'JSS',
#                 'description': 'Junior Secondary education (JSS 1-3)',
#                 'duration_years': 3,
#                 'is_active': True
#             },
#             {
#                 'name': 'Senior Secondary School',
#                 'program_type': 'senior_secondary',
#                 'code': 'SSS',
#                 'description': 'Senior Secondary education with specialization (SSS 1-3)',
#                 'duration_years': 3,
#                 'is_active': True
#             },
#         ]
        
#         for data in programs_data:
#             program, created = Program.objects.get_or_create(
#                 code=data['code'],
#                 defaults=data
#             )
#             if created:
#                 self.stdout.write(f'  ✓ Created: {program.name}')
#             else:
#                 self.stdout.write(f'  - Already exists: {program.name}')

#     def load_class_levels(self):
#         self.stdout.write('\nLoading Class Levels...')
        
#         # Get programs
#         creche_prog = Program.objects.get(code='CRE')
#         nursery_prog = Program.objects.get(code='NUR')
#         primary_prog = Program.objects.get(code='PRI')
#         jss_prog = Program.objects.get(code='JSS')
#         sss_prog = Program.objects.get(code='SSS')
        
#         class_levels_data = [
#             # Creche
#             {'program': creche_prog, 'level': 'creche', 'name': 'Creche', 'code': 'CRE', 'order': 1, 'min_age': 0, 'max_age': 2},
            
#             # Nursery
#             {'program': nursery_prog, 'level': 'nursery_1', 'name': 'Nursery 1', 'code': 'NUR1', 'order': 2, 'min_age': 3, 'max_age': 4},
#             {'program': nursery_prog, 'level': 'nursery_2', 'name': 'Nursery 2', 'code': 'NUR2', 'order': 3, 'min_age': 4, 'max_age': 5},
#             {'program': nursery_prog, 'level': 'kg_1', 'name': 'Kindergarten 1 (KG 1)', 'code': 'KG1', 'order': 4, 'min_age': 5, 'max_age': 6},
#             {'program': nursery_prog, 'level': 'kg_2', 'name': 'Kindergarten 2 (KG 2)', 'code': 'KG2', 'order': 5, 'min_age': 6, 'max_age': 7},
            
#             # Primary
#             {'program': primary_prog, 'level': 'primary_1', 'name': 'Primary 1 (Basic 1)', 'code': 'P1', 'order': 6, 'min_age': 6, 'max_age': 7},
#             {'program': primary_prog, 'level': 'primary_2', 'name': 'Primary 2 (Basic 2)', 'code': 'P2', 'order': 7, 'min_age': 7, 'max_age': 8},
#             {'program': primary_prog, 'level': 'primary_3', 'name': 'Primary 3 (Basic 3)', 'code': 'P3', 'order': 8, 'min_age': 8, 'max_age': 9},
#             {'program': primary_prog, 'level': 'primary_4', 'name': 'Primary 4 (Basic 4)', 'code': 'P4', 'order': 9, 'min_age': 9, 'max_age': 10},
#             {'program': primary_prog, 'level': 'primary_5', 'name': 'Primary 5 (Basic 5)', 'code': 'P5', 'order': 10, 'min_age': 10, 'max_age': 11},
#             {'program': primary_prog, 'level': 'primary_6', 'name': 'Primary 6 (Basic 6)', 'code': 'P6', 'order': 11, 'min_age': 11, 'max_age': 12, 'has_common_entrance': True},
            
#             # JSS
#             {'program': jss_prog, 'level': 'jss_1', 'name': 'JSS 1', 'code': 'JSS1', 'order': 12, 'min_age': 12, 'max_age': 13},
#             {'program': jss_prog, 'level': 'jss_2', 'name': 'JSS 2', 'code': 'JSS2', 'order': 13, 'min_age': 13, 'max_age': 14},
#             {'program': jss_prog, 'level': 'jss_3', 'name': 'JSS 3', 'code': 'JSS3', 'order': 14, 'min_age': 14, 'max_age': 15, 'has_bece': True},
            
#             # SSS
#             {'program': sss_prog, 'level': 'sss_1', 'name': 'SSS 1', 'code': 'SSS1', 'order': 15, 'min_age': 15, 'max_age': 16},
#             {'program': sss_prog, 'level': 'sss_2', 'name': 'SSS 2', 'code': 'SSS2', 'order': 16, 'min_age': 16, 'max_age': 17},
#             {'program': sss_prog, 'level': 'sss_3', 'name': 'SSS 3', 'code': 'SSS3', 'order': 17, 'min_age': 17, 'max_age': 18, 'has_waec_neco': True},
#         ]
        
#         for data in class_levels_data:
#             class_level, created = ClassLevel.objects.get_or_create(
#                 code=data['code'],
#                 defaults=data
#             )
#             if created:
#                 self.stdout.write(f'  ✓ Created: {class_level.name}')
#             else:
#                 self.stdout.write(f'  - Already exists: {class_level.name}')

#     def load_subjects(self):
#         self.stdout.write('\nLoading Subjects...')
        
#         subjects_data = [
#             # CRECHE & NURSERY SUBJECTS
#             {'name': 'Play Activities', 'code': 'PLAY', 'short_name': 'Play', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True, 'is_examinable': False, 'has_practical': True, 'ca_weight': 100, 'exam_weight': 0, 'available_for_creche': True, 'available_for_nursery': False},
#             {'name': 'Songs and Rhymes', 'code': 'SONG', 'short_name': 'Songs', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True, 'is_examinable': False, 'has_practical': True, 'ca_weight': 100, 'exam_weight': 0, 'available_for_creche': True, 'available_for_nursery': True},
#             {'name': 'Early Literacy', 'code': 'ELIT', 'short_name': 'Literacy', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True, 'is_examinable': True, 'available_for_nursery': True},
#             {'name': 'Early Numeracy', 'code': 'ENUM', 'short_name': 'Numeracy', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True, 'is_examinable': True, 'available_for_nursery': True},
#             {'name': 'Creative Arts', 'code': 'CART', 'short_name': 'Arts', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True, 'is_examinable': False, 'has_practical': True, 'ca_weight': 100, 'exam_weight': 0, 'available_for_nursery': True},
            
#             # CORE SUBJECTS (All levels)
#             {'name': 'English Language', 'code': 'ENG', 'short_name': 'English', 'subject_type': 'core', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'description': 'English Language - compulsory for all levels'},
#             {'name': 'Mathematics', 'code': 'MATH', 'short_name': 'Maths', 'subject_type': 'core', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'description': 'Mathematics - compulsory for all levels'},
            
#             # PRIMARY & JSS SUBJECTS
#             {'name': 'Basic Science', 'code': 'BSC', 'short_name': 'Basic Sci.', 'subject_type': 'science', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'has_practical': True, 'available_for_primary': True, 'available_for_jss': True},
#             {'name': 'Basic Technology', 'code': 'BTECH', 'short_name': 'Basic Tech', 'subject_type': 'technical', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'has_practical': True, 'available_for_primary': True, 'available_for_jss': True},
#             {'name': 'Social Studies', 'code': 'SOC', 'short_name': 'Social St.', 'subject_type': 'arts', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True},
#             {'name': 'Cultural and Creative Arts', 'code': 'CCA', 'short_name': 'CCA', 'subject_type': 'arts', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'has_practical': True, 'available_for_primary': True, 'available_for_jss': True},
#             {'name': 'Physical and Health Education', 'code': 'PHE', 'short_name': 'PHE', 'subject_type': 'core', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'has_practical': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True},
            
#             # RELIGIOUS STUDIES
#             {'name': 'Christian Religious Studies', 'code': 'CRS', 'short_name': 'CRS', 'subject_type': 'religious', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True},
#             {'name': 'Islamic Religious Studies', 'code': 'IRS', 'short_name': 'IRS', 'subject_type': 'religious', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True},
            
#             # NIGERIAN LANGUAGES
#             {'name': 'Yoruba Language', 'code': 'YOR', 'short_name': 'Yoruba', 'subject_type': 'language', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True},
#             {'name': 'Igbo Language', 'code': 'IGB', 'short_name': 'Igbo', 'subject_type': 'language', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True},
#             {'name': 'Hausa Language', 'code': 'HAU', 'short_name': 'Hausa', 'subject_type': 'language', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True},
#             {'name': 'French Language', 'code': 'FRE', 'short_name': 'French', 'subject_type': 'language', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True},
            
#             # JSS SPECIFIC
#             {'name': 'Computer Studies', 'code': 'COMP', 'short_name': 'Computer', 'subject_type': 'technical', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'has_practical': True, 'available_for_jss': True, 'available_for_sss': True},
#             {'name': 'Home Economics', 'code': 'HECO', 'short_name': 'Home Econ', 'subject_type': 'vocational', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_jss': True},
#             {'name': 'Agricultural Science', 'code': 'AGRIC', 'short_name': 'Agric', 'subject_type': 'science', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_jss': True, 'available_for_sss': True},
            
#             # SSS SCIENCE STREAM
#             {'name': 'Biology', 'code': 'BIO', 'short_name': 'Biology', 'subject_type': 'science', 'stream': 'science', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_sss': True, 'description': 'Biology for Science stream'},
#             {'name': 'Chemistry', 'code': 'CHEM', 'short_name': 'Chemistry', 'subject_type': 'science', 'stream': 'science', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_sss': True, 'description': 'Chemistry for Science stream'},
#             {'name': 'Physics', 'code': 'PHY', 'short_name': 'Physics', 'subject_type': 'science', 'stream': 'science', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_sss': True, 'description': 'Physics for Science stream'},
#             {'name': 'Further Mathematics', 'code': 'FMATH', 'short_name': 'Further Maths', 'subject_type': 'science', 'stream': 'science', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Technical Drawing', 'code': 'TD', 'short_name': 'Tech Draw', 'subject_type': 'technical', 'stream': 'science', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_sss': True},
            
#             # SSS COMMERCIAL STREAM
#             {'name': 'Financial Accounting', 'code': 'FACC', 'short_name': 'Accounting', 'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Commerce', 'code': 'COM', 'short_name': 'Commerce', 'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Economics', 'code': 'ECON', 'short_name': 'Economics', 'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Book Keeping', 'code': 'BKPG', 'short_name': 'Book Keep', 'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Office Practice', 'code': 'OFPRAC', 'short_name': 'Office Prac', 'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Typewriting', 'code': 'TYPE', 'short_name': 'Typing', 'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_sss': True},
            
#             # SSS ARTS STREAM
#             {'name': 'Literature in English', 'code': 'LIT', 'short_name': 'Literature', 'subject_type': 'arts', 'stream': 'arts', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Government', 'code': 'GOV', 'short_name': 'Government', 'subject_type': 'arts', 'stream': 'arts', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'History', 'code': 'HIST', 'short_name': 'History', 'subject_type': 'arts', 'stream': 'arts', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Geography', 'code': 'GEO', 'short_name': 'Geography', 'subject_type': 'arts', 'stream': 'arts', 'is_compulsory': False, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Fine Arts', 'code': 'FART', 'short_name': 'Fine Arts', 'subject_type': 'arts', 'stream': 'arts', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_sss': True},
#             {'name': 'Music', 'code': 'MUS', 'short_name': 'Music', 'subject_type': 'arts', 'stream': 'arts', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_sss': True},
            
#             # SSS GENERAL (All streams)
#             {'name': 'Civic Education', 'code': 'CIV', 'short_name': 'Civic Ed', 'subject_type': 'core', 'stream': 'general', 'is_compulsory': True, 'is_examinable': True, 'available_for_sss': True},
#             {'name': 'Data Processing', 'code': 'DPROC', 'short_name': 'Data Proc', 'subject_type': 'technical', 'stream': 'general', 'is_compulsory': False, 'is_examinable': True, 'has_practical': True, 'available_for_sss': True},
#         ]
        
#         for data in subjects_data:
#             # Set defaults for fields not in data
#             defaults = {
#                 'short_name': data.get('short_name', ''),
#                 'subject_type': data.get('subject_type', 'core'),
#                 'stream': data.get('stream', 'general'),
#                 'is_compulsory': data.get('is_compulsory', False),
#                 'is_examinable': data.get('is_examinable', True),
#                 'has_practical': data.get('has_practical', False),
#                 'ca_weight': data.get('ca_weight', 40),
#                 'exam_weight': data.get('exam_weight', 60),
#                 'total_marks': data.get('total_marks', 100),
#                 'pass_mark': data.get('pass_mark', 40),
#                 'available_for_creche': data.get('available_for_creche', False),
#                 'available_for_nursery': data.get('available_for_nursery', False),
#                 'available_for_primary': data.get('available_for_primary', False),
#                 'available_for_jss': data.get('available_for_jss', False),
#                 'available_for_sss': data.get('available_for_sss', False),
#                 'is_active': data.get('is_active', True),
#                 'description': data.get('description', ''),
#             }
            
#             subject, created = Subject.objects.get_or_create(
#                 code=data['code'],
#                 defaults={'name': data['name'], **defaults}
#             )
#             if created:
#                 self.stdout.write(f'  ✓ Created: {subject.name} ({subject.code})')
#             else:
#                 self.stdout.write(f'  - Already exists: {subject.name} ({subject.code})')



# academic/management/commands/load_complete_nigerian_data.py
"""
Complete Nigerian Academic Data Loader - ALL SUBJECTS & CLASSES
Run: python manage.py load_complete_nigerian_data
"""

from django.core.management.base import BaseCommand
from datetime import date
from academic.models import AcademicSession, AcademicTerm, Program, ClassLevel, Subject


class Command(BaseCommand):
    help = 'Load complete Nigerian academic data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(self.style.WARNING('COMPLETE NIGERIAN ACADEMIC DATA LOADER'))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))
        
        self.load_sessions()
        self.load_terms()
        self.load_programs()
        self.load_class_levels()
        self.load_subjects()
        
        self.stdout.write(self.style.SUCCESS('\n✅ ALL DATA LOADED SUCCESSFULLY!\n'))

    def load_sessions(self):
        self.stdout.write('📅 Loading Academic Sessions...')
        sessions = [
            ('2024/2025', date(2024, 9, 16), date(2025, 7, 18), True, 'active'),
            ('2025/2026', date(2025, 9, 15), date(2026, 7, 17), False, 'upcoming'),
            ('2026/2027', date(2026, 9, 14), date(2027, 7, 16), False, 'upcoming'),
            ('2027/2028', date(2027, 9, 13), date(2028, 7, 14), False, 'upcoming'),
            ('2028/2029', date(2028, 9, 18), date(2029, 7, 20), False, 'upcoming'),
            ('2029/2030', date(2029, 9, 17), date(2030, 7, 19), False, 'upcoming'),
            ('2030/2031', date(2030, 9, 16), date(2031, 7, 18), False, 'upcoming'),
            ('2031/2032', date(2031, 9, 15), date(2032, 7, 16), False, 'upcoming'),
            ('2032/2033', date(2032, 9, 13), date(2033, 7, 15), False, 'upcoming'),
            ('2033/2034', date(2033, 9, 19), date(2034, 7, 21), False, 'upcoming'),
            ('2034/2035', date(2034, 9, 18), date(2035, 7, 20), False, 'upcoming'),
            ('2035/2036', date(2035, 9, 17), date(2036, 7, 18), False, 'upcoming'),
            ('2036/2037', date(2036, 9, 15), date(2037, 7, 17), False, 'upcoming'),
            ('2037/2038', date(2037, 9, 14), date(2038, 7, 16), False, 'upcoming'),
            ('2038/2039', date(2038, 9, 13), date(2039, 7, 15), False, 'upcoming'),
            ('2039/2040', date(2039, 9, 19), date(2040, 7, 21), False, 'upcoming'),
        ]
        
        for name, start, end, is_current, status in sessions:
            session, created = AcademicSession.objects.get_or_create(
                name=f'{name} Academic Session',
                defaults={'start_date': start, 'end_date': end, 'is_current': is_current, 'status': status}
            )
            self.stdout.write(f"  {'✓ Created' if created else '- Exists'}: {session.name}")

    def load_terms(self):
        self.stdout.write('\n📚 Loading Academic Terms...')
        session = AcademicSession.objects.get(name='2024/2025 Academic Session')
        
        terms = [
            ('first', 'First Term 2024/2025', date(2024, 9, 16), date(2024, 12, 20), True, 'active', 65, 13),
            ('second', 'Second Term 2024/2025', date(2025, 1, 13), date(2025, 4, 11), False, 'upcoming', 60, 12),
            ('third', 'Third Term 2024/2025', date(2025, 4, 28), date(2025, 7, 18), False, 'upcoming', 55, 11),
        ]
        
        for term_type, name, start, end, is_current, status, days, weeks in terms:
            term, created = AcademicTerm.objects.get_or_create(
                session=session, term=term_type,
                defaults={'name': name, 'start_date': start, 'end_date': end, 'is_current': is_current,
                         'status': status, 'total_school_days': days, 'total_teaching_weeks': weeks}
            )
            self.stdout.write(f"  {'✓ Created' if created else '- Exists'}: {term.name}")

    def load_programs(self):
        self.stdout.write('\n🎓 Loading Programs...')
        programs = [
            ('Creche', 'creche', 'CRE', 2),
            ('Nursery', 'nursery', 'NUR', 4),
            ('Primary School', 'primary', 'PRI', 6),
            ('Junior Secondary School', 'junior_secondary', 'JSS', 3),
            ('Senior Secondary School', 'senior_secondary', 'SSS', 3),
        ]
        
        for name, prog_type, code, duration in programs:
            prog, created = Program.objects.get_or_create(
                code=code,
                defaults={'name': name, 'program_type': prog_type, 'duration_years': duration, 'is_active': True}
            )
            self.stdout.write(f"  {'✓ Created' if created else '- Exists'}: {prog.name}")

    def load_class_levels(self):
        self.stdout.write('\n📖 Loading Class Levels...')
        
        levels = [
            ('CRE', 'creche', 'Creche', 'CRE', 1, 0, 2),
            ('NUR', 'nursery_1', 'Nursery 1', 'NUR1', 2, 3, 4),
            ('NUR', 'nursery_2', 'Nursery 2', 'NUR2', 3, 4, 5),
            ('NUR', 'kg_1', 'Kindergarten 1 (KG 1)', 'KG1', 4, 5, 6),
            ('NUR', 'kg_2', 'Kindergarten 2 (KG 2)', 'KG2', 5, 6, 7),
            ('PRI', 'primary_1', 'Primary 1 (Basic 1)', 'P1', 6, 6, 7),
            ('PRI', 'primary_2', 'Primary 2 (Basic 2)', 'P2', 7, 7, 8),
            ('PRI', 'primary_3', 'Primary 3 (Basic 3)', 'P3', 8, 8, 9),
            ('PRI', 'primary_4', 'Primary 4 (Basic 4)', 'P4', 9, 9, 10),
            ('PRI', 'primary_5', 'Primary 5 (Basic 5)', 'P5', 10, 10, 11),
            ('PRI', 'primary_6', 'Primary 6 (Basic 6)', 'P6', 11, 11, 12),
            ('JSS', 'jss_1', 'JSS 1 (Basic 7)', 'JSS1', 12, 12, 13),
            ('JSS', 'jss_2', 'JSS 2 (Basic 8)', 'JSS2', 13, 13, 14),
            ('JSS', 'jss_3', 'JSS 3 (Basic 9)', 'JSS3', 14, 14, 15),
            ('SSS', 'sss_1', 'SSS 1', 'SSS1', 15, 15, 16),
            ('SSS', 'sss_2', 'SSS 2', 'SSS2', 16, 16, 17),
            ('SSS', 'sss_3', 'SSS 3', 'SSS3', 17, 17, 18),
        ]
        
        for prog_code, level, name, code, order, min_age, max_age in levels:
            program = Program.objects.get(code=prog_code)
            cl, created = ClassLevel.objects.get_or_create(
                code=code,
                defaults={'program': program, 'level': level, 'name': name, 'order': order,
                         'min_age': min_age, 'max_age': max_age, 'is_active': True}
            )
            self.stdout.write(f"  {'✓ Created' if created else '- Exists'}: {cl.name}")

    def load_subjects(self):
        self.stdout.write('\n📝 Loading ALL Nigerian Subjects...')
        
        subjects = [
            # CRECHE (3 subjects)
            ('Play Activities', 'PLAY', 'Play', 'pre_school', 'pre_school', True, False, True, 100, 0, True, False, False, False, False),
            ('Songs and Rhymes', 'SONG', 'Songs', 'pre_school', 'pre_school', True, False, True, 100, 0, True, True, False, False, False),
            ('Sensory Play', 'SENS', 'Sensory', 'pre_school', 'pre_school', True, False, True, 100, 0, True, False, False, False, False),
            
            # NURSERY (8 additional subjects)
            ('Early Literacy', 'ELIT', 'Literacy', 'pre_school', 'pre_school', True, True, False, 40, 60, False, True, False, False, False),
            ('Early Numeracy', 'ENUM', 'Numeracy', 'pre_school', 'pre_school', True, True, False, 40, 60, False, True, False, False, False),
            ('Creative Arts', 'CART', 'Arts', 'pre_school', 'pre_school', True, False, True, 100, 0, False, True, False, False, False),
            ('Pre-Writing Skills', 'PWRT', 'Pre-Writing', 'pre_school', 'pre_school', True, True, False, 40, 60, False, True, False, False, False),
            ('Pre-Reading Skills', 'PRED', 'Pre-Reading', 'pre_school', 'pre_school', True, True, False, 40, 60, False, True, False, False, False),
            ('Health Habits', 'HHAB', 'Health', 'pre_school', 'pre_school', True, True, False, 40, 60, False, True, False, False, False),
            ('Social Studies (Nursery)', 'SOCN', 'Social St.', 'pre_school', 'pre_school', True, True, False, 40, 60, False, True, False, False, False),
            ('Rhymes and Stories', 'RHYM', 'Rhymes', 'pre_school', 'pre_school', True, False, False, 100, 0, False, True, False, False, False),
            
            # CORE SUBJECTS - All Levels (2 subjects)
            ('English Language', 'ENG', 'English', 'core', 'general', True, True, False, 40, 60, False, False, True, True, True),
            ('Mathematics', 'MATH', 'Maths', 'core', 'general', True, True, False, 40, 60, False, False, True, True, True),
            
            # PRIMARY CORE (10 subjects)
            ('Basic Science', 'BSC', 'Basic Sci.', 'science', 'general', True, True, True, 40, 60, False, False, True, True, False),
            ('Basic Technology', 'BTECH', 'Basic Tech', 'technical', 'general', True, True, True, 40, 60, False, False, True, True, False),
            ('Social Studies', 'SOC', 'Social St.', 'arts', 'general', True, True, False, 40, 60, False, False, True, True, False),
            ('Cultural and Creative Arts', 'CCA', 'CCA', 'arts', 'general', True, True, True, 40, 60, False, False, True, True, False),
            ('Physical and Health Education', 'PHE', 'PHE', 'core', 'general', True, True, True, 40, 60, False, False, True, True, True),
            ('Civic Education', 'CIV', 'Civic Ed', 'core', 'general', True, True, False, 40, 60, False, False, True, True, True),
            ('Quantitative Reasoning', 'QREA', 'Quant. Reasoning', 'core', 'general', False, True, False, 40, 60, False, False, True, False, False),
            ('Verbal Reasoning', 'VREA', 'Verbal Reasoning', 'core', 'general', False, True, False, 40, 60, False, False, True, False, False),
            ('Phonics', 'PHON', 'Phonics', 'language', 'general', True, True, False, 40, 60, False, False, True, False, False),
            ('Handwriting', 'HWRT', 'Handwriting', 'core', 'general', True, True, False, 40, 60, False, False, True, False, False),
            ('Diction', 'DICT', 'Diction', 'language', 'general', True, True, False, 40, 60, False, False, True, False, False),
            
            # RELIGIOUS STUDIES (3 subjects)
            ('Christian Religious Studies', 'CRS', 'CRS', 'religious', 'general', False, True, False, 40, 60, False, False, True, True, True),
            ('Islamic Religious Studies', 'IRS', 'IRS', 'religious', 'general', False, True, False, 40, 60, False, False, True, True, True),
            ('Arabic Language', 'ARB', 'Arabic', 'language', 'general', False, True, False, 40, 60, False, False, True, True, True),
            
            # NIGERIAN LANGUAGES (4 subjects)
            ('Yoruba Language', 'YOR', 'Yoruba', 'language', 'general', False, True, False, 40, 60, False, False, True, True, True),
            ('Igbo Language', 'IGB', 'Igbo', 'language', 'general', False, True, False, 40, 60, False, False, True, True, True),
            ('Hausa Language', 'HAU', 'Hausa', 'language', 'general', False, True, False, 40, 60, False, False, True, True, True),
            ('French Language', 'FRE', 'French', 'language', 'general', False, True, False, 40, 60, False, False, True, True, True),
            
            # JSS SPECIFIC (7 subjects)
            ('Computer Studies', 'COMP', 'Computer', 'technical', 'general', True, True, True, 40, 60, False, False, False, True, True),
            ('Home Economics', 'HECO', 'Home Econ', 'vocational', 'general', False, True, True, 40, 60, False, False, False, True, True),
            ('Agricultural Science', 'AGRIC', 'Agric', 'science', 'general', False, True, True, 40, 60, False, False, False, True, True),
            ('Business Studies', 'BUS', 'Business', 'commercial', 'general', False, True, False, 40, 60, False, False, False, True, False),
            ('Music', 'MUS', 'Music', 'arts', 'general', False, True, True, 40, 60, False, False, False, True, True),
            ('Fine Arts', 'FART', 'Fine Arts', 'arts', 'general', False, True, True, 40, 60, False, False, False, True, True),
            ('History', 'HIST', 'History', 'arts', 'general', False, True, False, 40, 60, False, False, True, True, True),
            
            # SSS SCIENCE STREAM (6 subjects)
            ('Biology', 'BIO', 'Biology', 'science', 'science', False, True, True, 40, 60, False, False, False, False, True),
            ('Chemistry', 'CHEM', 'Chemistry', 'science', 'science', False, True, True, 40, 60, False, False, False, False, True),
            ('Physics', 'PHY', 'Physics', 'science', 'science', False, True, True, 40, 60, False, False, False, False, True),
            ('Further Mathematics', 'FMATH', 'Further Maths', 'science', 'science', False, True, False, 40, 60, False, False, False, False, True),
            ('Technical Drawing', 'TD', 'Tech Draw', 'technical', 'science', False, True, True, 40, 60, False, False, False, False, True),
            ('Health Science', 'HSCI', 'Health Sci', 'science', 'science', False, True, False, 40, 60, False, False, False, False, True),
            
            # SSS COMMERCIAL STREAM (8 subjects)
            ('Financial Accounting', 'FACC', 'Accounting', 'commercial', 'commercial', False, True, False, 40, 60, False, False, False, False, True),
            ('Commerce', 'COM', 'Commerce', 'commercial', 'commercial', False, True, False, 40, 60, False, False, False, False, True),
            ('Economics', 'ECON', 'Economics', 'commercial', 'commercial', False, True, False, 40, 60, False, False, False, False, True),
            ('Book Keeping', 'BKPG', 'Book Keep', 'commercial', 'commercial', False, True, False, 40, 60, False, False, False, False, True),
            ('Office Practice', 'OFPRAC', 'Office Prac', 'commercial', 'commercial', False, True, False, 40, 60, False, False, False, False, True),
            ('Typewriting', 'TYPE', 'Typing', 'commercial', 'commercial', False, True, True, 40, 60, False, False, False, False, True),
            ('Marketing', 'MRKT', 'Marketing', 'commercial', 'commercial', False, True, False, 40, 60, False, False, False, False, True),
            ('Data Processing', 'DPROC', 'Data Proc', 'technical', 'commercial', False, True, True, 40, 60, False, False, False, False, True),
            
            # SSS ARTS STREAM (6 subjects)
            ('Literature in English', 'LIT', 'Literature', 'arts', 'arts', False, True, False, 40, 60, False, False, False, False, True),
            ('Government', 'GOV', 'Government', 'arts', 'arts', False, True, False, 40, 60, False, False, False, False, True),
            ('Geography', 'GEO', 'Geography', 'arts', 'arts', False, True, False, 40, 60, False, False, False, False, True),
            ('Tourism', 'TOUR', 'Tourism', 'arts', 'arts', False, True, False, 40, 60, False, False, False, False, True),
            ('Photography', 'PHOT', 'Photography', 'arts', 'arts', False, True, True, 40, 60, False, False, False, False, True),
            ('Catering Craft Practice', 'CCP', 'Catering', 'vocational', 'arts', False, True, True, 40, 60, False, False, False, False, True),
        ]
        
        # Format: name, code, short_name, subject_type, stream, is_compulsory, is_examinable, has_practical, 
        #         ca_weight, exam_weight, creche, nursery, primary, jss, sss
        
        for subj_data in subjects:
            name, code, short_name, subj_type, stream, compulsory, examinable, practical, ca, exam, creche, nursery, primary, jss, sss = subj_data
            
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name, 'short_name': short_name, 'subject_type': subj_type,
                    'stream': stream, 'is_compulsory': compulsory, 'is_examinable': examinable,
                    'has_practical': practical, 'ca_weight': ca, 'exam_weight': exam,
                    'available_for_creche': creche, 'available_for_nursery': nursery,
                    'available_for_primary': primary, 'available_for_jss': jss,
                    'available_for_sss': sss, 'is_active': True, 'total_marks': 100, 'pass_mark': 40
                }
            )
            if created:
                self.stdout.write(f"  ✓ Created: {subject.name} ({subject.code})")
            else:
                self.stdout.write(f"  - Exists: {subject.name} ({subject.code})")
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n📊 SUMMARY:'))
        self.stdout.write(f'  Total Subjects: {Subject.objects.count()}')
        self.stdout.write(f'  Creche: {Subject.objects.filter(available_for_creche=True).count()}')
        self.stdout.write(f'  Nursery: {Subject.objects.filter(available_for_nursery=True).count()}')
        self.stdout.write(f'  Primary: {Subject.objects.filter(available_for_primary=True).count()}')
        self.stdout.write(f'  JSS: {Subject.objects.filter(available_for_jss=True).count()}')
        self.stdout.write(f'  SSS: {Subject.objects.filter(available_for_sss=True).count()}')