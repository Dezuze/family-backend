from django.contrib import admin
from unfold.admin import ModelAdmin
from . import models


@admin.register(models.Family)
class FamilyAdmin(ModelAdmin):
    list_display = ('member_no', 'sl_no', 'branch', 'created_at')




@admin.register(models.FamilyMember)
class FamilyMemberAdmin(ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age', 'blood_group', 'is_independent')
    list_filter = ('relation', 'blood_group', 'family', 'is_independent')
    search_fields = ('name', 'temp_member_id')

    tabs = [
        ("Personal Info", ["info_tab"]),
        ("Work & Education", ["work_tab"]),
        ("Gallery & Links", ["links_tab"]),
    ]
    
    fieldsets = (
        ("Basic Information", {
            "classes": ["unfold-tab", "unfold-info_tab"],
            "fields": (("name", "relation"), ("age", "date_of_birth"), "blood_group", "family", "committee_role")
        }),
        ("Career & Studies", {
            "classes": ["unfold-tab", "unfold-work_tab"],
            "fields": (("education", "occupation"), "place_of_work")
        }),
        ("Profile Data", {
            "classes": ["unfold-tab", "unfold-links_tab"],
            "fields": ("temp_member_id", "parents", "photo", "created_by")
        }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        from profiles.models import CommunityRole
        if db_field.name == "committee_role":
            # Only show active roles
            roles = CommunityRole.objects.filter(is_active=True).order_by('priority', 'name')
            choices = [(role.name, role.name) for role in roles]
            from django.forms import Select
            kwargs["widget"] = Select(choices=[("", "---------")] + choices)
            kwargs["required"] = False
        return super().formfield_for_dbfield(db_field, **kwargs)


@admin.register(models.DeceasedMember)
class DeceasedMemberAdmin(ModelAdmin):
    list_display = ('name', 'family', 'relation', 'age_at_death')
    list_filter = ('family',)
    search_fields = ('name',)


@admin.register(models.FamilyCommitteeMember)
class FamilyCommitteeMemberAdmin(ModelAdmin):
    list_display = ('term_label', 'category', 'role_title', 'name', 'member_code', 'phone_no', 'is_active')
    list_filter = ('term_label', 'category', 'is_active')
    search_fields = ('name', 'role_title', 'member_code', 'phone_no', 'email_id')
    ordering = ('term_label', 'category', 'display_order', 'name')
