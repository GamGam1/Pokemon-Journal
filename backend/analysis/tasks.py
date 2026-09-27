from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from .services import analyze_entry
from entries.models import JournalEntry

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_entry_task(self, entry_id: int):
    try:
        entry = JournalEntry.objects.get(id=entry_id)
        entry.processing_status = 'processing'
        entry.save()

        result = analyze_entry(entry.content)

        entry.detected_themes = result["themes"]
        entry.pokemon_song = result["songs"]
        entry.processing_status = 'done'
        entry.save()
       
    except JournalEntry.DoesNotExist:
        pass
    except Exception as exc:
        try:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)
        except MaxRetriesExceededError:
            entry.processing_status = 'failed'
            entry.save()