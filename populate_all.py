"""
Complete Data Population Script - Academic Structure + Subjects
Run from your project root with:
    python populate_all.py
"""

import os
import sys
import django

# ============================================================
# SET DATABASE URL BEFORE DJANGO SETUP
# ============================================================
os.environ['DATABASE_URL'] = (
    'postgresql://postgres.lwpfwoinswxxqbhgzrde:ConcordTS2025Secure99'
    '@aws-1-eu-north-1.pooler.supabase.com:6543/postgres'
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# ============================================================
# NOW IMPORT MODELS
# ============================================================
from datetime import datetime
from academic.models import Program, ClassLevel, Subject, AcademicSession, AcademicTerm


# ============================================================
# PART 1: ACADEMIC STRUCTURE
# ============================================================
def populate_academic_structure():
    print("=" * 60)
    print("PART 1: POPULATING NIGERIAN ACADEMIC STRUCTURE")
    print("=" * 60)

    # --- Programs ---
    print("\n📚 CREATING PROGRAMS...")
    programs_data = [
        {'name': 'Creche',                    'program_type': 'creche',            'code': 'CR',  'duration_years': 2, 'description': 'Early childhood education for ages 0-2 years',               'is_active': True},
        {'name': 'Nursery',                   'program_type': 'nursery',           'code': 'NUR', 'duration_years': 2, 'description': 'Pre-primary education for ages 3-5 years',                   'is_active': True},
        {'name': 'Primary School',            'program_type': 'primary',           'code': 'PRI', 'duration_years': 6, 'description': 'Basic education for ages 6-11 years (Primary 1-6)',          'is_active': True},
        {'name': 'Junior Secondary School',   'program_type': 'junior_secondary',  'code': 'JSS', 'duration_years': 3, 'description': 'Lower secondary education for ages 12-14 years (JSS 1-3)',  'is_active': True},
        {'name': 'Senior Secondary School',   'program_type': 'senior_secondary',  'code': 'SSS', 'duration_years': 3, 'description': 'Upper secondary education for ages 15-17 years (SSS 1-3)', 'is_active': True},
    ]

    program_objs = {}
    for pd in programs_data:
        program, created = Program.objects.get_or_create(code=pd['code'], defaults=pd)
        program_objs[pd['program_type']] = program
        print(f"  {'✅ CREATED' if created else '📝 EXISTS'}: {program.name} ({program.code})")

    # --- Class Levels ---
    print("\n🏫 CREATING CLASS LEVELS...")
    class_levels = [
        # Creche
        {'program': 'creche',           'level': 'creche',      'name': 'Creche',         'code': 'CR',   'order': 1,  'min_age': 0,  'max_age': 2,  'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        # Nursery
        {'program': 'nursery',          'level': 'nursery_1',   'name': 'Nursery 1',      'code': 'NUR1', 'order': 2,  'min_age': 3,  'max_age': 4,  'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'nursery',          'level': 'nursery_2',   'name': 'Nursery 2',      'code': 'NUR2', 'order': 3,  'min_age': 4,  'max_age': 5,  'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'nursery',          'level': 'kg_1',        'name': 'Kindergarten 1', 'code': 'KG1',  'order': 4,  'min_age': 5,  'max_age': 6,  'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'nursery',          'level': 'kg_2',        'name': 'Kindergarten 2', 'code': 'KG2',  'order': 5,  'min_age': 6,  'max_age': 7,  'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        # Primary
        {'program': 'primary',          'level': 'primary_1',   'name': 'Primary 1',      'code': 'PRI1', 'order': 6,  'min_age': 7,  'max_age': 8,  'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'primary',          'level': 'primary_2',   'name': 'Primary 2',      'code': 'PRI2', 'order': 7,  'min_age': 8,  'max_age': 9,  'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'primary',          'level': 'primary_3',   'name': 'Primary 3',      'code': 'PRI3', 'order': 8,  'min_age': 9,  'max_age': 10, 'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'primary',          'level': 'primary_4',   'name': 'Primary 4',      'code': 'PRI4', 'order': 9,  'min_age': 10, 'max_age': 11, 'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'primary',          'level': 'primary_5',   'name': 'Primary 5',      'code': 'PRI5', 'order': 10, 'min_age': 11, 'max_age': 12, 'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'primary',          'level': 'primary_6',   'name': 'Primary 6',      'code': 'PRI6', 'order': 11, 'min_age': 12, 'max_age': 13, 'has_common_entrance': True,  'has_bece': False, 'has_waec_neco': False},
        # JSS
        {'program': 'junior_secondary', 'level': 'jss_1',       'name': 'JSS 1',          'code': 'JSS1', 'order': 12, 'min_age': 13, 'max_age': 14, 'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'junior_secondary', 'level': 'jss_2',       'name': 'JSS 2',          'code': 'JSS2', 'order': 13, 'min_age': 14, 'max_age': 15, 'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'junior_secondary', 'level': 'jss_3',       'name': 'JSS 3',          'code': 'JSS3', 'order': 14, 'min_age': 15, 'max_age': 16, 'has_common_entrance': False, 'has_bece': True,  'has_waec_neco': False},
        # SSS
        {'program': 'senior_secondary', 'level': 'sss_1',       'name': 'SSS 1',          'code': 'SSS1', 'order': 15, 'min_age': 16, 'max_age': 17, 'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'senior_secondary', 'level': 'sss_2',       'name': 'SSS 2',          'code': 'SSS2', 'order': 16, 'min_age': 17, 'max_age': 18, 'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': False},
        {'program': 'senior_secondary', 'level': 'sss_3',       'name': 'SSS 3',          'code': 'SSS3', 'order': 17, 'min_age': 18, 'max_age': 19, 'has_common_entrance': False, 'has_bece': False, 'has_waec_neco': True },
    ]

    for cl in class_levels:
        program = program_objs[cl['program']]
        obj, created = ClassLevel.objects.get_or_create(
            program=program,
            level=cl['level'],
            defaults={
                'name': cl['name'], 'code': cl['code'], 'order': cl['order'],
                'min_age': cl['min_age'], 'max_age': cl['max_age'], 'is_active': True,
                'has_common_entrance': cl['has_common_entrance'],
                'has_bece': cl['has_bece'], 'has_waec_neco': cl['has_waec_neco'],
            }
        )
        print(f"  {'✅ CREATED' if created else '📝 EXISTS'}: {obj.name} ({obj.code})")

    # --- Academic Sessions ---
    print("\n📅 CREATING ACADEMIC SESSIONS...")
    sessions_data = [
        {'name': '2023/2024 Academic Session', 'start_date': datetime(2023, 9, 2).date(),  'end_date': datetime(2024, 7, 18).date(), 'is_current': False, 'status': 'completed', 'description': 'Completed academic session'},
        {'name': '2024/2025 Academic Session', 'start_date': datetime(2024, 9, 2).date(),  'end_date': datetime(2025, 7, 18).date(), 'is_current': True,  'status': 'active',    'description': 'Current academic session'},
        {'name': '2025/2026 Academic Session', 'start_date': datetime(2025, 9, 1).date(),  'end_date': datetime(2026, 7, 17).date(), 'is_current': False, 'status': 'upcoming',  'description': 'Upcoming academic session'},
    ]

    for sd in sessions_data:
        session, created = AcademicSession.objects.get_or_create(name=sd['name'], defaults=sd)
        print(f"  {'✅ CREATED' if created else '📝 EXISTS'}: {session.name} ({session.status})")

    # --- Academic Terms ---
    print("\n📚 CREATING ACADEMIC TERMS...")
    current_session = AcademicSession.objects.get(is_current=True)
    terms_data = [
        {
            'session': current_session, 'term': 'first',  'name': 'First Term 2024/2025',
            'start_date': datetime(2024, 9, 2).date(),   'end_date': datetime(2024, 12, 13).date(),
            'is_current': False, 'status': 'completed',
            'resumption_date': datetime(2024, 9, 2).date(), 'vacation_date': datetime(2024, 12, 13).date(),
            'total_school_days': 65, 'total_teaching_weeks': 13,
            'mid_term_break_start': datetime(2024, 10, 14).date(), 'mid_term_break_end': datetime(2024, 10, 18).date(),
        },
        {
            'session': current_session, 'term': 'second', 'name': 'Second Term 2024/2025',
            'start_date': datetime(2025, 1, 6).date(),   'end_date': datetime(2025, 4, 4).date(),
            'is_current': True,  'status': 'active',
            'resumption_date': datetime(2025, 1, 6).date(), 'vacation_date': datetime(2025, 4, 4).date(),
            'total_school_days': 60, 'total_teaching_weeks': 12,
            'mid_term_break_start': datetime(2025, 2, 17).date(), 'mid_term_break_end': datetime(2025, 2, 21).date(),
        },
        {
            'session': current_session, 'term': 'third',  'name': 'Third Term 2024/2025',
            'start_date': datetime(2025, 4, 28).date(),  'end_date': datetime(2025, 7, 18).date(),
            'is_current': False, 'status': 'upcoming',
            'resumption_date': datetime(2025, 4, 28).date(), 'vacation_date': datetime(2025, 7, 18).date(),
            'total_school_days': 55, 'total_teaching_weeks': 11,
            'mid_term_break_start': datetime(2025, 6, 2).date(), 'mid_term_break_end': datetime(2025, 6, 6).date(),
        },
    ]

    for td in terms_data:
        term, created = AcademicTerm.objects.get_or_create(
            session=td['session'], term=td['term'], defaults=td
        )
        print(f"  {'✅ CREATED' if created else '📝 EXISTS'}: {term.name} ({term.status})")

    print(f"\n✅ ACADEMIC STRUCTURE DONE!")
    print(f"   Programs: {Program.objects.count()}")
    print(f"   Class Levels: {ClassLevel.objects.count()}")
    print(f"   Sessions: {AcademicSession.objects.count()}")
    print(f"   Terms: {AcademicTerm.objects.count()}")


# ============================================================
# PART 2: SUBJECTS
# ============================================================
def populate_subjects():
    print("\n" + "=" * 60)
    print("PART 2: POPULATING NIGERIAN SUBJECTS")
    print("=" * 60)

    subjects_data = [
        # CRECHE
        {'name': 'Rhymes and Songs',            'code': 'RHS',  'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_creche': True,  'pass_mark': 30, 'ca_weight': 40, 'exam_weight': 60},
        {'name': 'Play Activities',             'code': 'PLA',  'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_creche': True,  'pass_mark': 30},
        {'name': 'Colours Recognition',         'code': 'COL',  'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_creche': True,  'pass_mark': 30},
        {'name': 'Number Work (Creche)',         'code': 'NUMC', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_creche': True,  'pass_mark': 30},
        # NURSERY
        {'name': 'English Language (Nursery)',   'code': 'ENGN', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_nursery': True, 'pass_mark': 40},
        {'name': 'Mathematics (Nursery)',        'code': 'MATN', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_nursery': True, 'pass_mark': 40},
        {'name': 'Phonics',                      'code': 'PHO',  'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_nursery': True, 'pass_mark': 40},
        {'name': 'Writing',                      'code': 'WRI',  'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_nursery': True, 'pass_mark': 40},
        {'name': 'Colouring',                    'code': 'CLR',  'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_nursery': True, 'pass_mark': 40},
        {'name': 'Health Habits',                'code': 'HLH',  'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_nursery': True, 'pass_mark': 40},
        {'name': 'Rhymes (Nursery)',              'code': 'RHYN', 'subject_type': 'pre_school', 'stream': 'pre_school', 'is_compulsory': True,  'available_for_nursery': True, 'pass_mark': 40},
        # PRIMARY CORE
        {'name': 'English Language',             'code': 'ENG',  'subject_type': 'core',       'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Mathematics',                  'code': 'MAT',  'subject_type': 'core',       'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Quantitative Reasoning',       'code': 'QUA',  'subject_type': 'core',       'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'pass_mark': 40},
        {'name': 'Verbal Reasoning',             'code': 'VER',  'subject_type': 'core',       'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'pass_mark': 40},
        # SCIENCE
        {'name': 'Basic Science',                'code': 'BSC',  'subject_type': 'science',    'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        {'name': 'Basic Technology',             'code': 'BTE',  'subject_type': 'technical',  'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        # SOCIAL
        {'name': 'Social Studies',               'code': 'SOS',  'subject_type': 'arts',       'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        {'name': 'Civic Education',              'code': 'CIV',  'subject_type': 'arts',       'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        {'name': 'History',                      'code': 'HIS',  'subject_type': 'arts',       'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        # RELIGIOUS
        {'name': 'Christian Religious Studies',  'code': 'CRS',  'subject_type': 'religious',  'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Islamic Religious Studies',    'code': 'IRS',  'subject_type': 'religious',  'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Bible Knowledge',              'code': 'BKN',  'subject_type': 'religious',  'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'pass_mark': 40},
        {'name': 'Quran',                        'code': 'QUR',  'subject_type': 'religious',  'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'pass_mark': 40},
        # PHE
        {'name': 'Physical and Health Education','code': 'PHE',  'subject_type': 'core',       'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        # COMPUTER
        {'name': 'Computer Studies',             'code': 'COM',  'subject_type': 'technical',  'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Robotics',                     'code': 'ROB',  'subject_type': 'technical',  'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        # VOCATIONAL
        {'name': 'Home Economics',               'code': 'HEC',  'subject_type': 'vocational', 'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        {'name': 'Practical Vocational Studies (PVS)', 'code': 'PVS', 'subject_type': 'vocational', 'stream': 'general', 'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        # ARTS
        {'name': 'Cultural and Creative Arts',   'code': 'CCA',  'subject_type': 'arts',       'stream': 'general',    'is_compulsory': True,  'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        {'name': 'Music',                        'code': 'MUS',  'subject_type': 'arts',       'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'pass_mark': 40},
        {'name': 'Fine Arts',                    'code': 'FAR',  'subject_type': 'arts',       'stream': 'general',    'is_compulsory': False, 'available_for_jss': True,     'pass_mark': 40},
        # LANGUAGES
        {'name': 'Yoruba Language',              'code': 'YOR',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Igbo Language',                'code': 'IGB',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Hausa Language',               'code': 'HAU',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'French Language',              'code': 'FRE',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Arabic',                       'code': 'ARA',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        # ENGLISH SKILLS
        {'name': 'Diction',                      'code': 'DIC',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'pass_mark': 40},
        {'name': 'Writing Skills',               'code': 'WRS',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'pass_mark': 40},
        {'name': 'Spelling',                     'code': 'SPE',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'pass_mark': 40},
        {'name': 'Handwriting',                  'code': 'HAN',  'subject_type': 'language',   'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'pass_mark': 40},
        # AGRIC
        {'name': 'Agricultural Science',         'code': 'AGR',  'subject_type': 'science',    'stream': 'general',    'is_compulsory': False, 'available_for_primary': True, 'available_for_jss': True, 'available_for_sss': True, 'pass_mark': 40},
        # JSS
        {'name': 'Business Studies',             'code': 'BUS',  'subject_type': 'commercial', 'stream': 'general',    'is_compulsory': True,  'available_for_jss': True,     'pass_mark': 40},
        # SSS SCIENCE
        {'name': 'Physics',                      'code': 'PHY',  'subject_type': 'science',    'stream': 'science',    'is_compulsory': True,  'available_for_sss': True, 'has_practical': True,  'pass_mark': 40},
        {'name': 'Chemistry',                    'code': 'CHE',  'subject_type': 'science',    'stream': 'science',    'is_compulsory': True,  'available_for_sss': True, 'has_practical': True,  'pass_mark': 40},
        {'name': 'Biology',                      'code': 'BIO',  'subject_type': 'science',    'stream': 'science',    'is_compulsory': True,  'available_for_sss': True, 'has_practical': True,  'pass_mark': 40},
        {'name': 'Further Mathematics',          'code': 'FMA',  'subject_type': 'science',    'stream': 'science',    'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Technical Drawing',            'code': 'TED',  'subject_type': 'technical',  'stream': 'science',    'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        # SSS COMMERCIAL
        {'name': 'Financial Accounting',         'code': 'ACC',  'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': True,  'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Commerce',                     'code': 'CMR',  'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': True,  'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Economics',                    'code': 'ECO',  'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': True,  'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Book Keeping',                 'code': 'BKP',  'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Office Practice',              'code': 'OFP',  'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Marketing',                    'code': 'MKT',  'subject_type': 'commercial', 'stream': 'commercial', 'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        # SSS ARTS
        {'name': 'Literature in English',        'code': 'LIT',  'subject_type': 'arts',       'stream': 'arts',       'is_compulsory': True,  'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Government',                   'code': 'GOV',  'subject_type': 'arts',       'stream': 'arts',       'is_compulsory': True,  'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Geography',                    'code': 'GEO',  'subject_type': 'arts',       'stream': 'arts',       'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Visual Arts',                  'code': 'VIA',  'subject_type': 'arts',       'stream': 'arts',       'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Drama',                        'code': 'DRA',  'subject_type': 'arts',       'stream': 'arts',       'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        # SSS GENERAL
        {'name': 'Data Processing',              'code': 'DAP',  'subject_type': 'technical',  'stream': 'general',    'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
        {'name': 'Food and Nutrition',           'code': 'FNU',  'subject_type': 'vocational', 'stream': 'general',    'is_compulsory': False, 'available_for_sss': True, 'pass_mark': 40},
    ]

    created_count = 0
    updated_count = 0

    for sd in subjects_data:
        subject, created = Subject.objects.update_or_create(code=sd['code'], defaults=sd)
        if created:
            created_count += 1
            print(f"  ✅ CREATED: {subject.name} ({subject.code})")
        else:
            updated_count += 1
            print(f"  📝 UPDATED: {subject.name} ({subject.code})")

    print(f"\n✅ SUBJECTS DONE!")
    print(f"   Created: {created_count}")
    print(f"   Updated: {updated_count}")
    print(f"   Total:   {Subject.objects.count()}")


# ============================================================
# RUN EVERYTHING
# ============================================================
if __name__ == '__main__':
    try:
        populate_academic_structure()
        populate_subjects()
        print("\n" + "=" * 60)
        print("🎉 ALL DATA POPULATED SUCCESSFULLY!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()