from datetime import datetime

from typing import Any

from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.http.request import HttpRequest

from users.mixins import AdminMixin
from users.models import Signatory

from .models import (
    PaymentOrder,
    PaymentOrderItem,
    Payment,
    PaymentType
)
from .signals import (
    payment_order_prepared,
    payment_order_signed,
    payment_order_released,
    payment_order_paid
)


class PaymentOrderItemInline(admin.TabularInline):
    model = PaymentOrderItem
    extra = 1


@admin.register(PaymentOrder)
class PaymentOrderAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ('no', 'permit_application',
                    'paid', 'created_by', 'prepared_by', 'approved_by', 'created_at', 'released_at')
    autocomplete_fields = ('permit_application', 'client', 'created_by')
    search_fields = ('no', 'permit_application__no')
    inlines = (PaymentOrderItemInline,)
    change_form_template = 'payments/admin/paymentorder_changeform.html'

    def paid(self):
        return self.paid

    paid.boolean = True

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)

        if isinstance(request.user.subclass, Signatory):
            qs = qs.filter(Q(prepared_by=request.user.subclass)
                           | Q(approved_by=request.user.subclass))

        return qs

    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        fields = ['no', 'nature_of_doc_being_secured',
                  'client', 'permit_application', 'created_by', 'prepared_by',
                  'paid', 'released_at']

        if obj and obj.prepared_by and obj.prepared_by_signature:
            fields.append('approved_by')

        fieldsets = [
            ('Permit Application Data', {
                'fields': fields,
            })
        ]
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        fields = ['client', 'permit_application', 'created_by', 'released_at']
        # If obj is None, it means we are adding a new record
        if obj is None:
            return ()
        if isinstance(request.user.subclass, Signatory) == False:
            fields.append('approved_by')
        # Otherwise, when updating an existing record
        return fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['prepared_by', 'approved_by']:
            payment_order_signatory_group = (
                Group
                .objects
                .filter(name__iexact='Payment Order Signatory')
                .first())
            if payment_order_signatory_group:
                kwargs['queryset'] = (
                    Signatory
                    .objects
                    .filter(groups__in=[payment_order_signatory_group]))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def response_change(self, request, obj):
        if 'create_payment' in request.POST:
            if not hasattr(obj, 'payment') and obj.total != 0 and obj.released_at:
                payment = Payment(receipt_no=obj.no,
                                  payment_order=obj,
                                  amount=obj.total,
                                  payment_type=PaymentType.OTC,
                                  created_by=request.user.subclass)
                payment.save()
                self.message_user(
                    request, 'Payment record has been made.', level=messages.SUCCESS)
                return HttpResponseRedirect(payment.admin_url)
            else:
                self.message_user(request, 'Incomplete or unreleased payment order.',
                                  level=messages.ERROR)
                return HttpResponseRedirect('.')

        if 'release' in request.POST:
            if obj.total != 0:
                obj.released_at = datetime.now()
                obj.save()
                self.message_user(
                    request, 'Payment record has been released, and the client has been notified already.', level=messages.SUCCESS)

                payment_order_released.send(
                    sender=request.user, payment_order=obj)

            else:
                self.message_user(
                    request,
                    'Cannot release this payment order with 0 amount to pay.',
                    level=messages.ERROR)
            return HttpResponseRedirect('.')

        # Before signing, make sure the payment order has a total
        if 'add_sign' in request.POST:
            if obj.total == 0:
                self.message_user(
                    request, 'Cannot sign an incomplete payment order.',
                    level=messages.ERROR)
                return HttpResponseRedirect('.')

        response_change = super().response_change(request, obj)

        # Check if it's been signed by the prepared_by
        if 'add_sign' in request.POST and obj.prepared_by_signature \
                and obj.prepared_by_signature.person == request.user:
            payment_order_prepared.send(
                sender=request.user, payment_order=obj)

        # Check if it's been signed by the approved_by
        if 'add_sign' in request.POST and obj.approved_by_signature \
                and obj.approved_by_signature.person == request.user:
            payment_order_signed.send(
                sender=request.user, payment_order=obj)

        return response_change

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            obj.created_by = request.user.subclass

        obj.save()
        return super().save_model(request, obj, form, change)


@admin.register(Payment)
class PaymentAdmin(AdminMixin, admin.ModelAdmin):
    exclude = ('json_response',)
    autocomplete_fields = ('payment_order',)
    change_form_template = 'payments/admin/payment_changeform.html'

    def delete_model(self, request: HttpRequest, obj: Any) -> None:
        obj.payment_order.paid = False
        obj.payment_order.save()
        return super().delete_model(request, obj)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            obj.created_by = request.user.subclass

        obj.payment_order.paid = bool(obj.uploaded_receipt)
        obj.payment_order.save()
        if obj.payment_order.paid:
            payment_order_paid.send(
                sender=request.user, payment_order=obj.payment_order)

        obj.save()
        return super().save_model(request, obj, form, change)
