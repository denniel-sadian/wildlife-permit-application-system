from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest

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


class TransportEntryInline(admin.TabularInline):
    fields = ('sub_species', 'quantity')
    model = TransportEntry
    extra = 1
    verbose_name_plural = 'Transport Entries'


class CollectionEntryInline(admin.TabularInline):
    fields = ('sub_species', 'quantity')
    model = CollectionEntry
    extra = 1
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
