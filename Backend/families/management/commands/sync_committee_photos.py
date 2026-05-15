"""
Django management command to sync committee member photos from production DB dump.
Maps committee members to their photo filenames based on the production data.
"""
from django.core.management.base import BaseCommand
from families.models import FamilyCommitteeMember
from django.conf import settings
import os

# Production photo mapping from live_family_db.sql
# Only files that actually exist in production are included
PHOTO_MAPPING = {
    "Baby Kuriakose": "committee/photos/baby_kuriakose.jpeg",
}

# Photos referenced in production DB but files don't exist locally
MISSING_PHOTOS = {
    "Korula Issac": "committee/photos/korula.jpeg",
    "Saju Elias": "committee/photos/saju_eleas.jpeg",
}


class Command(BaseCommand):
    help = "Sync committee member photos from production data"

    def handle(self, *args, **options):
        term_label = "2026-28"
        updated_count = 0
        missing_files = []
        media_root = settings.MEDIA_ROOT

        # Sync photos that exist
        for member_name, photo_path in PHOTO_MAPPING.items():
            try:
                # Search for member by exact name match
                member = FamilyCommitteeMember.objects.get(
                    term_label=term_label, name__iexact=member_name
                )

                # Check if photo file actually exists
                photo_full_path = os.path.join(media_root, photo_path)

                if os.path.exists(photo_full_path):
                    if not member.photo or str(member.photo) != photo_path:
                        member.photo = photo_path
                        member.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Updated {member_name}: {photo_path}"
                            )
                        )
                    else:
                        self.stdout.write(
                            f"✓ {member_name} already has photo: {photo_path}"
                        )
                else:
                    missing_files.append(photo_path)
                    self.stdout.write(
                        self.style.WARNING(f"⚠ Photo file missing: {photo_path}")
                    )
            except FamilyCommitteeMember.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"✗ Member not found: {member_name}")
                )

        # Report photos that are in production DB but files don't exist
        self.stdout.write("\nProduction DB references (files missing locally):")
        for member_name, photo_path in MISSING_PHOTOS.items():
            self.stdout.write(
                self.style.WARNING(f"  {member_name}: {photo_path} (not found)")
            )

        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Synced {updated_count} photo(s)")
        )
        if missing_files:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ {len(missing_files)} file(s) missing from local media directory"
                )
            )
