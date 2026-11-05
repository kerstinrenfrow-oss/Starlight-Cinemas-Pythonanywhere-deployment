from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('upcoming/', views.upcoming, name='upcoming'),
    path('reservation/', views.reservation, name='reservation'),
]