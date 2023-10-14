from typing import Any
from datetime import datetime

from django.contrib import admin
from django.contrib import messages
from django.contrib.contenttypes.admin import GenericStackedInline
from django.http.request import HttpRequest
from django.http import HttpResponseRedirect

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
    GratuitousPermit,
    CertificateOfWildlifeRegistration,
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
    Inspection,
    Signature
)


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


class SignatureInline(GenericStackedInline):
    model = Signature
    fields = ('title', 'image', 'person')
    readonly_fields = ('person',)
    extra = 1


class PermitBaseAdmin(admin.ModelAdmin):
    list_display = ('permit_no', 'status', 'client',
                    'issued_date', 'valid_until', 'created_at')
    fields = ('permit_no', 'client', 'status', 'or_no', 'issued_date',
              'valid_until', 'uploaded_file')
    search_fields = ('permit_no',)
    autocomplete_fields = ('client',)
    change_form_template = 'permits/admin/permit_changeform.html'

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if (isinstance(instance, Signature)):
                instance.person = request.user
                instance.title = instance.person.title
            instance.save()
        formset.save_m2m()

    def save_model(self, request: Any, obj: Permit, form: Any, change: Any) -> None:
        obj.calculate_validity_date()
        return super().save_model(request, obj, form, change)


@admin.register(LocalTransportPermit)
class LocalTransportPermitAdmin(PermitBaseAdmin):
    inlines = (TransportEntryInline, SignatureInline)

    def get_fields(self, request, obj):
        fields = super().get_fields(request, obj)
        fields += ['wfp', 'wcp', 'transport_location', 'transport_date']
        return fields


@admin.register(WildlifeFarmPermit)
class WildlifeFarmPermitAdmin(PermitBaseAdmin):
    pass


class PermittedToCollectAnimalInline(admin.TabularInline):
    model = PermittedToCollectAnimal
    autocomplete_fields = ('sub_species',)
    extra = 1


@admin.register(WildlifeCollectorPermit)
class WildlifeCollectorPermitAdmin(PermitBaseAdmin):
    inlines = (PermittedToCollectAnimalInline,)


@admin.register(GratuitousPermit)
class GratuitousPermitAdmin(PermitBaseAdmin):
    pass


@admin.register(CertificateOfWildlifeRegistration)
class CertificateOfWildlifeRegistrationAdmin(PermitBaseAdmin):
    pass


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
                return HttpResponseRedirect(obj.admin_url)
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
                return HttpResponseRedirect(payment_order.admin_url)
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
                return HttpResponseRedirect(obj.inspection.admin_url)
            if obj.submittable and obj.status != Status.DRAFT:
                inspection = Inspection(
                    permit_application=obj,
                    no=obj.no+'-inspection')
                inspection.save()
                self.message_user(
                    request, 'Please continue editing the inspection record.', level=messages.SUCCESS)
                return HttpResponseRedirect(inspection.admin_url)
            else:
                self.message_user(request,
                                  f'Please make sure the permit application is submittable '
                                  f'and no longer on status {Status.DRAFT} (i.e. should be ACCEPTED) '
                                  'before starting the inspection.',
                                  level=messages.ERROR)
                return HttpResponseRedirect('.')

        if 'generate_permit' in request.POST:
            if obj.permit is None:
                if not hasattr(obj, 'paymentorder') or (hasattr(obj, 'paymentorder') and not obj.paymentorder.paid):
                    self.message_user(
                        request,
                        'Please make sure first that there is a payment order and that it has been '
                        'paid already before generating the very permit record.', level=messages.ERROR)
                    return HttpResponseRedirect('.')

                if not hasattr(obj, 'inspection'):
                    self.message_user(
                        request,
                        'Cannot generate the permit because there is no inspection report.', level=messages.ERROR)
                    return HttpResponseRedirect('.')

                if obj.permit_type == PermitType.LTP:
                    ltp = LocalTransportPermit(
                        status=Status.DRAFT,
                        client=obj.client,
                        wfp=obj.client.current_wfp,
                        wcp=obj.client.current_wcp,
                        transport_location=obj.transport_location,
                        transport_date=obj.transport_date,
                        payment_order=obj.paymentorder,
                        inspection=obj.inspection
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

                    return HttpResponseRedirect(ltp.admin_url)

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


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('no', 'scheduled_date')
    search_fields = ('no',)
    autocomplete_fields = ('permit_application', 'inspecting_officer')
    change_form_template = 'permits/admin/inspection_changeform.html'
