from django.shortcuts import render
from .models import Movie, MovieScreen, Showtime, Reservation, ScreeningSchedule
from django.utils import timezone
from datetime import timedelta

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
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    for schedule in ScreeningSchedule.objects.all():
        for day in range(7):
            date = monday + timedelta(days=day)

            Showtime.objects.get_or_create(
                movie=schedule.movie,
                screen=schedule.screen,
                show_date=date,
                show_time=schedule.show_time
            )
    showtimes = Showtime.objects.filter(
        show_date__range=[monday, sunday]
    ).order_by('show_date', 'show_time')

    context = {
               'movies': movies,
               'showtimes': showtimes,
               'num_movies': num_movies,
               'num_showtimes': num_showtimes,
               'num_reservations': num_reservations,
               'num_screens': num_screens

    }
    return render(request, 'index.html', context)

def aboutus(request):
    """View function for the about page of the site."""
    return render(request, 'aboutus.html')

def upcoming(request):
    return render(request, 'upcoming.html')