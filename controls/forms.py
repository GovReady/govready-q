from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.forms.widgets import HiddenInput
from django.db.models import Exists
import json

from guidedmodules.models import AppSource, AppVersion
from .models import Statement, Poam, Element, Deployment, SystemAssessmentResult
# from jsonfield import JSONField


class StatementPoamForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self._status = kwargs.pop('status', None)
        self._statement_type = kwargs.pop('statement_type', None)
        self._consumer_element = kwargs.pop('consumer_element', None)
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = self._status
        self.fields['statement_type'].initial = self._statement_type
        self.fields['statement_type'].widget = HiddenInput()
        self.fields['consumer_element'].initial = self._consumer_element
        self.fields['consumer_element'].widget = HiddenInput()

    class Meta:
        model = Statement
        fields = ['id', 'statement_type', 'body', 'status', 'consumer_element' ]
        labels = {
            "body": "Description"
        }
        help_texts = {
            "body": "Description of the finding, deficiency, or issue requiring a Plan of Action",
            "status": "The current status of the POAM (e.g., Open, Closed, In progress, ...)",
            "remarks": "Internal remarks about this POAM",
        }
        widgets = {
        }

class PoamForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self._poam_id = kwargs.pop('poam_id', None)
        super().__init__(*args, **kwargs)
        self.fields['weakness_name'].widget.attrs['placeholder'] = ""
        self.fields['controls'].widget.attrs['placeholder'] = "e.g., CM-3, CM-6"
        self.fields['poam_group'].widget.attrs['placeholder'] = "e.g., Epic 23, Log Fixes"
        self.fields['risk_rating_original'].widget.attrs['placeholder'] = "e.g., Low, Moderate, or High"
        self.fields['risk_rating_adjusted'].widget.attrs['placeholder'] = "e.g., Low, Moderate, or High"
        self.fields['weakness_detection_source'].widget.attrs['placeholder'] = ""
        self.fields['remediation_plan'].widget.attrs['placeholder'] = ""
        self.fields['milestones'].widget.attrs['placeholder'] = ""
        self.fields['scheduled_completion_date'].widget.attrs['placeholder'] = "YYYY-MM-DD"

    class Meta:
        model = Poam
        fields = ['weakness_name', 'controls', 'poam_group', 'risk_rating_original', 'risk_rating_adjusted', 'weakness_detection_source', 'remediation_plan', 'milestones', 'scheduled_completion_date']
        # scheduled_completion_date = forms.DateField(widget=forms.DateField)
        widgets = {
            # "scheduled_completion_date": forms.DateField(),
        }
        labels = {
            "poam_group": "Group"
        }

class ElementForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['element_type'] = 'system_element'
        self.fields['element_type'].widget = forms.HiddenInput()

    class Meta:
        model = Element
        fields = ['name', 'full_name', 'description', 'element_type', 'component_type', 'component_state']

    def clean(self):
        """Extend clean to validate element name is not reused."""
        cd = self.cleaned_data
        # Validate element name does not exist case insensitive
        if Element.objects.filter(name__iexact=cd['name']).exists():
            raise ValidationError("Component (aka Element) name {} not available.".format(cd['name']))
        return cd

class ElementEditForm(ModelForm):

    class Meta:
        model = Element
        fields = ['id', 'name', 'description']
class ImportOSCALComponentForm(forms.Form):

    file = forms.FileField(label="Select OSCAL file (.json)",
        widget=forms.FileInput(
            attrs={
                'onchange': "fillJSONContent(this);",
                'accept':'application/json'
            }
        ),
        required=False
    )
    json_content = forms.CharField(label='OSCAL (JSON)', widget=forms.Textarea())
    import_name = forms.CharField(label='Import File Name', widget=forms.HiddenInput(), required=False)

class ImportProjectForm(forms.Form):

    file = forms.FileField(label="Select project file (.json)",
        widget=forms.FileInput(
            attrs={
                'onchange': "fillProjectJSONContent(this);",
                'accept':'application/json'
            }
        ),
        required=False
    )
    json_content = forms.CharField(label='Project (JSON)', widget=forms.Textarea(), help_text="The JSON necessary for importing a project.")

class DeploymentForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['system'] = self.instance.system_id
        self.fields['system'].widget = forms.HiddenInput()
        # Display pretty JSON in JSONfield's text area
        self.initial['inventory_items'] = json.dumps(self.instance.inventory_items, indent=4, sort_keys=True)

    class Meta:
        model = Deployment
        fields = ['name', 'description', 'system', 'inventory_items']

    def clean(self):
        """Validate data."""

        cd = self.cleaned_data
        return cd

    inventory_items = forms.CharField(label='Inventory items (JSON)', required=False, widget=forms.Textarea(),
            help_text="Listing of inventory items in JSON")

class SystemAssessmentResultForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['system'] = self.instance.system_id
        self.fields['system'].widget = forms.HiddenInput()
        # Display pretty JSON in JSONfield's text area
        self.initial['assessment_results'] = json.dumps(self.instance.assessment_results, indent=4, sort_keys=True)

    class Meta:
        model = SystemAssessmentResult
        fields = ['name', 'description', 'system', 'deployment', 'assessment_results']

    def clean(self):
        """Validate data."""

        cd = self.cleaned_data
        return cd

    assessment_results = forms.CharField(label='System assessment result items (JSON)', required=False, widget=forms.Textarea(),
            help_text="Listing of assessment items in JSON")

