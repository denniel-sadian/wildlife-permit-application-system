from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest

from django.db.models import Q
from django import forms

from animals.models import (
    SubSpecies
)

from .models import (
    WildlifeFarmPermit,
    WildlifeCollectorPermit,
    PermittedToCollectAnimal,
    PermitApplication,
    PermitType,
    Requirement,
    TransportEntry,
    RequirementList,
    RequirementItem,
    CollectionEntry,
    Remarks
)


@admin.register(WildlifeFarmPermit)
class WildlifeFarmPermitAdmin(admin.ModelAdmin):
    list_display = ('permit_no', 'status', 'client')


class PermittedToCollectAnimalInline(admin.TabularInline):
    model = PermittedToCollectAnimal
    extra = 1


@admin.register(WildlifeCollectorPermit)
class WildlifeCollectorPermitAdmin(admin.ModelAdmin):
    list_display = ('permit_no', 'status', 'client')
    inlines = (PermittedToCollectAnimalInline,)


class RequirementInline(admin.StackedInline):
    model = Requirement
    extra = 1
    verbose_name_plural = 'Submitted Requirements'


class TransportEntryForm(forms.ModelForm):

    class Meta:
        model = TransportEntry
        fields = ('sub_species', 'quantity')

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


class TransportEntryInline(admin.TabularInline):
    fields = ('sub_species', 'quantity')
    model = TransportEntry
    form = TransportEntryForm
    extra = 1
    autocomplete_fields = ('sub_species',)
    verbose_name_plural = 'Transport Entries'


class CollectionEntryInline(admin.TabularInline):
    fields = ('sub_species', 'quantity')
    model = CollectionEntry
    extra = 1
    autocomplete_fields = ('sub_species',)
    verbose_name_plural = 'Collection Entries'


class RemarksInline(admin.TabularInline):
    fields = ('content',)
    model = Remarks
    extra = 0
    verbose_name_plural = 'Remarks'


@admin.register(PermitApplication)
class PermitApplicationAdmin(admin.ModelAdmin):
    list_display = ('no', 'permit_type', 'client', 'status', 'created_at')
    list_filter = ('permit_type', 'status',)
    search_fields = ('no', 'permit_type', 'client__first_name',
                     'client__last_name', 'status')
    autocomplete_fields = ('client',)

    def get_readonly_fields(self, request, obj=None):
        # If obj is None, it means we are adding a new record
        if obj is None:
            return ()
        # Otherwise, when updating an existing record
        return ('client', 'permit_type')

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fields = ['no', 'permit_type', 'status', 'client']

        if obj and obj.permit_type == PermitType.LTP:
            fields.append('transport_date')
        if obj and obj.permit_type == PermitType.WCP:
            fields.append(
                'names_and_addresses_of_authorized_collectors_or_trappers')

        fieldsets = [
            ('Permit Application Data', {
                'fields': fields,
            })
        ]
        return fieldsets

    def get_inline_instances(self, request: HttpRequest, obj: Any | None = ...):
        inlines = [
            RequirementInline(self.model, self.admin_site),
            RemarksInline(self.model, self.admin_site)
        ]

        if obj and obj.permit_type == PermitType.LTP:
            inlines.insert(0, TransportEntryInline(
                self.model, self.admin_site))

        if obj and obj.permit_type == PermitType.WCP:
            inlines.insert(0, CollectionEntryInline(
                self.model, self.admin_site))

        return inlines

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if (isinstance(instance, Remarks)):
                instance.user = request.user
            instance.save()
        formset.save_m2m()


class RequirementItemInline(admin.StackedInline):
    model = RequirementItem
    extra = 1


@admin.register(RequirementList)
class RequirementListAdmin(admin.ModelAdmin):
    inlines = (RequirementItemInline,)
