from django import forms
from django.forms import ModelForm

from .models import Portfolio


class PortfolioForm(ModelForm):

    class Meta:
        model = Portfolio
        fields = ['title', 'description']


class PortfolioSignupForm(ModelForm):

    class Meta:
        model = Portfolio
        fields = ['title']

        labels = {
            "title": "Your personal portfolio will be:",
        }
        help_texts = {
            "title": "Only lowercase letters, digits, and dashes.",
        }
        widgets = {
            "description": forms.HiddenInput(),
            "title": forms.TextInput(attrs={"placeholder": "username"})
        }
