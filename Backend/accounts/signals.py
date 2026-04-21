from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from families.models import FamilyMember

@receiver(post_save, sender=User)
def sync_user_to_family_head(sender, instance, created, raw=False, **kwargs):
    """
    """
    # Django fixtures call save(..., raw=True); avoid relationship lookups during raw loads.
    if raw or not getattr(instance, 'member_id', None):
        return

    member = FamilyMember.objects.filter(id=instance.member_id).first()
    if not member:
        return

    # No longer syncing User to FamilyHead as the model has been removed.
