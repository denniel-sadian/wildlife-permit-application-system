from typing import Any
from datetime import datetime

from django.contrib import admin
from django.contrib import messages
from django.db.models.query import QuerySet
from django.db.models import Q
from django.http.request import HttpRequest
from django.http import HttpResponseRedirect
from django.db import transaction

from users.mixins import AdminMixin
from users.models import Admin

from payments.models import (
    PaymentOrder
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
    CollectorOrTrapper,
    Remarks,
    Status,
    Inspection,
    Signature
)
from .signals import (
    application_accepted,
    application_returned,
    inspection_scheduled,
    inspection_signed,
    permit_created,
    permit_signed,
    permit_released
)


class UploadedRequirementInline(admin.StackedInline):
    model = UploadedRequirement
    extra = 1
    autocomplete_fields = ('requirement',)


class TransportEntryInline(admin.TabularInline):
    fields = ('sub_species', 'quantity')
    model = TransportEntry
    extra = 1
    autocomplete_fields = ('sub_species',)
    verbose_name_plural = 'Transport Entries'


class PermitBaseAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ('permit_no', 'status', 'client',
                    'issued_date', 'valid_until', 'created_at')
    fields = ('permit_no', 'client', 'status', 'or_no', 'issued_date',
              'valid_until', 'uploaded_file')
    search_fields = ('permit_no', 'client__first_name', 'client__last_name')
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

    def response_change(self, request, obj):
        if 'release' in request.POST:
            if obj.status not in [Status.RELEASED, Status.USED, Status.EXPIRED]:

                if isinstance(obj.subclass, LocalTransportPermit) and obj.signatures.first() is None:
                    self.message_user(
                        request, 'You cannot release this unsigned permit yet.',
                        level=messages.ERROR)
                    return HttpResponseRedirect('.')

                obj.status = Status.RELEASED
                obj.save()
                self.message_user(
                    request, 'The permit has been released.', level=messages.SUCCESS)

                permit_released.send(sender=request.user, permit=obj)

            else:
                self.message_user(
                    request, 'The permit cannot be released because of the current status.', level=messages.ERROR)
            return HttpResponseRedirect('.')

        response_change = super().response_change(request, obj)

        # Check signature has been attached already
        if 'add_sign' in request.POST and obj.signatures.first() is not None:
            permit_signed.send(sender=request.user, permit=obj)

        return response_change

    def save_model(self, request: Any, obj: Permit, form: Any, change: Any) -> None:
        super().save_model(request, obj, form, change)

        if obj is not None:
            if obj.valid_until is None:
                obj.calculate_validity_date()
                obj.save()


@admin.register(LocalTransportPermit)
class LocalTransportPermitAdmin(PermitBaseAdmin):
    autocomplete_fields = ('client', 'wfp', 'wcp', 'payment_order',
                           'inspection')
    inlines = (TransportEntryInline,)

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fields = ['permit_no', 'status', 'client', 'wfp', 'wcp',
                  'transport_date', 'transport_location',
                  'inspection', 'issued_date', 'valid_until']

        if obj is not None and obj.payment_order is not None:
            fields += ['payment_order']
        else:
            fields += ['or_no', 'or_no_amount']

        fieldsets = [
            ('Permit Data', {
                'fields': fields,
            })
        ]
        return fieldsets


@admin.register(WildlifeFarmPermit)
class WildlifeFarmPermitAdmin(PermitBaseAdmin):
    fields = ('permit_no', 'client', 'status', 'farm_name', 'farm_address',
              'or_no', 'issued_date', 'valid_until', 'uploaded_file')


class PermittedToCollectAnimalInline(admin.TabularInline):
    model = PermittedToCollectAnimal
    autocomplete_fields = ('sub_species',)
    extra = 1


@admin.register(WildlifeCollectorPermit)
class WildlifeCollectorPermitAdmin(PermitBaseAdmin):
    fields = ('permit_no', 'client', 'status', 'farm_name', 'farm_address',
              'or_no', 'issued_date', 'valid_until', 'uploaded_file')
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


class CollectorOrTrapperInline(admin.TabularInline):
    fields = ('name', 'address')
    model = CollectorOrTrapper
    extra = 1


class RemarksInline(admin.TabularInline):
    fields = ('content',)
    model = Remarks
    extra = 0
    verbose_name_plural = 'Remarks'


@admin.register(PermitApplication)
class PermitApplicationAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ('no', 'permit_type', 'client', 'status',
                    'acceptable', 'created_at')
    list_filter = ('permit_type', 'status',)
    search_fields = ('no', 'permit_type', 'client__first_name',
                     'client__last_name', 'status')
    autocomplete_fields = ('client',)
    change_form_template = 'permits/admin/application_changeform.html'

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)

        # Do not include on draft applications
        qs = qs.exclude(status=Status.DRAFT)

        # For admins, exclude those that they didn't accept
        if isinstance(request.user.subclass, Admin):
            qs = qs.exclude(~Q(accepted_by=request.user.subclass)
                            & Q(accepted_by__isnull=False))

        return qs

    def acceptable(self, obj):
        return obj.submittable

    acceptable.boolean = True

    def get_readonly_fields(self, request, obj=None):
        # If obj is None, it means we are adding a new record
        if obj is None:
            return ()
        # Otherwise, when updating an existing record
        return ('client', 'permit_type', 'accepted_by')

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fields = ['no', 'status', 'permit_type', 'client', 'accepted_by']

        if obj and obj.permit_type == PermitType.LTP:
            fields.append('transport_date')
            fields.append('transport_location')
        if obj and obj.permit_type == PermitType.WCP:
            pass

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
            inlines.insert(0, CollectorOrTrapperInline(
                self.model, self.admin_site))

        return inlines

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if (isinstance(instance, Remarks)):
                instance.user = request.user

                # Admin has added some remarks, so we return the application
                form.instance.status = Status.RETURNED
                form.save()

                application_returned.send(
                    request.user, application=form.instance)

            instance.save()
        formset.save_m2m()

    def response_change(self, request, obj: PermitApplication):
        if 'accept' in request.POST:
            if obj.status in [Status.DRAFT, Status.RETURNED, Status.SUBMITTED] \
                    and obj.submittable:
                obj.status = Status.ACCEPTED
                obj.accepted_by = request.user.subclass
                obj.save()
                self.message_user(
                    request, 'The application has been accepted.', level=messages.SUCCESS)

                application_accepted.send(
                    sender=request.user, application=obj)

            else:
                self.message_user(
                    request, 'Cannot be accepted – yet.',
                    level=messages.ERROR)
            return HttpResponseRedirect('.')

        if 'generate_payment_order' in request.POST:
            if hasattr(obj, 'paymentorder'):
                self.message_user(
                    request, 'Order of Payment has been created already.', level=messages.WARNING)
                return HttpResponseRedirect(obj.admin_url)
            if obj.submittable and obj.status == Status.ACCEPTED:
                payment_order = PaymentOrder(
                    nature_of_doc_being_secured='Wildlife',
                    client=obj.client,
                    permit_application=obj,
                    created_by=request.user.subclass
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
            if obj.submittable and obj.status == Status.ACCEPTED \
                    and hasattr(obj, 'paymentorder') and obj.paymentorder.paid:
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
                                  'before starting the inspection. Also, please make sure that '
                                  'the client has paid the payment order already.',
                                  level=messages.ERROR)
                return HttpResponseRedirect('.')

        if 'create_permit' in request.POST:
            if obj.permit is None:
                if not hasattr(obj, 'paymentorder') or (hasattr(obj, 'paymentorder') and not obj.paymentorder.paid):
                    self.message_user(
                        request,
                        'Please make sure first that there is a payment order and that it has been '
                        'paid already before creating the very permit record.', level=messages.ERROR)
                    return HttpResponseRedirect('.')

                if obj.permit_type == PermitType.LTP:
                    if not hasattr(obj, 'inspection') or (hasattr(obj, 'inspection') and obj.inspection.signatures.count() == 0):
                        self.message_user(
                            request,
                            'Cannot generate the permit because the inspection is not done yet.', level=messages.ERROR)
                        return HttpResponseRedirect('.')

                    with transaction.atomic():
                        ltp = LocalTransportPermit(
                            status=Status.DRAFT,
                            client=obj.client,
                            wfp=obj.client.current_wfp,
                            wcp=obj.client.current_wcp,
                            transport_location=obj.transport_location,
                            transport_date=obj.transport_date,
                            payment_order=obj.paymentorder,
                            or_no=obj.paymentorder.no,
                            inspection=obj.inspection,
                            issued_date=datetime.now())
                        ltp.save()
                        formatted_date = datetime.now().strftime("%Y-%m")
                        day_part = datetime.now().day
                        ltp.permit_no = f'MIMAROPA-{obj.permit_type}-{formatted_date}-{day_part}-{ltp.id}'
                        ltp.save()
                        for i in obj.requested_species_to_transport.all():
                            i.ltp = ltp
                            i.save()
                        obj.permit = Permit.objects.select_subclasses().get(id=ltp.id)
                        obj.save()

                        transaction.on_commit(
                            lambda: permit_created.send(
                                sender=request.user, permit=ltp))

                    return HttpResponseRedirect(ltp.admin_url)

                if obj.permit_type == PermitType.WCP:
                    wcp = WildlifeCollectorPermit(
                        status=Status.DRAFT,
                        client=obj.client,
                        or_no=obj.paymentorder.payment.receipt_no,
                        issued_date=datetime.now(),
                        farm_name=obj.farm_name,
                        farm_address=obj.farm_address)
                    wcp.save()
                    formatted_date = datetime.now().strftime("%Y-%m")
                    day_part = datetime.now().day
                    wcp.permit_no = f'MIMAROPA-{obj.permit_type}-{formatted_date}-{day_part}-{wcp.id}'
                    wcp.save()
                    for i in obj.requested_species.all():
                        collection = PermittedToCollectAnimal(
                            wcp=wcp,
                            sub_species=i.sub_species,
                            quantity=i.quantity)
                        collection.save()
                    obj.permit = Permit.objects.select_subclasses().get(id=wcp.id)
                    obj.save()

                    return HttpResponseRedirect(wcp.admin_url)

                if obj.permit_type == PermitType.WFP:
                    wfp = WildlifeFarmPermit(
                        status=Status.DRAFT,
                        client=obj.client,
                        or_no=obj.paymentorder.payment.receipt_no,
                        issued_date=datetime.now(),
                        farm_name=obj.farm_name,
                        farm_address=obj.farm_address)
                    wfp.save()
                    formatted_date = datetime.now().strftime("%Y-%m")
                    day_part = datetime.now().day
                    wfp.permit_no = f'MIMAROPA-{obj.permit_type}-{formatted_date}-{day_part}-{wfp.id}'
                    wfp.save()
                    obj.permit = Permit.objects.select_subclasses().get(id=wfp.id)
                    obj.save()

                    return HttpResponseRedirect(wfp.admin_url)

                if obj.permit_type == PermitType.GP:
                    gp = GratuitousPermit(
                        status=Status.DRAFT,
                        client=obj.client,
                        or_no=obj.paymentorder.payment.receipt_no,
                        issued_date=datetime.now())
                    gp.save()
                    formatted_date = datetime.now().strftime("%Y-%m")
                    day_part = datetime.now().day
                    gp.permit_no = f'MIMAROPA-{obj.permit_type}-{formatted_date}-{day_part}-{gp.id}'
                    gp.save()
                    obj.permit = Permit.objects.select_subclasses().get(id=gp.id)
                    obj.save()

                    return HttpResponseRedirect(gp.admin_url)

                if obj.permit_type == PermitType.CWR:
                    cwr = CertificateOfWildlifeRegistration(
                        status=Status.DRAFT,
                        client=obj.client,
                        or_no=obj.paymentorder.payment.receipt_no,
                        issued_date=datetime.now())
                    cwr.save()
                    formatted_date = datetime.now().strftime("%Y-%m")
                    day_part = datetime.now().day
                    cwr.permit_no = f'MIMAROPA-{obj.permit_type}-{formatted_date}-{day_part}-{cwr.id}'
                    cwr.save()
                    obj.permit = Permit.objects.select_subclasses().get(id=cwr.id)
                    obj.save()

                    return HttpResponseRedirect(cwr.admin_url)

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
class InspectionAdmin(AdminMixin, admin.ModelAdmin):
    fields = ('no', 'scheduled_date', 'inspecting_officer')
    list_display = ('no', 'scheduled_date')
    search_fields = ('no',)
    autocomplete_fields = ('permit_application', 'inspecting_officer')
    change_form_template = 'permits/admin/inspection_changeform.html'

    def response_change(self, request, obj):
        response_change = super().response_change(request, obj)

        # Check signature has been attached already
        if 'add_sign' in request.POST and obj.signatures.first() is not None:
            inspection_signed.send(
                sender=request.user, application=obj.permit_application)

        return response_change

    def save_model(self, request, obj, form, change):
        if change:
            # Check if the object is being updated
            original_obj = Inspection.objects.get(pk=obj.pk)
            changed_fields = set()

            # Compare each field to determine which ones have changed
            for field in Inspection._meta.fields:
                if getattr(obj, field.name) != getattr(original_obj, field.name):
                    changed_fields.add(field.name)

            # Now, 'changed_fields' contains the names of the fields that have been updated
            if {'inspecting_officer', 'scheduled_date'}.issubset(changed_fields) \
                    and obj.inspecting_officer is not None and obj.scheduled_date is not None:
                inspection_scheduled.send(
                    sender=request.user, application=obj.permit_application)

        obj.save()
