from django.db import models
from django.conf import settings

class JournalEntry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='entries')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    detected_themes = models.JSONField(default=list, blank=True)
    pokemon_song = models.JSONField(default=list, blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.created_at.date()}"
