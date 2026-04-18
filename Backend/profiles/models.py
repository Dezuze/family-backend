from django.db import models
from django.conf import settings


class CommunityRole(models.Model):
	name = models.CharField(max_length=120, unique=True)
	members = models.ManyToManyField(
		'families.FamilyMember',
		related_name='community_roles',
		blank=True,
	)
	priority = models.PositiveSmallIntegerField(default=100)
	can_manage_all = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('priority', 'name')

	def __str__(self):
		return self.name


class Gallery(models.Model):
	image = models.ImageField(upload_to='gallery/')
	date = models.DateField(null=True, blank=True)
	description = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Gallery {self.id} - {self.date}"


class Committee(models.Model):
	# linked to a user (the 'other id' requested)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='committee_entries')
	pic = models.ImageField(upload_to='committee/')
	role = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Committee {self.id} - {self.user.username}"
