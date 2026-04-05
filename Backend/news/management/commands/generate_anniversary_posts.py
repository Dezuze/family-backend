from django.core.management.base import BaseCommand

from news.services import ensure_daily_anniversary_posts


class Command(BaseCommand):
    help = 'Generate today\'s birthday, death anniversary, and marriage anniversary posts.'

    def handle(self, *args, **options):
        ensure_daily_anniversary_posts()
        self.stdout.write(self.style.SUCCESS('Anniversary post generation completed.'))
