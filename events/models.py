from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="events/")
    created_at = models.DateTimeField(auto_now_add=True)
    member_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title