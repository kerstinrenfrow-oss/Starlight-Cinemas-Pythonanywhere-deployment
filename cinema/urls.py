
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('upcoming/', views.upcoming, name='upcoming'),
    path('reservation/', views.reservation, name='reservation'),
    path(
        'confirmation/<int:reservation_id>/',
        views.confirmation,
        name='confirmation'
    ),
    path('myaccount/', views.my_account, name='my_account'),
    path('register/', views.register, name='register'),

    path(
        'myaccount/reservation/<int:reservation_id>/',
        views.reservation_details,
        name='reservation_details'
    ),
    path(
        'myaccount/reservation/<int:reservation_id>/cancel/',
        views.cancel_reservation,
        name='cancel_reservation'
    ),
]
