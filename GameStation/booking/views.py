from django.shortcuts import render, redirect, get_object_or_404
from .models import Game, Booking, Payment
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from .forms import SignUpForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from datetime import timedelta
from datetime import datetime
from django.utils.dateparse import parse_datetime


def game_list(request):
    games = Game.objects.all()
    return render(request, 'booking/game_list.html', {'games': games})

def calculate_price(duration, mode):
    if mode == 'story':
        if duration == '20M':
            return None  # Invalid for story mode
        return 100 * int(duration[0])  # 1H = 1, 2H = 2, 3H = 3

    if mode == 'single':
        if duration == '20M':
            return 25
        elif duration == '1H':
            return 80
        elif duration == '2H':
            return 160
        elif duration == '3H':
            return 240

    if mode == 'multi':
        if duration == '20M':
            return 40
        elif duration == '1H':
            return 120
        elif duration == '2H':
            return 240
        elif duration == '3H':
            return 360

    return None  # Invalid combination

@login_required
def book_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)

    if request.method == 'POST':
        duration = request.POST.get('duration')
        mode = request.POST.get('mode')
        start_time_str = request.POST.get('start_time')
        # Parse the datetime from input
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M")

        # Calculate end time
        duration_map = {
            '20M': timedelta(minutes=20),
            '1H': timedelta(hours=1),
            '2H': timedelta(hours=2),
            '3H': timedelta(hours=3),
        }
        duration_delta = duration_map.get(duration, timedelta(hours=1))
        end_time = start_time + duration_delta

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            game=game,
            start_time__lt=end_time,
            start_time__gt=start_time - duration_delta
        ).count()

        if overlapping_bookings >= 3:
            messages.error(request, "This time slot is full. Please try another time.")
            return redirect('book_game', game_id=game.id)

        # Calculate price
        price = calculate_price(duration, mode)
        if price is None:
            messages.error(request, "Invalid mode and duration combination.")
            return redirect('book_game', game_id=game.id)

        # Proceed with booking
        booking = Booking.objects.create(
            user=request.user,
            game=game,
            duration=duration,
            start_time=start_time,
            renewed=False,
            mode=mode
        )

        Payment.objects.create(booking=booking, amount=price)

        messages.success(request, f"Successfully booked '{game.title}' in {mode} mode!")
        return redirect('my_bookings')

    return render(request, 'booking/book_game.html', {'game': game})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'booking/my_bookings.html', {'bookings': bookings})

@login_required
def renew_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.is_active() and not booking.renewed:
        booking.start_time = timezone.now()
        booking.renewed = True
        booking.save()
        Payment.objects.create(booking=booking, amount=booking.price())
        messages.success(request, "Booking renewed!")
    else:
        messages.error(request, "Renewal not allowed.")
    return redirect('my_bookings')

@login_required
def admin_summary(request):
    if not request.user.is_staff:
        return redirect('game_list')

    today = timezone.now().date()

    # Filter by booking start_time, not payment timestamp
    income = Payment.objects.filter(booking__start_time__date=today).aggregate(total=Sum('amount'))['total'] or 0

    # Get bookings that are scheduled for today
    users = Booking.objects.filter(start_time__date=today).select_related('user')

    return render(request, 'booking/admin_summary.html', {'income': income, 'users': users})
@login_required
def payment_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking/payment_confirmation.html', {'booking': booking})



def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            return redirect('game_list')
    else:
        form = SignUpForm()
    return render(request, 'booking/signup.html', {'form': form})
