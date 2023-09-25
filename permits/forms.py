from datetime import datetime

from django import forms

from users.models import Client
from .models import (
    Requirement,
    PermitApplication,
    Status,
    PermitType,
    TransportEntry,
    CollectionEntry
)


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


class TransportEntryForm(forms.ModelForm):

    class Meta:
        model = TransportEntry
        fields = ('sub_species', 'quantity')

    def clean_sub_species(self):
        sub_species = self.cleaned_data.get('sub_species')
        application: PermitApplication = self.instance.permit_application
        existing_transport = application.requested_species_to_transport.filter(
            sub_species=sub_species).first()
        if existing_transport is not None and (existing_transport.id != self.instance.id):
            raise forms.ValidationError(
                'This species has been chosen for transport already.')
        return sub_species


class PermitApplicationForm(forms.ModelForm):

    class Meta:
        model = PermitApplication
        fields = ('permit_type', 'client')
        widgets = {
            'client': forms.HiddenInput()
        }

    def clean_permit_type(self):
        permit_type = self.cleaned_data.get('permit_type')
        client: Client = self.initial.get('client')

        if permit_type == PermitType.LTP:
            has_needed_permits = client.current_wcp and client.current_wfp
            if not has_needed_permits:
                return forms.ValidationError(
                    "You currently don't have the needed permits WFP or WCP.")

        in_progress_application = PermitApplication.objects.filter(
            client=client, permit_type=permit_type).exclude(status=Status.RELEASED).first()
        if in_progress_application:
            return forms.ValidationError(
                "You currently have an in progress application for this permit type.")

        return permit_type


class PermitApplicationUpdateForm(forms.ModelForm):

    class Meta:
        model = PermitApplication
        fields = ('transport_date',
                  'names_and_addresses_of_authorized_collectors_or_trappers')
        widgets = {
            'transport_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_transport_date(self):
        transport_date = self.cleaned_data.get('transport_date')
        if transport_date is not None and (transport_date <= datetime.now().date()):
            raise forms.ValidationError(
                'The transport date must be a future date.')
        return transport_date


class CollectionEntryForm(forms.ModelForm):

    class Meta:
        model = CollectionEntry
        fields = ('sub_species', 'quantity')

    def clean_sub_species(self):
        sub_species = self.cleaned_data.get('sub_species')
        application: PermitApplication = self.instance.permit_application
        existing_entry = application.requested_species.filter(
            sub_species=sub_species).first()
        if existing_entry is not None and (existing_entry.id != self.instance.id):
            print('Not oklang', existing_entry)
            raise forms.ValidationError(
                'This species has been chosen.')
        print('Oklang')
        return sub_species


RequirementFormSet = forms.inlineformset_factory(
    PermitApplication, Requirement, form=RequirementForm, extra=1)

TransportEntryFormSet = forms.inlineformset_factory(
    PermitApplication, TransportEntry, form=TransportEntryForm, extra=1)

CollectionEntryFormSet = forms.inlineformset_factory(
    PermitApplication, CollectionEntry, form=CollectionEntryForm, extra=1)
