from django.core.management.base import BaseCommand
from django.utils import timezone
from booking.models import Booking

class Command(BaseCommand):
    help = 'Delete expired bookings'

    def handle(self, *args, **kwargs):
        expired = Booking.objects.filter(start_time__lt=timezone.now() - timezone.timedelta(hours=3))
        count = expired.count()
        expired.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} expired bookings.'))
