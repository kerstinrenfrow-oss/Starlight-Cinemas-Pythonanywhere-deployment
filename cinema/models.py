from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Movie(models.Model):
    movie_id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=100)
    movie_summary = models.CharField(max_length=800)
    movie_genre = models.CharField(max_length=100)
    movie_image = models.ImageField(upload_to='movies/')
    movie_rating = models.CharField(max_length=10)
    movie_director = models.CharField(max_length=100)
    movie_release_date = models.DateField()
    movie_runtime = models.IntegerField()

    def __str__(self):
        return self.movie_title


class MovieScreen(models.Model):
    screen_id = models.AutoField(primary_key=True)
    theater_number = models.IntegerField()
    capacity = models.IntegerField()

    def __str__(self):
        return f"Theater {self.theater_number}"

class Showtime(models.Model):
    showtime_id = models.AutoField(primary_key=True)
    show_date = models.DateField()
    show_time = models.TimeField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screen = models.ForeignKey(MovieScreen, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.movie.movie_title} - Theater {self.screen.theater_number} - {self.show_date} - {self.show_time}"

class ScreeningSchedule(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screen = models.ForeignKey(MovieScreen, on_delete=models.CASCADE)
    show_time = models.TimeField()

    def __str__(self):
        return f"{self.movie.movie_title} - Theater {self.screen.theater_number} - {self.show_time}"

class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    ticket_quantity = models.IntegerField()
    ticket_price = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    reservation_date = models.DateTimeField()
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

