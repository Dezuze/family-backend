from django.core.management.base import BaseCommand
from django.db import transaction

from families.models import Family, FamilyHead, FamilyMember, DeceasedMember, FamilyMedia


class Command(BaseCommand):
    help = 'Wipe family data (optional) and/or link every member to every other member.'

    def add_arguments(self, parser):
        parser.add_argument('--wipe', action='store_true', help='Delete all family-related data')
        parser.add_argument('--link-everyone', action='store_true', help='Make every member parent and child of every other member')

    def handle(self, *args, **options):
        wiped = False
        if options.get('wipe'):
            with transaction.atomic():
                FamilyMedia.objects.all().delete()
                DeceasedMember.objects.all().delete()
                FamilyHead.objects.all().delete()
                FamilyMember.objects.all().delete()
                Family.objects.all().delete()
            wiped = True
            self.stdout.write(self.style.SUCCESS('Deleted all family-related data.'))

        if options.get('link_everyone'):
            members = list(FamilyMember.objects.all())
            if not members:
                self.stdout.write(self.style.WARNING('No members to link.'))
                return
            # For each member, set parents to all other members
            for m in members:
                others = [o for o in members if o.pk != m.pk]
                m.parents.set(others)
            self.stdout.write(self.style.SUCCESS('Linked everyone to everyone (parents/children).'))

        if not options.get('wipe') and not options.get('link_everyone'):
            msg = 'No action specified. Use --wipe and/or --link-everyone.'
            self.stdout.write(self.style.WARNING(msg))
