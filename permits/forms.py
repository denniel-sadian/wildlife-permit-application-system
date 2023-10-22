from datetime import datetime

from ajax_select.fields import AutoCompleteSelectField

from django.db.models import Q
from django import forms

from animals.models import (
    SubSpecies
)

from users.models import Client

from .models import (
    UploadedRequirement,
    PermitApplication,
    Status,
    PermitType,
    TransportEntry,
    CollectionEntry,
    WildlifeCollectorPermit,
    PermittedToCollectAnimal
)


class TransportEntryBaseForm(forms.ModelForm):

    class Meta:
        model = TransportEntry
        fields = ('sub_species', 'quantity', 'description')

    def clean_sub_species(self):
        # Make sure double transport for the same species is forbidden
        sub_species = self.cleaned_data.get('sub_species')
        application: PermitApplication = self.instance.permit_application
        existing_transport = application.requested_species_to_transport.filter(
            sub_species=sub_species).first()
        if existing_transport is not None and (existing_transport.id != self.instance.id):
            raise forms.ValidationError(
                'This species has been chosen for transport already.')

        # Make sure only collected species are chosen for transport
        allowed = SubSpecies.objects.filter(Q(species_permitted__wcp__client=application.client) &
                                            Q(common_name__exact=sub_species.common_name)).first()
        if not allowed:
            raise forms.ValidationError(
                'The client is not allowed to transport this species.')

        return sub_species

    def clean_quantity(self):
        sub_species = self.cleaned_data.get('sub_species')
        quantity = self.cleaned_data.get('quantity')

        wcp: WildlifeCollectorPermit = self.instance.permit_application.client.current_wcp
        if wcp:
            permitted_species: PermittedToCollectAnimal = wcp.allowed_species.filter(
                sub_species=sub_species).first()
            if permitted_species:
                if quantity > permitted_species.quantity:
                    raise forms.ValidationError(
                        f'The client is only allowed to transport a quanity of {permitted_species.quantity} '
                        f'for the species {sub_species}.')
        else:
            raise forms.ValidationError(
                'The client does not have a WCP yet.')

        return quantity


class UploadedRequirementForm(forms.ModelForm):
    requirement = AutoCompleteSelectField(
        'needed-requirements', required=True, help_text=None)

    class Meta:
        model = UploadedRequirement
        fields = ('requirement', 'uploaded_file')

    def clean_requirement(self):
        requirement = self.cleaned_data.get('requirement')
        application: PermitApplication = self.instance.permit_application
        existing_requirement = application.requirements.filter(
            requirement=requirement).first()
        if existing_requirement is not None and (existing_requirement.id != self.instance.id):
            raise forms.ValidationError(
                'The requirement has been uploaded already.')
        return requirement


class TransportEntryForm(TransportEntryBaseForm):
    sub_species = AutoCompleteSelectField(
        'permitted-subspecies', required=True, help_text=None, label='Species')


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
            client=client, permit_type=permit_type).exclude(
                status__in=[Status.RELEASED, Status.EXPIRED, Status.USED]).first()
        if in_progress_application:
            return forms.ValidationError(
                "You currently have an in progress application for this permit type.")

        return permit_type


class PermitApplicationUpdateForm(forms.ModelForm):

    class Meta:
        model = PermitApplication
        fields = ('transport_date', 'transport_location',
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
    sub_species = AutoCompleteSelectField(
        'subspecies', required=True, help_text=None, label='Species')

    class Meta:
        model = CollectionEntry
        fields = ('sub_species', 'quantity')

    def clean_sub_species(self):
        sub_species = self.cleaned_data.get('sub_species')
        application: PermitApplication = self.instance.permit_application
        existing_entry = application.requested_species.filter(
            sub_species=sub_species).first()
        if existing_entry is not None and (existing_entry.id != self.instance.id):
            raise forms.ValidationError(
                f'{sub_species} has been chosen already.')
        return sub_species
