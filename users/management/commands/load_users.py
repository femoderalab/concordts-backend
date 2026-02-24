# users/management/commands/load_users.py
"""
Load 150 Users with Different Roles for Nigerian School System
Password for all users: Fatunbi1111.

Run: python manage.py load_users
"""

from django.core.management.base import BaseCommand
from users.models import User
from datetime import date
import random


class Command(BaseCommand):
    help = 'Load 150 users across all roles with password: Fatunbi1111.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('\n' + '='*80))
        self.stdout.write(self.style.WARNING('LOADING 150 USERS - ALL ROLES'))
        self.stdout.write(self.style.WARNING('Default Password: Fatunbi1111.'))
        self.stdout.write(self.style.WARNING('='*80 + '\n'))
        
        self.load_admin_users()
        self.load_teaching_staff()
        self.load_non_teaching_staff()
        self.load_students()
        self.load_parents()
        
        total_users = User.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n✅ TOTAL USERS CREATED: {total_users}\n'))

    def load_admin_users(self):
        """Load administrative staff"""
        self.stdout.write(self.style.WARNING('\n👔 Loading Administrative Users...'))
        
        admins = [
            # HEAD/PROPRIETORS (2)
            ('CTS_0001', 'Adebayo', 'Ogunleye', 'head', 'male', 'oyo', 'adebayo.ogunleye@school.com', '08012345678'),
            ('CTS_0002', 'Ngozi', 'Okafor', 'head', 'female', 'anambra', 'ngozi.okafor@school.com', '08012345679'),
            
            # PRINCIPALS (3)
            ('CTS_0003', 'Ibrahim', 'Musa', 'principal', 'male', 'kano', 'ibrahim.musa@school.com', '08012345680'),
            ('CTS_0004', 'Chioma', 'Nwosu', 'principal', 'female', 'imo', 'chioma.nwosu@school.com', '08012345681'),
            ('CTS_0005', 'Tunde', 'Bakare', 'principal', 'male', 'lagos', 'tunde.bakare@school.com', '08012345682'),
            
            # VICE PRINCIPALS (4)
            ('CTS_0006', 'Fatima', 'Bello', 'vice_principal', 'female', 'kaduna', 'fatima.bello@school.com', '08012345683'),
            ('CTS_0007', 'Emeka', 'Eze', 'vice_principal', 'male', 'enugu', 'emeka.eze@school.com', '08012345684'),
            ('CTS_0008', 'Blessing', 'Okoro', 'vice_principal', 'female', 'rivers', 'blessing.okoro@school.com', '08012345685'),
            ('CTS_0009', 'Yusuf', 'Abubakar', 'vice_principal', 'male', 'sokoto', 'yusuf.abubakar@school.com', '08012345686'),
            
            # HEAD MASTERS (2)
            ('CTS_0010', 'Oluwaseun', 'Adeyemi', 'hm', 'male', 'ogun', 'oluwaseun.adeyemi@school.com', '08012345687'),
            ('CTS_0011', 'Amina', 'Lawal', 'hm', 'female', 'kwara', 'amina.lawal@school.com', '08012345688'),
        ]
        
        for reg, fname, lname, role, gender, state, email, phone in admins:
            user, created = User.objects.get_or_create(
                registration_number=reg,
                defaults={
                    'first_name': fname, 'last_name': lname, 'role': role,
                    'gender': gender, 'state_of_origin': state, 'email': email,
                    'phone_number': phone, 'is_staff': True, 'is_active': True,
                    'date_of_birth': date(1975, random.randint(1, 12), random.randint(1, 28))
                }
            )
            if created:
                user.set_password('Fatunbi1111.')
                user.save()
                self.stdout.write(f'  ✓ Created: {user.get_full_name()} ({role})')

    def load_teaching_staff(self):
        """Load 40 teachers"""
        self.stdout.write(self.style.WARNING('\n👨‍🏫 Loading Teaching Staff (40 Teachers)...'))
        
        first_names_m = ['Chukwudi', 'Olumide', 'Abdullahi', 'Kenneth', 'Samuel', 'Joseph', 'Daniel', 'Emmanuel',
                         'Michael', 'David', 'James', 'John', 'Peter', 'Paul', 'Moses', 'Isaac', 'Jacob', 'Stephen',
                         'Matthew', 'Mark', 'Luke', 'Timothy', 'Joshua', 'Caleb']
        first_names_f = ['Chidinma', 'Aisha', 'Funmilayo', 'Grace', 'Mercy', 'Faith', 'Hope', 'Joy',
                         'Peace', 'Patience', 'Mary', 'Sarah', 'Ruth', 'Esther', 'Deborah', 'Hannah', 
                         'Rebecca', 'Rachel', 'Lydia', 'Priscilla', 'Elizabeth', 'Martha', 'Naomi', 'Miriam']
        last_names = ['Adewale', 'Okonkwo', 'Ibrahim', 'Nnamdi', 'Olayinka', 'Mohammed', 'Chukwuma', 'Babatunde',
                      'Ifeoma', 'Chiamaka', 'Oluwasegun', 'Chinonso', 'Adaeze', 'Adeola', 'Temitope', 'Folake',
                      'Kehinde', 'Taiwo', 'Biodun', 'Kolawole', 'Ayodele', 'Bamidele', 'Omotola', 'Gbemisola']
        
        states = ['lagos', 'oyo', 'ogun', 'kano', 'kaduna', 'rivers', 'delta', 'enugu', 'anambra', 'imo']
        roles = ['teacher', 'form_teacher', 'subject_teacher']
        
        for i in range(40):
            reg_num = f'CTS_T{str(i+1).zfill(3)}'
            gender = random.choice(['male', 'female'])
            fname = random.choice(first_names_m if gender == 'male' else first_names_f)
            lname = random.choice(last_names)
            role = random.choice(roles)
            state = random.choice(states)
            email = f'{fname.lower()}.{lname.lower()}{i+1}@school.com'
            phone = f'0801{str(random.randint(1000000, 9999999))}'
            
            user, created = User.objects.get_or_create(
                registration_number=reg_num,
                defaults={
                    'first_name': fname, 'last_name': lname, 'role': role,
                    'gender': gender, 'state_of_origin': state, 'email': email,
                    'phone_number': phone, 'is_staff': True, 'is_active': True,
                    'date_of_birth': date(random.randint(1980, 1995), random.randint(1, 12), random.randint(1, 28))
                }
            )
            if created:
                user.set_password('Fatunbi1111.')
                user.save()
                if (i + 1) % 10 == 0:
                    self.stdout.write(f'  ✓ Created {i + 1}/40 teachers')

    def load_non_teaching_staff(self):
        """Load non-teaching staff"""
        self.stdout.write(self.style.WARNING('\n👥 Loading Non-Teaching Staff...'))
        
        staff = [
            # ACCOUNTANTS (3)
            ('CTS_A001', 'Nkechi', 'Okeke', 'accountant', 'female', 'abia'),
            ('CTS_A002', 'Usman', 'Garba', 'accountant', 'male', 'borno'),
            ('CTS_A003', 'Folashade', 'Williams', 'accountant', 'female', 'lagos'),
            
            # SECRETARIES (4)
            ('CTS_S001', 'Joke', 'Adekunle', 'secretary', 'female', 'ekiti'),
            ('CTS_S002', 'Hauwa', 'Suleiman', 'secretary', 'female', 'bauchi'),
            ('CTS_S003', 'Chinwe', 'Udoka', 'secretary', 'female', 'ebonyi'),
            ('CTS_S004', 'Ronke', 'Oladele', 'secretary', 'female', 'osun'),
            
            # LIBRARIANS (3)
            ('CTS_L001', 'Adamu', 'Shehu', 'librarian', 'male', 'niger'),
            ('CTS_L002', 'Ngozi', 'Ibe', 'librarian', 'female', 'abia'),
            ('CTS_L003', 'Kunle', 'Ajayi', 'librarian', 'male', 'ondo'),
            
            # LABORATORY TECHNICIANS (3)
            ('CTS_LAB01', 'Chidi', 'Obi', 'laboratory', 'male', 'anambra'),
            ('CTS_LAB02', 'Bisi', 'Adebayo', 'laboratory', 'female', 'oyo'),
            ('CTS_LAB03', 'Ahmed', 'Balarabe', 'laboratory', 'male', 'katsina'),
            
            # SECURITY (4)
            ('CTS_SEC01', 'Musa', 'Tanko', 'security', 'male', 'plateau'),
            ('CTS_SEC02', 'Godwin', 'Okafor', 'security', 'male', 'delta'),
            ('CTS_SEC03', 'Sani', 'Umar', 'security', 'male', 'jigawa'),
            ('CTS_SEC04', 'Felix', 'Udo', 'security', 'male', 'cross_river'),
            
            # CLEANERS (3)
            ('CTS_C001', 'Mama', 'Nkechi', 'cleaner', 'female', 'imo'),
            ('CTS_C002', 'Zainab', 'Aliyu', 'cleaner', 'female', 'kebbi'),
            ('CTS_C003', 'Blessing', 'Eze', 'cleaner', 'female', 'enugu'),
        ]
        
        for reg, fname, lname, role, gender, state in staff:
            email = f'{fname.lower()}.{lname.lower()}@school.com'
            phone = f'0803{str(random.randint(1000000, 9999999))}'
            
            user, created = User.objects.get_or_create(
                registration_number=reg,
                defaults={
                    'first_name': fname, 'last_name': lname, 'role': role,
                    'gender': gender, 'state_of_origin': state, 'email': email,
                    'phone_number': phone, 'is_staff': True, 'is_active': True,
                    'date_of_birth': date(random.randint(1975, 1990), random.randint(1, 12), random.randint(1, 28))
                }
            )
            if created:
                user.set_password('Fatunbi1111.')
                user.save()
                self.stdout.write(f'  ✓ Created: {fname} {lname} ({role})')

    def load_students(self):
        """Load 50 students"""
        self.stdout.write(self.style.WARNING('\n👦 Loading Students (50)...'))
        
        first_names_m = ['Tobiloba', 'Ayomide', 'Abdulrahman', 'Chibueze', 'Emmanuel', 'Daniel', 'David',
                         'Samuel', 'Joshua', 'Michael', 'Israel', 'Gabriel', 'Nathaniel', 'Benjamin',
                         'Victor', 'Joseph', 'Daniel', 'Matthew', 'Solomon', 'Elijah']
        first_names_f = ['Anuoluwapo', 'Chiamaka', 'Zainab', 'Treasure', 'Favour', 'Blessing', 'Gift',
                         'Precious', 'Princess', 'Grace', 'Faith', 'Hope', 'Joy', 'Peace', 'Patience',
                         'Esther', 'Hannah', 'Sarah', 'Ruth', 'Mary']
        last_names = ['Adeola', 'Okafor', 'Yusuf', 'Nwankwo', 'Adeyemi', 'Ibrahim', 'Chukwu', 'Balogun',
                      'Ogundele', 'Madu', 'Hassan', 'Eze', 'Afolayan', 'Okoro', 'Suleiman', 'Nwosu',
                      'Adebisi', 'Okeke', 'Ahmad', 'Okonkwo', 'Bello', 'Onyeka', 'Usman', 'Chidera']
        
        states = ['lagos', 'oyo', 'ogun', 'kano', 'kaduna', 'rivers', 'delta', 'enugu', 'anambra', 
                  'imo', 'edo', 'kwara', 'osun', 'ekiti', 'ondo', 'cross_river', 'akwa_ibom']
        
        for i in range(50):
            reg_num = f'CTS_{str(2024)}_{str(i+1).zfill(3)}'
            gender = random.choice(['male', 'female'])
            fname = random.choice(first_names_m if gender == 'male' else first_names_f)
            lname = random.choice(last_names)
            state = random.choice(states)
            
            user, created = User.objects.get_or_create(
                registration_number=reg_num,
                defaults={
                    'first_name': fname, 'last_name': lname, 'role': 'student',
                    'gender': gender, 'state_of_origin': state,
                    'is_active': True, 'is_staff': False,
                    'date_of_birth': date(random.randint(2008, 2018), random.randint(1, 12), random.randint(1, 28))
                }
            )
            if created:
                user.set_password('Fatunbi1111.')
                user.save()
                if (i + 1) % 10 == 0:
                    self.stdout.write(f'  ✓ Created {i + 1}/50 students')

    def load_parents(self):
        """Load 27 parents"""
        self.stdout.write(self.style.WARNING('\n👨‍👩‍👧 Loading Parents/Guardians (27)...'))
        
        parents = [
            ('CTS_P001', 'Alhaji', 'Musa', 'male', 'kano'),
            ('CTS_P002', 'Mrs', 'Adeyemi', 'female', 'lagos'),
            ('CTS_P003', 'Chief', 'Okonkwo', 'male', 'anambra'),
            ('CTS_P004', 'Mrs', 'Ibrahim', 'female', 'kaduna'),
            ('CTS_P005', 'Mr', 'Okafor', 'male', 'enugu'),
            ('CTS_P006', 'Mrs', 'Bello', 'female', 'kwara'),
            ('CTS_P007', 'Engr', 'Nwosu', 'male', 'imo'),
            ('CTS_P008', 'Dr', 'Adeleke', 'female', 'osun'),
            ('CTS_P009', 'Pastor', 'Eze', 'male', 'ebonyi'),
            ('CTS_P010', 'Mrs', 'Usman', 'female', 'sokoto'),
            ('CTS_P011', 'Mr', 'Okoro', 'male', 'rivers'),
            ('CTS_P012', 'Mrs', 'Yusuf', 'female', 'niger'),
            ('CTS_P013', 'Dr', 'Nnamdi', 'male', 'abia'),
            ('CTS_P014', 'Mrs', 'Hassan', 'female', 'bauchi'),
            ('CTS_P015', 'Hon', 'Adeola', 'male', 'oyo'),
            ('CTS_P016', 'Mrs', 'Mohammed', 'female', 'borno'),
            ('CTS_P017', 'Mr', 'Chukwu', 'male', 'delta'),
            ('CTS_P018', 'Mrs', 'Abubakar', 'female', 'katsina'),
            ('CTS_P019', 'Prof', 'Onyeka', 'male', 'anambra'),
            ('CTS_P020', 'Mrs', 'Balogun', 'female', 'ogun'),
            ('CTS_P021', 'Mr', 'Aliyu', 'male', 'kebbi'),
            ('CTS_P022', 'Mrs', 'Ojo', 'female', 'ekiti'),
            ('CTS_P023', 'Barr', 'Udoka', 'male', 'imo'),
            ('CTS_P024', 'Mrs', 'Suleiman', 'female', 'plateau'),
            ('CTS_P025', 'Alhaji', 'Garba', 'male', 'jigawa'),
            ('CTS_P026', 'Mrs', 'Oladele', 'female', 'ondo'),
            ('CTS_P027', 'Deacon', 'Udo', 'male', 'cross_river'),
        ]
        
        for reg, fname, lname, gender, state in parents:
            email = f'{fname.lower()}.{lname.lower()}@parent.com'
            phone = f'0805{str(random.randint(1000000, 9999999))}'
            
            user, created = User.objects.get_or_create(
                registration_number=reg,
                defaults={
                    'first_name': fname, 'last_name': lname, 'role': 'parent',
                    'gender': gender, 'state_of_origin': state, 'email': email,
                    'phone_number': phone, 'is_active': True, 'is_staff': False,
                    'date_of_birth': date(random.randint(1970, 1985), random.randint(1, 12), random.randint(1, 28))
                }
            )
            if created:
                user.set_password('Fatunbi1111.')
                user.save()
                self.stdout.write(f'  ✓ Created: {fname} {lname}')
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n📊 USER SUMMARY:'))
        self.stdout.write(f'  Administrative: {User.objects.filter(role__in=["head", "hm", "principal", "vice_principal"]).count()}')
        self.stdout.write(f'  Teachers: {User.objects.filter(role__in=["teacher", "form_teacher", "subject_teacher"]).count()}')
        self.stdout.write(f'  Non-Teaching Staff: {User.objects.filter(role__in=["accountant", "secretary", "librarian", "laboratory", "security", "cleaner"]).count()}')
        self.stdout.write(f'  Students: {User.objects.filter(role="student").count()}')
        self.stdout.write(f'  Parents: {User.objects.filter(role="parent").count()}')