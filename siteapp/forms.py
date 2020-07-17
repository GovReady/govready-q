from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.db.models import Exists

from .models import Portfolio, Project

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['portfolio']
        portfolio = forms.ChoiceField(choices = [])

        user1 = forms.ChoiceField(choices = [])

    def __init__(self, user, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        # self.fields['portfolio'].choices = [(x.pk, x.title) for x in Portfolio.get_all_readable_by(user).order_by('title')]
        self.fields['portfolio'].choices = [(x.pk, x.title) for x in user.portfolio_list().order_by('title')]

class PortfolioForm(ModelForm):

    class Meta:
        model = Portfolio
        fields = ['title', 'description']

    def clean(self):
        """Extend clean to validate portfolio name is not reused."""
        cd = self.cleaned_data
        # Validate portfolio name does not exist case insensitive
        if Portfolio.objects.filter(title__iexact=cd['title']).exists():
            raise ValidationError("Portfolio name {} not available.".format(cd['title']))
        return cd

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
