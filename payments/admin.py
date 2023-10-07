from typing import Any
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy

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
              'client', 'permit_application', 'prepared_by', 'approved_by', 'paid')
    autocomplete_fields = ('permit_application', 'client',
                           'approved_by', 'prepared_by')
    search_fields = ('no', 'permit_application__no')
    inlines = (PaymentOrderItemInline,)
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


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    exclude = ('json_response',)
    autocomplete_fields = ('payment_order',)
    change_form_template = 'payments/admin/payment_changeform.html'
