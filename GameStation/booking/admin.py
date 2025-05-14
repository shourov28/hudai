from datetime import timedelta
from django.contrib import admin
from .models import Game, Booking, Payment

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'category']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'game', 'duration', 'start_time', 'get_end_time', 'renewed']
    list_filter = ['duration', 'start_time', 'game']

    def get_end_time(self, obj):
        # Assuming your `duration` is a string like '1H', '2H', etc.
        duration_map = {
            '20M': timedelta(minutes=20),
            '1H': timedelta(hours=1),
            '2H': timedelta(hours=2),
            '3H': timedelta(hours=3),
        }
        # Get the duration delta based on the selected option
        duration_delta = duration_map.get(obj.duration, timedelta(hours=1))
        # Calculate the end time
        end_time = obj.start_time + duration_delta
        return end_time.strftime('%Y-%m-%d %H:%M')  # Format as you like

    get_end_time.short_description = 'End Time'  # Customize the column name

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'timestamp']
    list_filter = ['timestamp']
