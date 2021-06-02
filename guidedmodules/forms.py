from django import forms


class ExportCSVTemplateSSPForm(forms.Form):

    info_system = forms.CharField(label='Column Header for `Program Name`', widget=forms.Textarea(attrs={"rows":1, "cols":3, 'style':'resize:none;', 'placeholder': 'Information System or Program Name (e.g. GovReady Project Name)'}))
    control_id = forms.CharField(label='Column Header for `Control ID`', widget=forms.Textarea(attrs={"rows":1, "cols":3, 'style':'resize:none;', 'placeholder': 'Control Number (e.g. GovReady Control Ids)'}))
    catalog = forms.CharField(label='Column Header for `Control Catalog`', widget=forms.Textarea(attrs={"rows":1, "cols":3, 'style':'resize:none;', 'placeholder': 'Control Set Version Number (e.g. GovReady Control Catalog)'}))
    shared_imps = forms.CharField(label='Column Header for `Shared Implementation Details`', widget=forms.Textarea(attrs={"rows":1, "cols":3, 'style':'resize:none;', 'placeholder': 'Shared Implementation Details (e.g. GovReady full inherits from...)'}))
    private_imps = forms.CharField(label='Column Header for `Control Implementation Statements`', widget=forms.Textarea(attrs={"rows":1, "cols":3, 'style':'resize:none;', 'placeholder': 'Private Implementation Details (e.g. GovReady does this...)'}))