from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Exists

from .models import Portfolio, Project, User
import logging
logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory


structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()

class EditProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['root_task']
        project_title = forms.CharField(label='Project Title', max_length=200)
        project_version = forms.CharField(label='Project Version', max_length=200)

class AddProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['portfolio']
        portfolio = forms.ChoiceField(choices = [])
        user1 = forms.ChoiceField(choices = [])

    def __init__(self, user, *args, **kwargs):
        super(AddProjectForm, self).__init__(*args, **kwargs)
        if not user.is_anonymous:
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

class AccountSettingsForm(ModelForm):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = User.objects.get(pk=request.user.id)
        self.fields['name'].initial = self.user.name
        self.fields['email'].initial = self.user.email
        self.fields['title'].initial = self.user.title
        self.request = request

    class Meta:
        model = User
        fields = ['name', 'email', 'title' ]

    def clean(self):
        cd = self.cleaned_data
        try:
            # Validate name uniqueness case insensitive
            if self.fields['name'].initial != cd['name'] and User.objects.filter(name__iexact=cd['name']).exists():
                raise ValidationError("User name {} not available.".format(cd['name']))
            # Validate email uniqueness case insensitive
            if  self.fields['email'].initial != cd['email'] and User.objects.filter(name__iexact=cd['email']).exists():
                raise ValidationError("Email name {} not available.".format(cd['name']))
        except Exception as e:
            print(e)
            logger.info(
                event="update_account_settings_fail",
                object={"object": "user", "id": self.user.id, "username": self.user.username},
                user={"id": self.user.id, "username": self.user.username}
            )
            messages.add_message(self.request, messages.ERROR, e)

        return cd
