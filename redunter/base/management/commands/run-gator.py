from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Runs an alligator worker'

    def handle(self, *args, **options):

        from alligator import Gator, Worker
        gator = Gator(settings.ALLIGATOR_CONN)

        worker = Worker(gator)
        worker.run_forever()
