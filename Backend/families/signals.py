from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .cache import invalidate_family_tree_cache
from .models import Family, FamilyMember, Relationship


@receiver([post_save, post_delete], sender=Family)
@receiver([post_save, post_delete], sender=FamilyMember)
@receiver([post_save, post_delete], sender=Relationship)
def clear_family_tree_cache_on_model_change(**kwargs):
    invalidate_family_tree_cache()


@receiver(m2m_changed, sender=FamilyMember.parents.through)
def clear_family_tree_cache_on_parent_change(action, **kwargs):
    if action in {"post_add", "post_remove", "post_clear"}:
        invalidate_family_tree_cache()
