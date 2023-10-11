from typing import Any
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http.request import HttpRequest

from permits.models import Signature
from permits.admin import SignatureInline

from .models import (
    PaymentOrder,
    PaymentOrderItem,
    Payment,
    PaymentType
)


class PaymentOrderItemInline(admin.TabularInline):
    model = PaymentOrderItem
    extra = 1


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ('no', 'permit_application',
                    'paid', 'prepared_by', 'created_at')
    fields = ('no', 'nature_of_doc_being_secured',
              'client', 'permit_application', 'prepared_by', 'paid')
    autocomplete_fields = ('permit_application', 'client', 'prepared_by')
    search_fields = ('no', 'permit_application__no')
    inlines = (PaymentOrderItemInline, SignatureInline)
    change_form_template = 'payments/admin/paymentorder_changeform.html'

    def paid(self):
        return self.paid

    paid.boolean = True

    def get_readonly_fields(self, request, obj=None):
        # If obj is None, it means we are adding a new record
        if obj is None:
            return ()
        # Otherwise, when updating an existing record
        return ('client', 'client', 'permit_application', 'prepared_by')

    def response_change(self, request, obj: PaymentOrder):
        if obj:
            if not obj.prepared_by_signature:
                self.message_user(
                    request, 'The one who prepared the payment order needs to sign.', level=messages.WARNING)
            if not obj.approved_by_signature:
                self.message_user(
                    request, 'A payment signatory needs to sign this payment order.', level=messages.WARNING)

        if 'create_payment' in request.POST:
            if not hasattr(obj, 'payment'):
                payment = Payment(receipt_no=obj.no,
                                  payment_order=obj,
                                  amount=obj.total,
                                  payment_type=PaymentType.OTC)
                payment.save()
                self.message_user(
                    request, 'Payment record has been made.', level=messages.SUCCESS)
                return HttpResponseRedirect(payment.admin_url)

        return super().response_change(request, obj)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            obj.prepared_by = request.user.subclass

        obj.save()
        return super().save_model(request, obj, form, change)

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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    exclude = ('json_response',)
    autocomplete_fields = ('payment_order',)
    change_form_template = 'payments/admin/payment_changeform.html'
