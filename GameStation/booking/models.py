from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Game(models.Model):
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('adventure', 'Adventure'),
        ('rpg', 'RPG'),
        ('strategy', 'Strategy'),
        ('simulation', 'Simulation'),
        ('puzzle', 'Puzzle'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=GENRE_CHOICES)
    image = models.ImageField(upload_to='games/', blank=True)

    def __str__(self):
        return self.title

class Booking(models.Model):
    DURATION_CHOICES = [
        ('20M', '20 Minutes'),
        ('1H', '1 Hour'),
        ('2H', '2 Hours'),
        ('3H', '3 Hours'),
    ]
    MODE_CHOICES = [
        ('single', 'Single Player'),
        ('multi', 'Multiplayer'),
        ('story', 'Story Mode'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    duration = models.CharField(max_length=3, choices=DURATION_CHOICES)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    start_time = models.DateTimeField()
    renewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.game.title} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"


    @property
    def end_time(self):
        if self.duration == '20M':
            return self.start_time + timedelta(minutes=20)
        hours = int(self.duration[0])
        return self.start_time + timedelta(hours=hours)

    def is_active(self):
        return timezone.now() < self.end_time

    def price(self):
        price_chart = {
            ('SP', '20M'): 25,
            ('SP', '1H'): 80,
            ('MP', '20M'): 40,
            ('MP', '1H'): 120,
            ('ST', '1H'): 100,
        }
        return price_chart.get((self.game.category, self.duration), 0)

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

class DailySummary(models.Model):
    date = models.DateField(auto_now_add=True)
    total_income = models.DecimalField(max_digits=8, decimal_places=2)
