from datetime import datetime

from django import forms

from users.models import Client
from .models import Requirement, PermitApplication, PermitType


class RequirementForm(forms.ModelForm):

    class Meta:
        model = Requirement
        fields = ('requirement_type', 'uploaded_file')

    def clean_requirement_type(self):
        requirement_type = self.cleaned_data.get('requirement_type')
        application: PermitApplication = self.instance.permit_application
        existing_requirement = application.requirements.filter(
            requirement_type=requirement_type).first()
        if existing_requirement is not None and (existing_requirement.id != self.instance.id):
            raise forms.ValidationError('This requirement already exists.')
        return requirement_type


class PermitApplicationForm(forms.ModelForm):

    class Meta:
        model = PermitApplication
        fields = ('permit_type', 'client')
        widgets = {
            'client': forms.HiddenInput()
        }

    def clean_permit_type(self):
        permit_type = self.cleaned_data.get('permit_type')
        if permit_type == PermitType.LTP:
            client: Client = self.initial.get('client')
            has_needed_permits = client.current_wcp and client.current_wfp
            if not has_needed_permits:
                return forms.ValidationError(
                    "You currently don't have the needed permits WFP or WCP.")
        return permit_type


class PermitApplicationUpdateForm(forms.ModelForm):

    class Meta:
        model = PermitApplication
        fields = ('transport_date',)
        widgets = {
            'transport_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_transport_date(self):
        transport_date = self.cleaned_data.get('transport_date')
        if transport_date is not None and (transport_date <= datetime.now().date()):
            raise forms.ValidationError(
                'The transport date must be a future date.')
        return transport_date


RequirementFormSet = forms.inlineformset_factory(
    PermitApplication, Requirement, form=RequirementForm, extra=1)
