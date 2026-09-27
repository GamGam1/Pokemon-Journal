from django.core.management.base import BaseCommand
from entries.models import JournalEntry
from analysis.services import analyze_entry


class Command(BaseCommand):
    help = 'ETL pipeline: analyze all unprocessed journal entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reprocess-all',
            action='store_true',
            help='Reprocess all entries, even ones already analyzed',
        )

    def handle(self, *args, **options):
        if options['reprocess_all']:
            entries = JournalEntry.objects.all()
            self.stdout.write('Reprocessing ALL entries...')
        else:
            # Only entries with empty themes (unprocessed)
            entries = JournalEntry.objects.filter(detected_themes=[])
            self.stdout.write('Processing unprocessed entries only...')

        total = entries.count()
        self.stdout.write(f'Found {total} entries to process.')

        success = 0
        failed = 0

        for entry in entries:
            try:
                result = analyze_entry(entry.content)
                entry.detected_themes = result["themes"]
                entry.pokemon_song = result["songs"]
                entry.save()
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Entry {entry.id}: {result["themes"]}')
                )
                success += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Entry {entry.id} failed: {e}')
                )
                failed += 1

        self.stdout.write(f'\nDone. {success} succeeded, {failed} failed.')