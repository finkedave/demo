from django.core.management.base import BaseCommand
from ... models import Game, Session


class Command(BaseCommand):
    """
    Django management command for finding dependency file discrepancies and optionally fixing them.
    """

    def handle(self, *args, **options):
        Game.objects.all().delete()
        Session.objects.all().delete()
