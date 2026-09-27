from celery import shared_task
from .services import analyze_entry
from entries.models import JournalEntry

@shared_task
def analyze_entry_task(entry_id: int):
    try:
        entry = JournalEntry.objects.get(id=entry_id)
        result = analyze_entry(entry.content)
        entry.detected_themes = result["themes"]
        entry.pokemon_song = result["songs"]
        entry.save()
    except JournalEntry.DoesNotExist:
        pass