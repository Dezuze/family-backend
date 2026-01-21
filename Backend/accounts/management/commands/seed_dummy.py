from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.base import ContentFile
from pathlib import Path
from io import BytesIO
from PIL import Image

from profiles.models import Gallery
from families.models import Family, FamilyHead, FamilyMember, FamilyMedia


def _make_png_bytes(color=(200, 100, 80), size=(200, 140)):
    buf = BytesIO()
    Image.new('RGB', size, color=color).save(buf, format='PNG')
    buf.seek(0)
    return buf.read()


class Command(BaseCommand):
    help = 'Seed dummy data for gallery, families and members for local testing'

    def handle(self, *args, **options):
        User = get_user_model()

        created_users = []
        for i in range(1, 4):
            username = f'demo{i}'
            email = f'demo{i}@example.com'
            member_id = f'member{i}'
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(username=username, email=email, member_id=member_id, password='password')
                created_users.append(u)

        # ensure media dir exists
        media_root = Path(settings.MEDIA_ROOT)
        media_root.mkdir(parents=True, exist_ok=True)

        # Create some gallery images
        gallery_count = 0
        for i in range(1, 7):
            color = (50 + i * 20, 80 + i * 10, 120 + i * 5)
            img_bytes = _make_png_bytes(color=color, size=(800, 600))
            name = f'gallery_{i}.png'
            g = Gallery()
            g.date = '2025-01-0' + str((i % 9) + 1)
            g.description = f'Demo gallery image {i}'
            g.image.save(name, ContentFile(img_bytes), save=True)
            gallery_count += 1

        # Create a family with members
        family, _ = Family.objects.get_or_create(sl_no='SL1', branch='Main', member_no='FAM001')
        # head
        head, _ = FamilyHead.objects.get_or_create(family=family, defaults={
            'name': 'John Doe', 'age': 58, 'gender': 'M', 'address': '123 Demo St', 'phone': '555-0100',
            'email': 'johndoe@example.com', 'church': 'Demo Church', 'education': 'College', 'occupation': 'Farmer'
        })

        # members
        members_created = 0
        for j in range(1, 6):
            mem, created = FamilyMember.objects.get_or_create(
                family=family,
                name=f'Member {j}',
                defaults={
                    'age': 20 + j, 'relation': 'Child', 'date_of_birth': f'200{j}-01-01',
                    'education': 'School', 'occupation': 'Student', 'blood_group': 'O+',
                }
            )
            if created:
                members_created += 1

        # Add family media images
        fm_count = 0
        for k in range(1, 4):
            img_bytes = _make_png_bytes(color=(100 + k * 30, 120, 80), size=(640, 480))
            name = f'family_media_{k}.png'
            fm = FamilyMedia.objects.create(family=family, category='family')
            fm.image.save(name, ContentFile(img_bytes), save=True)
            fm_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created users: {len(created_users)}'))
        self.stdout.write(self.style.SUCCESS(f'Created gallery items: {gallery_count}'))
        self.stdout.write(self.style.SUCCESS(f'Created family: {family.member_no} with members: {members_created}'))
        self.stdout.write(self.style.SUCCESS(f'Created family media: {fm_count}'))
