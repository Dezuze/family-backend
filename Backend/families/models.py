from django.db import models
from django.conf import settings


class Family(models.Model):
    sl_no = models.CharField(max_length=20)
    branch = models.CharField(max_length=100)

    member_no = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.member_no


class FamilyHead(models.Model):
    family = models.OneToOneField(Family, on_delete=models.CASCADE, related_name="head")

    # optional link to a registered user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, blank=True, null=True)

    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")])

    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    church = models.CharField(max_length=100)
    education = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)


class FamilyMember(models.Model):
    RELATION_CHOICES = [
        ('Head', 'Head'),
        ('Spouse', 'Spouse'),
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Grandfather', 'Grandfather'),
        ('Grandmother', 'Grandmother'),
        ('Grandson', 'Grandson'),
        ('Granddaughter', 'Granddaughter'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Nephew', 'Nephew'),
        ('Niece', 'Niece'),
        ('Cousin', 'Cousin'),
        ('Father-in-law', 'Father-in-law'),
        ('Mother-in-law', 'Mother-in-law'),
        ('Son-in-law', 'Son-in-law'),
        ('Daughter-in-law', 'Daughter-in-law'),
        ('Brother-in-law', 'Brother-in-law'),
        ('Sister-in-law', 'Sister-in-law'),
        ('Other', 'Other'),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="members")

    # temporary id for unregistered persons
    temp_member_id = models.CharField(max_length=50, blank=True, null=True)

    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")], default="M")

    # Kept as free text so users can enter custom labels like
    # "great great great grandfather" from the frontend.
    relation = models.CharField(max_length=50, default='Other')
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_death = models.DateField(blank=True, null=True)

    address_if_different = models.TextField(blank=True, null=True)

    education = models.CharField(max_length=100, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)
    place_of_work = models.CharField(max_length=100, blank=True, null=True)

    blood_group = models.CharField(max_length=10, blank=True, null=True)
    is_deceased = models.BooleanField(default=False)
    is_independent = models.BooleanField(
        default=False,
        help_text='When True, the creator/guardian loses write access and the profile owner has full control.'
    )
    phone_no = models.CharField(max_length=20, blank=True, null=True)
    email_id = models.EmailField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    church_parish = models.CharField(max_length=100, blank=True, null=True)

    photo = models.ImageField(upload_to="members/photos/", blank=True, null=True)
    
    # Member ID in format "III 2" (Roman numeral generation + number)
    # For spouses: "III 2W" (original ID + W suffix)
    member_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='managed_members',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    # Link to other FamilyMember instances to represent parent/child relationships.
    # Use `symmetrical=False` so `parents` and `children` are distinct.
    parents = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='children',
        blank=True,
    )

    @property
    def role(self):
        # Fallback gracefully if committee module is unavailable.
        try:
            if hasattr(self, 'user_account') and self.user_account:
                committee_entry = self.user_account.committee_entries.first()
                if committee_entry and committee_entry.role:
                    return committee_entry.role
        except Exception:
            pass
        return self.relation

    @property
    def is_committee(self):
        try:
            if hasattr(self, 'user_account') and self.user_account:
                return self.user_account.committee_entries.exists()
        except Exception:
            pass
        return False

    def __str__(self):
        return self.name


class DeceasedMember(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="deceased")

    name = models.CharField(max_length=100)
    age_at_death = models.PositiveIntegerField()

    relation = models.CharField(max_length=50)

    date_of_birth = models.DateField()
    date_of_death = models.DateField()

    crematory = models.CharField(max_length=100)

    photo = models.ImageField(upload_to="deceased/photos/", blank=True, null=True)


class FamilyMedia(models.Model):
    CATEGORY_CHOICES = [
        ("family", "Family"),
        ("wedding", "Wedding"),
        ("achievement", "Achievement"),
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="media")

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to="family/gallery/")


class Relationship(models.Model):
    RELATION_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Spouse', 'Spouse'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Grandfather', 'Grandfather'),
        ('Grandmother', 'Grandmother'),
        ('Paternal Grandfather', 'Paternal Grandfather'),
        ('Paternal Grandmother', 'Paternal Grandmother'),
        ('Maternal Grandfather', 'Maternal Grandfather'),
        ('Maternal Grandmother', 'Maternal Grandmother'),
        ('Grandson', 'Grandson'),
        ('Granddaughter', 'Granddaughter'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Nephew', 'Nephew'),
        ('Niece', 'Niece'),
        ('Cousin', 'Cousin'),
        ('Father-in-law', 'Father-in-law'),
        ('Mother-in-law', 'Mother-in-law'),
        ('Son-in-law', 'Son-in-law'),
        ('Daughter-in-law', 'Daughter-in-law'),
        ('Brother-in-law', 'Brother-in-law'),
        ('Sister-in-law', 'Sister-in-law'),
        ('Other', 'Other'),
    ]

    GENDER_MAP = {
        'Father': 'M', 'Mother': 'F',
        'Son': 'M', 'Daughter': 'F',
        'Brother': 'M', 'Sister': 'F',
        'Grandfather': 'M', 'Grandmother': 'F',
        'Paternal Grandfather': 'M', 'Paternal Grandmother': 'F',
        'Maternal Grandfather': 'M', 'Maternal Grandmother': 'F',
        'Grandson': 'M', 'Granddaughter': 'F',
        'Uncle': 'M', 'Aunt': 'F',
        'Nephew': 'M', 'Niece': 'F',
        'Father-in-law': 'M', 'Mother-in-law': 'F',
        'Son-in-law': 'M', 'Daughter-in-law': 'F',
        'Brother-in-law': 'M', 'Sister-in-law': 'F',
    }

    from_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='relationships_from')
    to_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='relationships_to')
    # Free text to support custom links in onboarding while preserving known presets.
    relation_type = models.CharField(max_length=50, default='Other')
    is_inferred = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_member', 'to_member', 'relation_type')

    def clean(self):
        """Prevent duplicate spouse relationships in reverse direction."""
        from django.core.exceptions import ValidationError
        
        # Only validate SPOUSE relationships to prevent bidirectional duplicates
        if (self.relation_type or '').strip().upper() == 'SPOUSE':
            # Check if reverse relationship already exists
            reverse_exists = Relationship.objects.filter(
                from_member_id=self.to_member_id,
                to_member_id=self.from_member_id,
                relation_type='Spouse'
            ).exclude(id=self.id).exists()
            
            if reverse_exists:
                raise ValidationError(
                    f'A spouse relationship already exists between {self.to_member.name} and {self.from_member.name}. '
                    'Relationship is bidirectional.'
                )

    def __str__(self):
        return f'{self.from_member.name} -> {self.relation_type} -> {self.to_member.name}'
