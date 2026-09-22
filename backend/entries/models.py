from django.db import models
from django.conf import settings

class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='entries')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    detected_themes = models.JSONField(default=list, blank=True)
    pokemon_song = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {self.created_at.date()}"
