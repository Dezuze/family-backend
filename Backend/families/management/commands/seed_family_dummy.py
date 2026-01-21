from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import date, timedelta
import random
import uuid

from families.models import Family, FamilyHead, FamilyMember


class Command(BaseCommand):
    help = 'Seed dummy families and members with parent/child relationships.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=50, help='Total number of members to create')

    def handle(self, *args, **options):
        count = options.get('count', 50)
        created = 0
        fam_index = 1
        members = []

        with transaction.atomic():
            while created < count:
                # create a family
                # Ensure unique member_no to avoid IntegrityError on repeated runs
                member_no = f'FAM{1000+fam_index}-{uuid.uuid4().hex[:6]}'
                fam = Family.objects.create(
                    sl_no=str(fam_index),
                    branch=f'Branch {fam_index}',
                    member_no=member_no,
                )

                # Create two parents (father, mother)
                father_age = random.randint(35, 70)
                mother_age = father_age - random.randint(-3, 3)

                father = FamilyMember.objects.create(
                    family=fam,
                    temp_member_id=f'F{fam_index}P1',
                    name=f'Father {fam_index}',
                    age=father_age,
                    relation='Father',
                    date_of_birth=date.today() - timedelta(days=father_age * 365),
                    education='N/A',
                    occupation='N/A',
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+']),
                )

                mother = FamilyMember.objects.create(
                    family=fam,
                    temp_member_id=f'F{fam_index}P2',
                    name=f'Mother {fam_index}',
                    age=mother_age,
                    relation='Mother',
                    date_of_birth=date.today() - timedelta(days=mother_age * 365),
                    education='N/A',
                    occupation='N/A',
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+']),
                )

                # set parents as spouses? we don't have spouse field; we will record as relation text
                # Create a FamilyHead record from father
                FamilyHead.objects.create(
                    family=fam,
                    user=None,
                    name=father.name,
                    nickname='',
                    age=father.age,
                    gender='M',
                    address='N/A',
                    phone='N/A',
                    email=f'father{fam_index}@example.com',
                    church='N/A',
                    education='N/A',
                    occupation='N/A',
                )

                members.append(father)
                members.append(mother)
                created += 2

                # Create several children for this family
                num_children = random.randint(1, 6)
                for c in range(num_children):
                    if created >= count:
                        break
                    child_age = random.randint(0, 30)
                    role = 'Son' if random.random() < 0.5 else 'Daughter'
                    child = FamilyMember.objects.create(
                        family=fam,
                        temp_member_id=f'F{fam_index}C{c+1}',
                        name=f'Child_{fam_index}_{c+1}',
                        age=child_age,
                        relation=role,
                        date_of_birth=date.today() - timedelta(days=child_age * 365),
                        education='N/A',
                        occupation='N/A',
                        blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+']),
                    )
                    # set both parents as this child's parents
                    child.parents.set([father, mother])
                    members.append(child)
                    created += 1

                fam_index += 1

            # After creating all members, optionally create some spouses for random members
            # We'll add simple relation text to indicate spouse relationships
            # and create spouse members who are linked as children/parents as appropriate
            # but more simply, create spouse entries and set relation='Spouse'
            extra_spouse_count = max(0, int(count * 0.1))
            for i in range(extra_spouse_count):
                person = random.choice(members)
                spouse_age = max(18, person.age + random.randint(-5, 5))
                spouse = FamilyMember.objects.create(
                    family=person.family,
                    temp_member_id=f'SP{person.pk}_{i}',
                    name=f'Spouse_of_{person.name}',
                    age=spouse_age,
                    relation='Spouse',
                    date_of_birth=date.today() - timedelta(days=spouse_age * 365),
                    education='N/A',
                    occupation='N/A',
                    blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+']),
                )
                # if the person is parent of some children, add spouse as parent too
                children = list(person.children.all())
                if children:
                    for ch in children:
                        ch.parents.add(spouse)
                members.append(spouse)

        self.stdout.write(self.style.SUCCESS(f'Created {len(members)} members across {fam_index-1} families.'))
