from django.contrib import admin
from .models import Movie, MovieScreen, Showtime, Reservation, ScreeningSchedule

admin.site.register(Movie)
admin.site.register(MovieScreen)
admin.site.register(Showtime)
admin.site.register(Reservation)
admin.site.register(ScreeningSchedule)

# Register your models here.
