from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Exists
from django.db.models import Q


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
        cd = self.cleaned_data
        # Validate portfolio name does not exist (case insensitive) only when creating a new portfolio
        if Portfolio.objects.filter(title__iexact=cd['title']).exists() and self.data.get('action') == 'newportfolio':
            raise ValidationError("Portfolio name {} not available.".format(cd['title']))
        return cd

class AccountSettingsForm(ModelForm):

    class Meta:
        model = User
        fields = ['name', 'email', 'title']

    def clean(self):
        cd = self.cleaned_data
        # errors = {}
        if User.objects.filter(Q(name__iexact=cd['name']) & ~Q(id=self.instance.id)).exists():
            self.add_error('name', "Display name {} not available.".format(cd['name']))
        if User.objects.filter(Q(email__iexact=cd['email']) & ~Q(email=self.instance.email)).exists():
            self.add_error('email', "Email {} not available.".format(cd['email']))
        return cd
