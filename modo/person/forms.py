from django import forms
from django.core import validators
from .models import Human
from django.utils.translation import ugettext as _


class SignupForm(forms.ModelForm):
    email = forms.EmailField(label=_('email'),
                             validators=[validators.EmailValidator],
                             error_messages={
                                 'invalid': 'Please enter a valid email address.\n',
                                 'unique': 'User with this email already exists.\n',
                             })
    password = forms.CharField(label=_('password'),
                               max_length=200,
                               widget=forms.PasswordInput())
    first_name = forms.CharField(label=_('first name'),
                                 max_length=100,
                                 required=True)
    last_name = forms.CharField(label=_('last name'),
                                max_length=100,
                                required=True)

    class Meta:
        model = Human
        widgets = {'password': forms.PasswordInput()}
        fields = ('email', 'password', 'first_name', 'last_name')
