"""
Complete Nigerian Subjects Data Population Script
All subjects for Creche, Nursery, KG, Primary, JSS, and SSS
With proper class-level and stream assignments
"""

from academic.models import Subject

def populate_nigerian_subjects():
    """Populate all Nigerian school subjects with proper class assignments"""
    
    subjects_data = [
        # ============================================
        # CRECHE SUBJECTS (Age 0-2)
        # ============================================
        {
            'name': 'Rhymes and Songs',
            'code': 'RHS',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_creche': True,
            'pass_mark': 30,
            'ca_weight': 40,
            'exam_weight': 60,
        },
        {
            'name': 'Play Activities',
            'code': 'PLA',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_creche': True,
            'pass_mark': 30,
        },
        {
            'name': 'Colours Recognition',
            'code': 'COL',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_creche': True,
            'pass_mark': 30,
        },
        {
            'name': 'Number Work (Creche)',
            'code': 'NUMC',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_creche': True,
            'pass_mark': 30,
        },
        
        # ============================================
        # NURSERY & KINDERGARTEN SUBJECTS
        # ============================================
        {
            'name': 'English Language (Nursery)',
            'code': 'ENGN',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_nursery': True,
            'pass_mark': 40,
        },
        {
            'name': 'Mathematics (Nursery)',
            'code': 'MATN',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_nursery': True,
            'pass_mark': 40,
        },
        {
            'name': 'Phonics',
            'code': 'PHO',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_nursery': True,
            'pass_mark': 40,
        },
        {
            'name': 'Writing',
            'code': 'WRI',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_nursery': True,
            'pass_mark': 40,
        },
        {
            'name': 'Colouring',
            'code': 'CLR',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_nursery': True,
            'pass_mark': 40,
        },
        {
            'name': 'Health Habits',
            'code': 'HLH',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_nursery': True,
            'pass_mark': 40,
        },
        {
            'name': 'Rhymes (Nursery)',
            'code': 'RHYN',
            'subject_type': 'pre_school',
            'stream': 'pre_school',
            'is_compulsory': True,
            'available_for_nursery': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # PRIMARY SCHOOL CORE SUBJECTS
        # ============================================
        {
            'name': 'English Language',
            'code': 'ENG',
            'subject_type': 'core',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Mathematics',
            'code': 'MAT',
            'subject_type': 'core',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Quantitative Reasoning',
            'code': 'QUA',
            'subject_type': 'core',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'pass_mark': 40,
        },
        {
            'name': 'Verbal Reasoning',
            'code': 'VER',
            'subject_type': 'core',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # PRIMARY SCHOOL SCIENCE SUBJECTS
        # ============================================
        {
            'name': 'Basic Science',
            'code': 'BSC',
            'subject_type': 'science',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Basic Technology',
            'code': 'BTE',
            'subject_type': 'technical',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # PRIMARY SOCIAL STUDIES & CIVICS
        # ============================================
        {
            'name': 'Social Studies',
            'code': 'SOS',
            'subject_type': 'arts',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Civic Education',
            'code': 'CIV',
            'subject_type': 'arts',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        {
            'name': 'History',
            'code': 'HIS',
            'subject_type': 'arts',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # RELIGIOUS STUDIES
        # ============================================
        {
            'name': 'Christian Religious Studies',
            'code': 'CRS',
            'subject_type': 'religious',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Islamic Religious Studies',
            'code': 'IRS',
            'subject_type': 'religious',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Bible Knowledge',
            'code': 'BKN',
            'subject_type': 'religious',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'pass_mark': 40,
        },
        {
            'name': 'Quran',
            'code': 'QUR',
            'subject_type': 'religious',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # PHYSICAL & HEALTH EDUCATION
        # ============================================
        {
            'name': 'Physical and Health Education',
            'code': 'PHE',
            'subject_type': 'core',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # COMPUTER & TECHNOLOGY
        # ============================================
        {
            'name': 'Computer Studies',
            'code': 'COM',
            'subject_type': 'technical',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Robotics',
            'code': 'ROB',
            'subject_type': 'technical',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # VOCATIONAL & PRACTICAL SUBJECTS
        # ============================================
        {
            'name': 'Home Economics',
            'code': 'HEC',
            'subject_type': 'vocational',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Practical Vocational Studies (PVS)',
            'code': 'PVS',
            'subject_type': 'vocational',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # ARTS & CREATIVE SUBJECTS
        # ============================================
        {
            'name': 'Cultural and Creative Arts',
            'code': 'CCA',
            'subject_type': 'arts',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Music',
            'code': 'MUS',
            'subject_type': 'arts',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Fine Arts',
            'code': 'FAR',
            'subject_type': 'arts',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # NIGERIAN LANGUAGES
        # ============================================
        {
            'name': 'Yoruba Language',
            'code': 'YOR',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Igbo Language',
            'code': 'IGB',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Hausa Language',
            'code': 'HAU',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'French Language',
            'code': 'FRE',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Arabic',
            'code': 'ARA',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # ENGLISH LANGUAGE SKILLS
        # ============================================
        {
            'name': 'Diction',
            'code': 'DIC',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'pass_mark': 40,
        },
        {
            'name': 'Writing Skills',
            'code': 'WRS',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'pass_mark': 40,
        },
        {
            'name': 'Spelling',
            'code': 'SPE',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'pass_mark': 40,
        },
        {
            'name': 'Handwriting',
            'code': 'HAN',
            'subject_type': 'language',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # AGRICULTURAL SCIENCE
        # ============================================
        {
            'name': 'Agricultural Science',
            'code': 'AGR',
            'subject_type': 'science',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_primary': True,
            'available_for_jss': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # JSS ADDITIONAL SUBJECTS
        # ============================================
        {
            'name': 'Business Studies',
            'code': 'BUS',
            'subject_type': 'commercial',
            'stream': 'general',
            'is_compulsory': True,
            'available_for_jss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # SSS SCIENCE STREAM SUBJECTS
        # ============================================
        {
            'name': 'Physics',
            'code': 'PHY',
            'subject_type': 'science',
            'stream': 'science',
            'is_compulsory': True,
            'available_for_sss': True,
            'has_practical': True,
            'pass_mark': 40,
        },
        {
            'name': 'Chemistry',
            'code': 'CHE',
            'subject_type': 'science',
            'stream': 'science',
            'is_compulsory': True,
            'available_for_sss': True,
            'has_practical': True,
            'pass_mark': 40,
        },
        {
            'name': 'Biology',
            'code': 'BIO',
            'subject_type': 'science',
            'stream': 'science',
            'is_compulsory': True,
            'available_for_sss': True,
            'has_practical': True,
            'pass_mark': 40,
        },
        {
            'name': 'Further Mathematics',
            'code': 'FMA',
            'subject_type': 'science',
            'stream': 'science',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Technical Drawing',
            'code': 'TED',
            'subject_type': 'technical',
            'stream': 'science',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # SSS COMMERCIAL STREAM SUBJECTS
        # ============================================
        {
            'name': 'Financial Accounting',
            'code': 'ACC',
            'subject_type': 'commercial',
            'stream': 'commercial',
            'is_compulsory': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Commerce',
            'code': 'CMR',
            'subject_type': 'commercial',
            'stream': 'commercial',
            'is_compulsory': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Economics',
            'code': 'ECO',
            'subject_type': 'commercial',
            'stream': 'commercial',
            'is_compulsory': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Book Keeping',
            'code': 'BKP',
            'subject_type': 'commercial',
            'stream': 'commercial',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Office Practice',
            'code': 'OFP',
            'subject_type': 'commercial',
            'stream': 'commercial',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Marketing',
            'code': 'MKT',
            'subject_type': 'commercial',
            'stream': 'commercial',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # SSS ARTS STREAM SUBJECTS
        # ============================================
        {
            'name': 'Literature in English',
            'code': 'LIT',
            'subject_type': 'arts',
            'stream': 'arts',
            'is_compulsory': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Government',
            'code': 'GOV',
            'subject_type': 'arts',
            'stream': 'arts',
            'is_compulsory': True,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Geography',
            'code': 'GEO',
            'subject_type': 'arts',
            'stream': 'arts',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Visual Arts',
            'code': 'VIA',
            'subject_type': 'arts',
            'stream': 'arts',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Drama',
            'code': 'DRA',
            'subject_type': 'arts',
            'stream': 'arts',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        
        # ============================================
        # SSS GENERAL SUBJECTS (All Streams)
        # ============================================
        {
            'name': 'Data Processing',
            'code': 'DAP',
            'subject_type': 'technical',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
        {
            'name': 'Food and Nutrition',
            'code': 'FNU',
            'subject_type': 'vocational',
            'stream': 'general',
            'is_compulsory': False,
            'available_for_sss': True,
            'pass_mark': 40,
        },
    ]
    
    # Create or update subjects
    created_count = 0
    updated_count = 0
    
    for subject_data in subjects_data:
        subject, created = Subject.objects.update_or_create(
            code=subject_data['code'],
            defaults=subject_data
        )
        
        if created:
            created_count += 1
            print(f"✓ Created: {subject.name} ({subject.code})")
        else:
            updated_count += 1
            print(f"↻ Updated: {subject.name} ({subject.code})")
    
    print("\n" + "="*60)
    print(f"SUMMARY:")
    print(f"  New subjects created: {created_count}")
    print(f"  Subjects updated: {updated_count}")
    print(f"  Total subjects: {Subject.objects.count()}")
    print("="*60)
    
    # Display subject distribution
    print("\nSUBJECT DISTRIBUTION:")
    print(f"  Creche: {Subject.objects.filter(available_for_creche=True).count()}")
    print(f"  Nursery/KG: {Subject.objects.filter(available_for_nursery=True).count()}")
    print(f"  Primary: {Subject.objects.filter(available_for_primary=True).count()}")
    print(f"  JSS: {Subject.objects.filter(available_for_jss=True).count()}")
    print(f"  SSS: {Subject.objects.filter(available_for_sss=True).count()}")
    print(f"  SSS Science: {Subject.objects.filter(available_for_sss=True, stream='science').count()}")
    print(f"  SSS Commercial: {Subject.objects.filter(available_for_sss=True, stream='commercial').count()}")
    print(f"  SSS Arts: {Subject.objects.filter(available_for_sss=True, stream='arts').count()}")


# Run the population
if __name__ == '__main__':
    populate_nigerian_subjects()