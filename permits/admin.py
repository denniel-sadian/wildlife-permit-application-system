from typing import Any
from datetime import datetime
from datetime import timedelta

from django.urls import reverse_lazy
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.widgets import AdminDateWidget
from django.http.request import HttpRequest
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.conf import settings

from django import forms

from payments.models import (
    PaymentOrder
)

from .forms import (
    TransportEntryBaseForm
)

from .models import (
    Permit,
    WildlifeFarmPermit,
    WildlifeCollectorPermit,
    LocalTransportPermit,
    PermittedToCollectAnimal,
    PermitApplication,
    PermitType,
    UploadedRequirement,
    TransportEntry,
    Requirement,
    RequirementList,
    RequirementItem,
    CollectionEntry,
    Remarks,
    Status,
    Inspection
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


class UploadedRequirementInline(admin.StackedInline):
    model = UploadedRequirement
    extra = 1
    autocomplete_fields = ('requirement',)


class TransportEntryForm(TransportEntryBaseForm):
    pass


class TransportEntryInline(admin.TabularInline):
    fields = ('sub_species', 'quantity')
    model = TransportEntry
    form = TransportEntryForm
    extra = 1
    autocomplete_fields = ('sub_species',)
    verbose_name_plural = 'Transport Entries'


@admin.register(LocalTransportPermit)
class LocalTransportPermitAdmin(admin.ModelAdmin):
    list_display = ('permit_no', 'status', 'client')
    inlines = (TransportEntryInline,)
    change_form_template = 'permits/admin/permit_changeform.html'


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
    list_display = ('no', 'permit_type', 'client', 'status',
                    'submittable', 'created_at')
    list_filter = ('permit_type', 'status',)
    search_fields = ('no', 'permit_type', 'client__first_name',
                     'client__last_name', 'status')
    autocomplete_fields = ('client',)
    change_form_template = 'permits/admin/application_changeform.html'

    def submittable(self, obj):
        return obj.submittable

    submittable.boolean = True

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
            fields.append('transport_location')
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
            UploadedRequirementInline(self.model, self.admin_site),
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

    def response_change(self, request, obj: PermitApplication):
        if 'generate_payment_order' in request.POST:
            if hasattr(obj, 'paymentorder'):
                self.message_user(
                    request, 'Order of Payment has been created already.', level=messages.WARNING)
                path = f'admin:{obj.paymentorder._meta.app_label}_{obj.paymentorder._meta.model_name}_change'
                return HttpResponseRedirect(reverse_lazy(path, args=[obj.paymentorder.id]))
            if obj.submittable and obj.status != Status.DRAFT:
                payment_order = PaymentOrder(
                    nature_of_doc_being_secured='Wildlife',
                    client=obj.client,
                    permit_application=obj,
                    prepared_by=request.user.subclass
                )
                payment_order.save()
                current_date = datetime.now()
                formatted_date = current_date.strftime("%Y-%m")
                day_part = current_date.day
                no = f'payment-order-{formatted_date}-{day_part}-{payment_order.id}'
                payment_order.no = no
                payment_order.save()
                self.message_user(
                    request, 'Order of Payment has been created.', level=messages.SUCCESS)
                path = f'admin:{payment_order._meta.app_label}_{payment_order._meta.model_name}_change'
                return HttpResponseRedirect(reverse_lazy(path, args=[payment_order.id]))
            else:
                self.message_user(request,
                                  f'Please make sure the permit application is submittable '
                                  f'and no longer on status {Status.DRAFT} (i.e. should be ACCEPTED) '
                                  'before generating the payment order.',
                                  level=messages.ERROR)
                return HttpResponseRedirect('.')

        if 'create_inspection' in request.POST:
            if hasattr(obj, 'inspection'):
                self.message_user(
                    request, 'Inspection has started already.', level=messages.WARNING)
                path = f'admin:{obj.inspection._meta.app_label}_{obj.inspection._meta.model_name}_change'
                return HttpResponseRedirect(reverse_lazy(path, args=[obj.inspection.id]))
            if obj.submittable and obj.status != Status.DRAFT:
                inspection = Inspection(permit_application=obj)
                inspection.save()
                self.message_user(
                    request, 'Please continue editing the inspection record.', level=messages.SUCCESS)
                path = f'admin:{inspection._meta.app_label}_{inspection._meta.model_name}_change'
                return HttpResponseRedirect(reverse_lazy(path, args=[inspection.id]))
            else:
                self.message_user(request,
                                  f'Please make sure the permit application is submittable '
                                  f'and no longer on status {Status.DRAFT} (i.e. should be ACCEPTED) '
                                  'before starting the inspection.',
                                  level=messages.ERROR)
                return HttpResponseRedirect('.')

        if 'generate_permit' in request.POST:
            if obj.permit is None:
                if obj.permit_type == PermitType.LTP:
                    ltp = LocalTransportPermit(
                        status=Status.DRAFT,
                        client=obj.client,
                        valid_until=timezone.now()+timedelta(days=settings.DAYS_VALID),
                        wfp=obj.client.current_wfp,
                        wcp=obj.client.current_wcp,
                        transport_location=obj.transport_location,
                        transport_date=obj.transport_date
                    )
                    ltp.save()
                    formatted_date = datetime.now().strftime("%Y-%m")
                    day_part = datetime.now().day
                    ltp.permit_no = f'PMDQ-{obj.permit_type}-{formatted_date}-{day_part}-{ltp.id}'
                    ltp.save()
                    for i in obj.requested_species_to_transport.all():
                        i.ltp = ltp
                        i.save()
                    obj.permit = Permit.objects.select_subclasses().get(id=ltp.id)
                    obj.save()

        return super().response_change(request, obj)


class RequirementItemInline(admin.TabularInline):
    model = RequirementItem
    extra = 1
    autocomplete_fields = ('requirement',)


@admin.register(RequirementList)
class RequirementListAdmin(admin.ModelAdmin):
    inlines = (RequirementItemInline,)


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('code',)
    search_fields = ('code', 'label')


class InspectionForm(forms.ModelForm):
    scheduled_date = forms.DateField(required=True, widget=AdminDateWidget())

    class Meta:
        model = Inspection
        fields = ('permit_application', 'scheduled_date',
                  'inspecting_officer', 'report_file')

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date is not None and (scheduled_date < datetime.now().date()):
            raise forms.ValidationError('The date is from the past.')
        return scheduled_date


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('permit_application', 'scheduled_date')
    autocomplete_fields = ('permit_application', 'inspecting_officer')
    form = InspectionForm
    change_form_template = 'permits/admin/inspection_changeform.html'
