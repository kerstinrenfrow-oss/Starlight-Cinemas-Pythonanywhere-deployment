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

def reservation(request):
    return render(request, 'reservation.html')