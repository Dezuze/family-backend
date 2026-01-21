from django.core.management.base import BaseCommand
from accounts.models import User
from families.models import FamilyMember, Family
from profiles.models import Committee
from news.models import News
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Populate database with dummy family tree data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning old data...")
        FamilyMember.objects.all().delete()
        Family.objects.all().delete()
        User.objects.all().delete()
        Committee.objects.all().delete()
        News.objects.all().delete()

        self.stdout.write("Creating Family Structure...")
        main_family = Family.objects.create(
            sl_no="001",
            branch="Main Branch",
            member_no="FAM001"
        )

        self.stdout.write("Creating Admins and Users...")
        # Admin
        admin = User.objects.create_superuser('admin', 'admin@family.com', 'Admin@123')
        admin.member_id = "ADM001"
        admin.save()
        
        # Test User
        test_user = User.objects.create_user('testuser', 'test@family.com', 'User@123')
        test_user.member_id = "TEST001"
        test_user.save()

        # Helper to create user+member
        def create_person(username, name, gender, age, generation):
            email = f"{username.lower()}@family.com"
            try:
                u = User.objects.get(username=username)
            except User.DoesNotExist:
                u = User.objects.create_user(username, email, 'User@123')
                u.member_id = f"MEM{random.randint(1000,9999)}"
                u.save()

            fm = FamilyMember.objects.create(
                user=u,
                family=main_family,
                name=name,
                age=age,
                date_of_birth=date(2025-age, 1, 1),
                blood_group=random.choice(['A+', 'B+', 'O+', 'AB+']),
                education="Degree",
                occupation="Professional",
                relation="Self", # logic handled by links
            )
            return fm

        # Generation 1 (Grandparents) - The Roots
        g1_dad = create_person('Grandpa', 'Joseph Kollaparambil', 'M', 80, 1)
        g1_mom = create_person('Grandma', 'Mary Joseph', 'F', 75, 1)
        
        # Link Spouses
        g1_dad.spouse = g1_mom
        g1_dad.save()
        g1_mom.spouse = g1_dad
        g1_mom.save()

        # Generation 2 (Children of G1)
        g2_sons = []
        for i, name in enumerate(['Thomas', 'Mathew', 'Philip']):
            # Son
            son = create_person(f'Son{i}', f'{name} Joseph', 'M', 55 - (i*2), 2)
            son.parents.add(g1_dad, g1_mom)
            
            # Wife for son
            wife = create_person(f'Wife{i}', f'Sarah {name}', 'F', 52 - (i*2), 2)
            wife.spouse = son
            wife.save()
            son.spouse = wife
            son.save()
            
            g2_sons.append((son, wife))

        # Generation 3 (Grandchildren)
        for idx, (dad, mom) in enumerate(g2_sons):
            for j in range(2): # 2 kids each
                kid_name = f'Child {j} of {dad.name.split()[0]}'
                kid_user = f'Kid{dad.id}_{j}'
                
                # Make one specifc kid the 'Test User' linked account
                if idx == 0 and j == 0:
                     kid = FamilyMember.objects.create(
                        user=test_user,
                        family=main_family,
                        name="Test User (You)",
                        age=25,
                        date_of_birth=date(2000, 1, 1),
                        blood_group='O+',
                        education="PhD",
                        occupation="Engineer",
                        relation="Self"
                     )
                else:
                    kid = create_person(kid_user, kid_name, 'M' if j%2==0 else 'F', 25 - j, 3)

                kid.parents.add(dad, mom)
                
                # Add to committee randomly
                if random.random() > 0.7:
                    Committee.objects.create(
                        user=kid.user,
                        role=random.choice(['Youth Rep', 'Secretary', 'Volunteer']),
                        pic=None
                    )

        # Re-create News/Events so homepage isn't empty
        today = date.today()
        News.objects.create(
            title="Family Gathering", 
            description="Annual Meet", 
            type='event',
            event_date=today+timedelta(days=10), 
            location="Main Hall", 
            image="news/family_gathering.png"
        )
        News.objects.create(
            title="New Website", 
            description="Welcome to the new site!", 
            type='news', 
            image="news/charity_drive.png"
        )

        self.stdout.write(self.style.SUCCESS("Successfully populated family tree data"))
