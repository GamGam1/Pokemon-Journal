from celery import shared_task
from django.contrib.auth import get_user_model
from collections import Counter
from .models import JournalEntry
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@shared_task
def generate_weekly_report():
    one_week_ago = timezone.now() - timedelta(days=7)
    users = User.objects.all()

    for user in users:
        entries = JournalEntry.objects.filter(
            user=user,
            created_at__gte=one_week_ago
        )

        if not entries.exists():
            continue

        all_themes = []
        for entry in entries:
            all_themes.extend(entry.detected_themes)

        theme_counts = Counter(all_themes)
        top_themes = theme_counts.most_common(3)

        print(f"Weekly report for {user.username}:")
        print(f"  Entries this week: {entries.count()}")
        print(f"  Top themes: {top_themes}")