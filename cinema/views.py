from django.shortcuts import render
from .models import Movie, MovieScreen, Showtime, Reservation

# Create your views here.


def index(request):
    """View function for the home page of the site."""
    num_movies = Movie.objects.all().count()
    movies = Movie.objects.all()
    num_showtimes = Showtime.objects.all().count()
    num_reservations = Reservation.objects.all().count()
    num_screens = MovieScreen.objects.all().count()

    context = {
               'movies': movies,
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