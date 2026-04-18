from django.core.management.base import BaseCommand, CommandError
from profiles.models import CommunityRole
from families.models import FamilyMember


class Command(BaseCommand):
    help = 'Grant a global manage role to a FamilyMember. Creates the role if missing.'

    def add_arguments(self, parser):
        parser.add_argument('--role', type=str, default='Global Manager', help='Role name to grant')
        parser.add_argument('--member', type=str, required=True, help='Exact FamilyMember.name to assign')

    def handle(self, *args, **options):
        role_name = options['role'].strip()
        member_name = options['member'].strip()

        if not member_name:
            raise CommandError('Member name is required')

        role, created = CommunityRole.objects.get_or_create(name=role_name, defaults={'priority': 50, 'is_active': True, 'can_manage_all': True})
        if not created and not role.can_manage_all:
            role.can_manage_all = True
            role.save()

        member = FamilyMember.objects.filter(name__iexact=member_name).first()
        if not member:
            raise CommandError(f'FamilyMember with name "{member_name}" not found')

        role.members.add(member)
        role.save()

        self.stdout.write(self.style.SUCCESS(f'Assigned role "{role_name}" (can_manage_all={role.can_manage_all}) to member "{member.name}" (id={member.id})'))
