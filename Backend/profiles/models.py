
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
	MEDIA_TYPE_CHOICES = [
		('image', 'Image'),
		('video', 'Video'),
	]

	image = models.FileField(upload_to='gallery/')
	media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='image')
	date = models.DateField(null=True, blank=True)
	description = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Gallery {self.id} - {self.date}"


