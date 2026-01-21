from django.db import models

class News(models.Model):
    TYPE_CHOICES = (
        ('news', 'News'),
        ('event', 'Event'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='news/')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    
    # New fields for Event logic
    event_date = models.DateTimeField(null=True, blank=True, help_text="Required if type is 'event'")
    location = models.CharField(max_length=255, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='posts', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
