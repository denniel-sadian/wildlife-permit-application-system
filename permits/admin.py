from django.contrib import admin

from .models import (
    WildlifeFarmPermit,
    WildlifeCollectorPermit,
    PermittedToCollectAnimal,
    PermitApplication,
    Requirement,
    TransportEntry
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


class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 1


class TransportEntryInline(admin.TabularInline):
    model = TransportEntry
    extra = 1


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
    )
    inlines = (RequirementInline, TransportEntryInline)
