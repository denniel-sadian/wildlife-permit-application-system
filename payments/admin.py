from typing import Any
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import HttpRequest
from django.contrib import messages
from django.urls import reverse_lazy

from .models import (
    PaymentOrder,
    ORItem,
    Payment,
    PaymentType
)


class OItemInline(admin.StackedInline):
    model = ORItem
    extra = 1


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ('no', 'permit_application', 'prepared_by', 'created_at')
    fields = ('no', 'nature_of_doc_being_secured',
              'client', 'permit_application', 'approved_by', 'prepared_by')
    autocomplete_fields = ('permit_application', 'client', 'approved_by')
    inlines = (OItemInline,)
    change_form_template = 'payments/admin/paymentorder_changeform.html'

    def get_readonly_fields(self, request, obj=None):
        # If obj is None, it means we are adding a new record
        if obj is None:
            return ()
        # Otherwise, when updating an existing record
        return ('client', 'client', 'permit_application', 'prepared_by')

    def response_change(self, request, obj: PaymentOrder):
        if 'create_payment' in request.POST:
            if obj.payment_order is None:
                payment = Payment(receipt_no=obj.no,
                                  payment_order=obj,
                                  amount=obj.total,
                                  payment_type=PaymentType.OTC)
                payment.save()
                self.message_user(
                    request, 'Payment record has been made.', level=messages.SUCCESS)
                path = f'admin:{payment._meta.app_label}_{payment._meta.model_name}_change'
                return HttpResponseRedirect(reverse_lazy(path, args=[payment.id]))

        return super().response_change(request, obj)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            obj.prepared_by = request.user.subclass

        obj.save()
        return super().save_model(request, obj, form, change)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    exclude = ('json_response',)
    change_form_template = 'payments/admin/payment_changeform.html'
