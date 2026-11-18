from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    username = User._meta.get_field('username').formfield(help_text="")
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.RegexField(
        regex=r'^[0-9]{10}$',
        max_length=10,
        required=True,
        help_text="Enter 10 digits including area code."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone',
                  'username', 'password1', 'password2']