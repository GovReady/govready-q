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
        if not user.is_anonymous:
            # self.fields['portfolio'].choices = [(x.pk, x.title) for x in Portfolio.get_all_readable_by(user).order_by('title')]
            self.fields['portfolio'].choices = [(x.pk, x.title) for x in user.portfolio_list().order_by('title')]
            self.fields['portfolio'].label = "Add project to portfolio"
            self.fields['portfolio'].label_suffix = "    "
            self.fields['portfolio'].help_text = ""

class PortfolioForm(ModelForm):

    class Meta:
        model = Portfolio
        fields = ['title', 'description' ]

    def clean(self):
        """Extend clean to validate portfolio name is not reused."""
        cd = self.cleaned_data
        # Validate portfolio name does not exist case insensitive only when creating a new portfolio
        if Portfolio.objects.filter(title__iexact=cd['title']).exists() and self.data.get('action') == 'newportfolio':
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
