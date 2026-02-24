"""
Complete Academic Data Population Script
Populates all academic data: Programs, Class Levels, Academic Sessions, Terms
"""

import os
import django
import sys
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from academic.models import Program, ClassLevel, Subject, AcademicSession, AcademicTerm
from django.contrib.auth import get_user_model

def create_nigerian_academic_structure():
    """Create complete Nigerian academic structure"""
    
    print("=" * 60)
    print("POPULATING NIGERIAN ACADEMIC STRUCTURE")
    print("=" * 60)
    
    # Create Programs
    print("\n📚 CREATING PROGRAMS...")
    programs = [
        {
            'name': 'Creche', 
            'program_type': 'creche', 
            'code': 'CR', 
            'duration_years': 2,
            'description': 'Early childhood education for ages 0-2 years',
            'is_active': True
        },
        {
            'name': 'Nursery', 
            'program_type': 'nursery', 
            'code': 'NUR', 
            'duration_years': 2,
            'description': 'Pre-primary education for ages 3-5 years',
            'is_active': True
        },
        {
            'name': 'Primary School', 
            'program_type': 'primary', 
            'code': 'PRI', 
            'duration_years': 6,
            'description': 'Basic education for ages 6-11 years (Primary 1-6)',
            'is_active': True
        },
        {
            'name': 'Junior Secondary School', 
            'program_type': 'junior_secondary', 
            'code': 'JSS', 
            'duration_years': 3,
            'description': 'Lower secondary education for ages 12-14 years (JSS 1-3)',
            'is_active': True
        },
        {
            'name': 'Senior Secondary School', 
            'program_type': 'senior_secondary', 
            'code': 'SSS', 
            'duration_years': 3,
            'description': 'Upper secondary education for ages 15-17 years (SSS 1-3)',
            'is_active': True
        },
    ]
    
    program_objs = {}
    for prog_data in programs:
        program, created = Program.objects.get_or_create(
            code=prog_data['code'],
            defaults=prog_data
        )
        program_objs[prog_data['program_type']] = program
        status = "✅ CREATED" if created else "📝 UPDATED"
        print(f"  {status}: {program.name} ({program.code})")
    
    # Create Class Levels
    print("\n🏫 CREATING CLASS LEVELS...")
    class_levels = [
        # Creche
        {
            'program': 'creche', 
            'level': 'creche', 
            'name': 'Creche', 
            'code': 'CR', 
            'order': 1,
            'min_age': 0,
            'max_age': 2,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        
        # Nursery
        {
            'program': 'nursery', 
            'level': 'nursery_1', 
            'name': 'Nursery 1', 
            'code': 'NUR1', 
            'order': 2,
            'min_age': 3,
            'max_age': 4,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'nursery', 
            'level': 'nursery_2', 
            'name': 'Nursery 2', 
            'code': 'NUR2', 
            'order': 3,
            'min_age': 4,
            'max_age': 5,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'nursery', 
            'level': 'kg_1', 
            'name': 'Kindergarten 1', 
            'code': 'KG1', 
            'order': 4,
            'min_age': 5,
            'max_age': 6,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'nursery', 
            'level': 'kg_2', 
            'name': 'Kindergarten 2', 
            'code': 'KG2', 
            'order': 5,
            'min_age': 6,
            'max_age': 7,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        
        # Primary
        {
            'program': 'primary', 
            'level': 'primary_1', 
            'name': 'Primary 1', 
            'code': 'PRI1', 
            'order': 6,
            'min_age': 7,
            'max_age': 8,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'primary', 
            'level': 'primary_2', 
            'name': 'Primary 2', 
            'code': 'PRI2', 
            'order': 7,
            'min_age': 8,
            'max_age': 9,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'primary', 
            'level': 'primary_3', 
            'name': 'Primary 3', 
            'code': 'PRI3', 
            'order': 8,
            'min_age': 9,
            'max_age': 10,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'primary', 
            'level': 'primary_4', 
            'name': 'Primary 4', 
            'code': 'PRI4', 
            'order': 9,
            'min_age': 10,
            'max_age': 11,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'primary', 
            'level': 'primary_5', 
            'name': 'Primary 5', 
            'code': 'PRI5', 
            'order': 10,
            'min_age': 11,
            'max_age': 12,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'primary', 
            'level': 'primary_6', 
            'name': 'Primary 6', 
            'code': 'PRI6', 
            'order': 11,
            'min_age': 12,
            'max_age': 13,
            'is_active': True,
            'has_common_entrance': True,
            'has_bece': False,
            'has_waec_neco': False
        },
        
        # Junior Secondary
        {
            'program': 'junior_secondary', 
            'level': 'jss_1', 
            'name': 'JSS 1', 
            'code': 'JSS1', 
            'order': 12,
            'min_age': 13,
            'max_age': 14,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'junior_secondary', 
            'level': 'jss_2', 
            'name': 'JSS 2', 
            'code': 'JSS2', 
            'order': 13,
            'min_age': 14,
            'max_age': 15,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'junior_secondary', 
            'level': 'jss_3', 
            'name': 'JSS 3', 
            'code': 'JSS3', 
            'order': 14,
            'min_age': 15,
            'max_age': 16,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': True,
            'has_waec_neco': False
        },
        
        # Senior Secondary
        {
            'program': 'senior_secondary', 
            'level': 'sss_1', 
            'name': 'SSS 1', 
            'code': 'SSS1', 
            'order': 15,
            'min_age': 16,
            'max_age': 17,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'senior_secondary', 
            'level': 'sss_2', 
            'name': 'SSS 2', 
            'code': 'SSS2', 
            'order': 16,
            'min_age': 17,
            'max_age': 18,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': False
        },
        {
            'program': 'senior_secondary', 
            'level': 'sss_3', 
            'name': 'SSS 3', 
            'code': 'SSS3', 
            'order': 17,
            'min_age': 18,
            'max_age': 19,
            'is_active': True,
            'has_common_entrance': False,
            'has_bece': False,
            'has_waec_neco': True
        },
    ]
    
    class_level_count = 0
    for cl_data in class_levels:
        program = program_objs[cl_data['program']]
        class_level, created = ClassLevel.objects.get_or_create(
            program=program,
            level=cl_data['level'],
            defaults={
                'name': cl_data['name'],
                'code': cl_data['code'],
                'order': cl_data['order'],
                'min_age': cl_data['min_age'],
                'max_age': cl_data['max_age'],
                'is_active': cl_data['is_active'],
                'has_common_entrance': cl_data['has_common_entrance'],
                'has_bece': cl_data['has_bece'],
                'has_waec_neco': cl_data['has_waec_neco']
            }
        )
        class_level_count += 1
        status = "✅ CREATED" if created else "📝 UPDATED"
        print(f"  {status}: {class_level.name} ({class_level.code})")
    
    # Create Academic Sessions
    print("\n📅 CREATING ACADEMIC SESSIONS...")
    today = datetime.now().date()
    
    sessions_data = [
        {
            'name': '2023/2024 Academic Session',
            'start_date': datetime(2023, 9, 2).date(),
            'end_date': datetime(2024, 7, 18).date(),
            'is_current': False,
            'status': 'completed',
            'description': 'Completed academic session'
        },
        {
            'name': '2024/2025 Academic Session',
            'start_date': datetime(2024, 9, 2).date(),
            'end_date': datetime(2025, 7, 18).date(),
            'is_current': True,
            'status': 'active',
            'description': 'Current academic session'
        },
        {
            'name': '2025/2026 Academic Session',
            'start_date': datetime(2025, 9, 1).date(),
            'end_date': datetime(2026, 7, 17).date(),
            'is_current': False,
            'status': 'upcoming',
            'description': 'Upcoming academic session'
        }
    ]
    
    for session_data in sessions_data:
        session, created = AcademicSession.objects.get_or_create(
            name=session_data['name'],
            defaults=session_data
        )
        status = "✅ CREATED" if created else "📝 UPDATED"
        print(f"  {status}: {session.name} ({session.status})")
    
    # Create Academic Terms for current session
    print("\n📚 CREATING ACADEMIC TERMS...")
    current_session = AcademicSession.objects.get(is_current=True)
    
    terms_data = [
        {
            'session': current_session,
            'term': 'first',
            'name': 'First Term 2024/2025',
            'start_date': datetime(2024, 9, 2).date(),
            'end_date': datetime(2024, 12, 13).date(),
            'is_current': False,
            'status': 'completed',
            'resumption_date': datetime(2024, 9, 2).date(),
            'vacation_date': datetime(2024, 12, 13).date(),
            'total_school_days': 65,
            'total_teaching_weeks': 13,
            'mid_term_break_start': datetime(2024, 10, 14).date(),
            'mid_term_break_end': datetime(2024, 10, 18).date()
        },
        {
            'session': current_session,
            'term': 'second',
            'name': 'Second Term 2024/2025',
            'start_date': datetime(2025, 1, 6).date(),
            'end_date': datetime(2025, 4, 4).date(),
            'is_current': True,
            'status': 'active',
            'resumption_date': datetime(2025, 1, 6).date(),
            'vacation_date': datetime(2025, 4, 4).date(),
            'total_school_days': 60,
            'total_teaching_weeks': 12,
            'mid_term_break_start': datetime(2025, 2, 17).date(),
            'mid_term_break_end': datetime(2025, 2, 21).date()
        },
        {
            'session': current_session,
            'term': 'third',
            'name': 'Third Term 2024/2025',
            'start_date': datetime(2025, 4, 28).date(),
            'end_date': datetime(2025, 7, 18).date(),
            'is_current': False,
            'status': 'upcoming',
            'resumption_date': datetime(2025, 4, 28).date(),
            'vacation_date': datetime(2025, 7, 18).date(),
            'total_school_days': 55,
            'total_teaching_weeks': 11,
            'mid_term_break_start': datetime(2025, 6, 2).date(),
            'mid_term_break_end': datetime(2025, 6, 6).date()
        }
    ]
    
    for term_data in terms_data:
        term, created = AcademicTerm.objects.get_or_create(
            session=term_data['session'],
            term=term_data['term'],
            defaults=term_data
        )
        status = "✅ CREATED" if created else "📝 UPDATED"
        print(f"  {status}: {term.name} ({term.status})")
    
    print("\n" + "=" * 60)
    print("📊 POPULATION SUMMARY:")
    print("=" * 60)
    print(f"  Programs: {len(program_objs)}")
    print(f"  Class levels: {class_level_count}")
    print(f"  Academic sessions: {AcademicSession.objects.count()}")
    print(f"  Academic terms: {AcademicTerm.objects.count()}")
    
    # Display structure
    print("\n" + "=" * 60)
    print("🏫 NIGERIAN ACADEMIC STRUCTURE:")
    print("=" * 60)
    for program_type, program in program_objs.items():
        class_levels = ClassLevel.objects.filter(program=program, is_active=True)
        print(f"\n  {program.name} ({program.code}):")
        for cl in class_levels:
            exam_info = []
            if cl.has_common_entrance:
                exam_info.append("Common Entrance")
            if cl.has_bece:
                exam_info.append("BECE")
            if cl.has_waec_neco:
                exam_info.append("WAEC/NECO")
            
            exam_text = f" [Exams: {', '.join(exam_info)}]" if exam_info else ""
            print(f"    • {cl.name} (Age: {cl.min_age}-{cl.max_age}){exam_text}")
    
    print("\n" + "=" * 60)
    print("✅ ACADEMIC DATA POPULATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("  1. Run 'python backend/populate_subjects.py' to populate Nigerian subjects")
    print("  2. Start Django server: 'python manage.py runserver'")
    print("  3. Access the academic API at: http://localhost:8000/api/academic/")

if __name__ == '__main__':
    create_nigerian_academic_structure()