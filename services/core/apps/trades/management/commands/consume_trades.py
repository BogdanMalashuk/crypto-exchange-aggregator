from django.core.management.base import BaseCommand
from services.core.apps.trades.consumer import run_consumer


class Command(BaseCommand):
    help = "Run Kafka consumer for trade.profit.detected"

    def handle(self, *args, **options):
        run_consumer()
