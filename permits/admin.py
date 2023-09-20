from django.contrib import admin

from .models import (
    WildlifeFarmPermit,
    WildlifeCollectorPermit,
    PermittedToCollectAnimal,
    PermitApplication,
    Requirement,
    TransportEntry,
    RequirementList,
    RequirementItem
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


class TransportEntryInline(admin.TabularInline):
    model = TransportEntry
    extra = 1
    verbose_name_plural = 'Transport Entries'


@admin.register(PermitApplication)
class PermitApplicationAdmin(admin.ModelAdmin):
    list_display = ('no', 'permit_type', 'client', 'status', 'created_at')
    fieldsets = (
        ('Common', {
            'fields': ('no', 'client', 'permit_type', 'status')
        }),
        ('Local Transport Permit', {
            'fields': ('transport_date',)
        }),
        ("Wildlife Collector's Permit", {
            'fields': ('names_and_addresses_of_authorized_collectors_or_trappers',)
        })
    )
    inlines = (RequirementInline, TransportEntryInline)


class RequirementItemInline(admin.StackedInline):
    model = RequirementItem
    extra = 1


@admin.register(RequirementList)
class RequirementListAdmin(admin.ModelAdmin):
    inlines = (RequirementItemInline,)
