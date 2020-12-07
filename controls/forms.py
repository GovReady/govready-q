from django import forms
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Statement, Poam

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

class ImportOSCALComponentForm(forms.Form):

    file = forms.FileField(label="Select OSCAL file (.json)", widget=forms.FileInput(
        attrs={
            'onchange': "fillJSONContent(this);"
        }),
       validators=[FileExtensionValidator(['json'])]
    )
    json_content = forms.CharField(label='OSCAL (JSON)', widget=forms.Textarea(
        attrs={
            "rows": 10,
            "cols": 75,
        }),
    )
