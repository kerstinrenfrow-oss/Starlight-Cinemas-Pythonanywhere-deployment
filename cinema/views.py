from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, MovieScreen, Showtime, Reservation, ScreeningSchedule, UserProfile
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Sum
from datetime import datetime, timedelta
from decimal import Decimal
from .forms import RegistrationForm
from django.contrib.auth import login

# Create your views here.

def index(request):
    """View function for the home page of the site."""
    num_movies = Movie.objects.all().count()
    showtimes = Showtime.objects.all()
    movies = Movie.objects.all()
    num_showtimes = Showtime.objects.all().count()
    num_reservations = Reservation.objects.all().count()
    num_screens = MovieScreen.objects.all().count()
    today = timezone.localdate()
    selected_movie = int(request.GET.get('movie_id') or 0)
    selected_date = request.GET.get('show_date', None)
    end_date = today + timedelta(days=7)
    for schedule in ScreeningSchedule.objects.all():
        for day in range(8):
            date = today + timedelta(days=day)

            Showtime.objects.get_or_create(
                movie=schedule.movie,
                screen=schedule.screen,
                show_date=date,
                show_time=schedule.show_time
            )
    showtimes = Showtime.objects.filter(
        show_date__range=[today, end_date]
    ).order_by('show_date', 'show_time')

    dates = sorted(set(showtimes.values_list('show_date', flat=True)))

    if selected_movie and selected_date:
        showtimes = showtimes.filter(
            movie=selected_movie,
            show_date=selected_date
        )

    context = {
               'movies': movies,
               'showtimes': showtimes,
               'num_movies': num_movies,
               'num_showtimes': num_showtimes,
               'num_reservations': num_reservations,
               'num_screens': num_screens,
               'dates': dates,
               'selected_movie': selected_movie,
               'selected_date': selected_date,
    }
    return render(request, 'index.html', context)

def aboutus(request):
    """View function for the about page of the site."""
    return render(request, 'aboutus.html')

def upcoming(request):
    return render(request, 'upcoming.html')


@login_required
def reservation(request):
    # Get the selected showtime from the homepage or reservation form
    if request.method == "POST":
        showtime_id = request.POST.get("show_time")
    else:
        showtime_id = request.GET.get("show_time")

    if not showtime_id:
        return render(request, "reservation.html", {
            "error": "Please select a showtime before making a reservation."
        })

    showtime = get_object_or_404(
        Showtime.objects.select_related("movie", "screen"),
        pk=showtime_id
    )

    # Verify that the screening is not in the past
    screening_datetime = timezone.make_aware(
        datetime.combine(
            showtime.show_date,
            showtime.show_time
        ),
        timezone.get_current_timezone()
    )

    if screening_datetime <= timezone.now():
        return render(request, "reservation.html", {
            "error": "This screening is no longer available."
        })
    reserved_tickets = Reservation.objects.filter(
        showtime=showtime
    ).aggregate(total=Sum("ticket_quantity"))['total'] or 0

    available_seats = max(0, showtime.screen.capacity - reserved_tickets)
    ticket_price = Decimal("10.00")

    context = {
        "showtime": showtime,
        "movie": showtime.movie,
        "screen": showtime.screen,
        "ticket_price": ticket_price,
        "available_seats": available_seats,
        "quantity": 1,
        "first_name": "",
        "last_name": "",
        "email": "",
    }

    # Process reservation form submission
    if request.method == "POST":
        quantity_raw = request.POST.get("quantity", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        context.update({
            "quantity": quantity_raw,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        })

        try:
            quantity = int(quantity_raw)
        except (ValueError, TypeError):
            context["error"] = "Please select a valid ticket quantity."
            return render(request, "reservation.html", context)

        if quantity < 1:
            context["error"] = "Please enter at least 1 ticket."
            return render(request, "reservation.html", context)

        if quantity > available_seats:
            context["error"] = f"Only {available_seats} seats are available for this showtime."
            return render(request, "reservation.html", context)

        if not first_name or not last_name or not email:
            context["error"] = "Please complete all contact information."
            return render(request, "reservation.html", context)

        if len(first_name) > 100 or len(last_name) > 100:
            context["error"] = "Names must be 100 characters or fewer."
            return render(request, "reservation.html", context)

        try:
            validate_email(email)
        except ValidationError:
            context["error"] = "Please enter a valid email address."
            return render(request, "reservation.html", context)

        # Calculate total on the server for accuracy
        total_price = ticket_price * quantity

        # Save the reservation to the local database
        with transaction.atomic():
            booking = Reservation.objects.create(
                showtime=showtime,
                user=request.user,
                ticket_quantity=quantity,
                ticket_price=int(ticket_price),
                total_price=total_price,
                reservation_date=timezone.now(),
                first_name=first_name,
                last_name=last_name,
                email=email,
            )

        # Redirect to the confirmation page
        return redirect(
            "confirmation",
            reservation_id=booking.pk
        )

    return render(request, "reservation.html", context)



@login_required
def confirmation(request, reservation_id):
    booking = get_object_or_404(
        Reservation.objects.select_related(
            "showtime__movie",
            "showtime__screen"
        ),
        pk=reservation_id,
        user=request.user
    )

    confirmation_number = (
        f"SC{booking.reservation_date:%m%d%Y}-{booking.pk:04d}"
    )

    context = {
        "booking": booking,
        "movie": booking.showtime.movie,
        "showtime": booking.showtime,
        "screen": booking.showtime.screen,
        "confirmation_number": confirmation_number,
    }

    return render(request, "confirmation.html", context)

def build_confirmation_number(booking):
    """Same format the confirmation page uses, e.g. SC10152026-0007."""
    return f"SC{booking.reservation_date:%m%d%Y}-{booking.pk:04d}"


def screening_has_started(showtime):
    """True once the movie's date and time have passed."""
    screening_datetime = timezone.make_aware(
        datetime.combine(showtime.show_date, showtime.show_time),
        timezone.get_current_timezone()
    )
    return screening_datetime <= timezone.now()


@login_required
def my_account(request):
    # Phone number lives in UserProfile (created the first time it is needed)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "")
        request.user.last_name = request.POST.get("last_name", "")
        request.user.email = request.POST.get("email", "")
        request.user.save()

        profile.phone = request.POST.get("phone", "")
        profile.save()

    # Only the reservations that belong to the signed-in user
    reservations = (
        Reservation.objects
        .filter(user=request.user)
        .select_related("showtime__movie", "showtime__screen")
        .order_by("showtime__show_date", "showtime__show_time")
    )

    for booking in reservations:
        booking.confirmation_number = build_confirmation_number(booking)

    context = {
        "profile": profile,
        "reservations": reservations,
    }

    return render(request, "myaccount.html", context)


@login_required
def reservation_details(request, reservation_id):
    # user=request.user stops people from viewing someone else's reservation
    booking = get_object_or_404(
        Reservation.objects.select_related(
            "showtime__movie",
            "showtime__screen"
        ),
        pk=reservation_id,
        user=request.user
    )

    context = {
        "booking": booking,
        "movie": booking.showtime.movie,
        "showtime": booking.showtime,
        "screen": booking.showtime.screen,
        "confirmation_number": build_confirmation_number(booking),
        "can_cancel": not screening_has_started(booking.showtime),
    }

    return render(request, "reservation_details.html", context)


@login_required
@require_POST
def cancel_reservation(request, reservation_id):
    booking = get_object_or_404(
        Reservation.objects.select_related("showtime__movie"),
        pk=reservation_id,
        user=request.user
    )

    if screening_has_started(booking.showtime):
        messages.error(
            request,
            "This screening has already started, so the reservation "
            "can no longer be cancelled."
        )
        return redirect("reservation_details", reservation_id=booking.pk)

    movie_title = booking.showtime.movie.movie_title
    booking.delete()

    messages.success(
        request,
        f"Your reservation for {movie_title} has been cancelled."
    )
    return redirect("my_account")

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                UserProfile.objects.create(
                    user=user,
                    phone=form.cleaned_data['phone']
                )

            login(request, user)
            return redirect('my_account')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})