from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from families.models import FamilyMember, FamilyHead

@receiver(post_save, sender=User)
def sync_user_to_family_head(sender, instance, created, raw=False, **kwargs):
    """
    Synchronizes the User link to FamilyHead records if the member is a head.
    """
    # Django fixtures call save(..., raw=True); avoid relationship lookups during raw loads.
    if raw or not getattr(instance, 'member_id', None):
        return

    member = FamilyMember.objects.filter(id=instance.member_id).first()
    if not member:
        return

    # Sync User to FamilyHead if this member is the head of their family.
    try:
        family_head = FamilyHead.objects.get(family=member.family)
        # If the member name matches the head name, we assume they are the same person.
        if family_head.name == member.name and family_head.user != instance:
            family_head.user = instance
            family_head.save()
    except FamilyHead.DoesNotExist:
        pass
