"""
Management command to identify and fix cross-family relationships.

Cross-family relationships occur when members from different Family units
are linked as parents, spouses, or siblings. This causes family trees to
incorrectly branch into other families.

Usage:
    # List all cross-family relationships
    python manage.py fix_cross_family_relationships --list

    # Dry-run: show what would be deleted
    python manage.py fix_cross_family_relationships --dry-run

    # Actually delete the relationships
    python manage.py fix_cross_family_relationships --delete
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from families.models import Relationship, FamilyMember


class Command(BaseCommand):
    help = 'Find and optionally remove cross-family relationships'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all cross-family relationships'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete the cross-family relationships'
        )

    def handle(self, *args, **options):
        # Find all relationships between members of different families
        cross_family_rels = []
        
        for rel in Relationship.objects.select_related('from_member', 'to_member'):
            from_family = rel.from_member.family_id
            to_family = rel.to_member.family_id
            
            if from_family != to_family:
                cross_family_rels.append(rel)

        if not cross_family_rels:
            self.stdout.write(
                self.style.SUCCESS('✓ No cross-family relationships found!')
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f'\n⚠ Found {len(cross_family_rels)} cross-family relationships:\n'
            )
        )

        for i, rel in enumerate(cross_family_rels, 1):
            from_member = rel.from_member
            to_member = rel.to_member
            self.stdout.write(
                f'{i}. {from_member.name} ({from_member.family.branch}) '
                f'--[{rel.relation_type}]--> '
                f'{to_member.name} ({to_member.family.branch})'
            )

        if options.get('delete'):
            count = len(cross_family_rels)
            for rel in cross_family_rels:
                rel.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Deleted {count} cross-family relationships.'
                )
            )
            
            # Also check for cross-family parent links
            self.fix_cross_family_parents()

        elif options.get('dry_run'):
            self.stdout.write(
                self.style.WARNING(
                    '\nDRY-RUN: Use --delete to actually remove these relationships.'
                )
            )
            self.check_cross_family_parents(dry_run=True)

        else:
            self.stdout.write(
                self.style.WARNING(
                    '\nUsage:\n'
                    '  --list     : List all cross-family relationships\n'
                    '  --dry-run  : Show what would be deleted\n'
                    '  --delete   : Delete all cross-family relationships\n'
                )
            )

    def check_cross_family_parents(self, dry_run=False):
        """Check for cross-family parent links via FamilyMember.parents M2M."""
        cross_family_parents = []
        
        for member in FamilyMember.objects.prefetch_related('parents'):
            for parent in member.parents.all():
                if member.family_id != parent.family_id:
                    cross_family_parents.append((member, parent))

        if cross_family_parents:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ Found {len(cross_family_parents)} cross-family parent links:\n'
                )
            )
            
            for member, parent in cross_family_parents:
                self.stdout.write(
                    f'  {member.name} ({member.family.branch}) <- parent <- '
                    f'{parent.name} ({parent.family.branch})'
                )

            if not dry_run:
                self.fix_cross_family_parents_impl(cross_family_parents)

    def fix_cross_family_parents_impl(self, cross_family_parents):
        """Remove cross-family parent links."""
        for member, parent in cross_family_parents:
            member.parents.remove(parent)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Removed {len(cross_family_parents)} cross-family parent links.'
            )
        )

    def fix_cross_family_parents(self):
        """Remove cross-family parent links."""
        cross_family_parents = []
        
        for member in FamilyMember.objects.prefetch_related('parents'):
            for parent in member.parents.all():
                if member.family_id != parent.family_id:
                    cross_family_parents.append((member, parent))

        if cross_family_parents:
            self.fix_cross_family_parents_impl(cross_family_parents)
