from django import forms

class ExportCSVTemplateSSPForm(forms.Form):

    info_system = forms.CharField(label='"Project Name" exported to column named: ', widget=forms.TextInput(attrs={'class': 'form-control', 'style':'resize:none;width:500px;', 'placeholder': 'Information System'}))
    control_id = forms.CharField(label='"Control ID" exported to column named:', widget=forms.TextInput(attrs={'class': 'form-control', 'style':'resize:none;width:500px;', 'placeholder': 'Control ID'}))
    catalog = forms.CharField(label='"Control Catalog" exported to column named:', widget=forms.TextInput(attrs={'class': 'form-control', 'style':'resize:none;width:500px;', 'placeholder': 'Control Set Version Number'}))
    shared_imps = forms.CharField(label='"Implementation Statement (Library)" exported to column named:', widget=forms.TextInput(attrs={'class': 'form-control', 'style':'resize:none;width:500px;', 'placeholder': 'Shared Implementation Details'}))
    private_imps = forms.CharField(label='"Implementation Statement (Local)" exported to column named:', widget=forms.TextInput(attrs={'class': 'form-control', 'style':'resize:none;width:500px;', 'placeholder': 'Private Implementation Details'}))
    oscal_format = forms.BooleanField(
        label='Would you like to have the Control ID data in OSCAL format?',
        required=False
    )