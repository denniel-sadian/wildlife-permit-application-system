from datetime import datetime

from typing import Any

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http.request import HttpRequest

from users.mixins import AdminMixin


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
class PaymentOrderAdmin(AdminMixin, admin.ModelAdmin):
    list_display = ('no', 'permit_application',
                    'paid', 'prepared_by', 'created_at', 'released_at')
    fields = ('no', 'nature_of_doc_being_secured',
              'client', 'permit_application', 'prepared_by',
              'paid', 'released_at')
    autocomplete_fields = ('permit_application', 'client', 'prepared_by')
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
        return ('client', 'permit_application', 'prepared_by', 'released_at')

    def response_change(self, request, obj):
        if 'create_payment' in request.POST:
            if not hasattr(obj, 'payment'):
                payment = Payment(receipt_no=obj.no,
                                  payment_order=obj,
                                  amount=obj.total,
                                  payment_type=PaymentType.OTC,
                                  created_by=request.user)
                payment.save()
                self.message_user(
                    request, 'Payment record has been made.', level=messages.SUCCESS)
                return HttpResponseRedirect(payment.admin_url)

        if 'release' in request.POST:
            if obj.total != 0:
                obj.released_at = datetime.now()
                obj.save()
                self.message_user(
                    request, 'Payment record has been released, and the client has been notified already.', level=messages.SUCCESS)
            else:
                self.message_user(
                    request,
                    'Cannot release this payment order with 0 amount to pay.',
                    level=messages.ERROR)
            return HttpResponseRedirect('.')

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

    def delete_model(self, request: HttpRequest, obj: Any) -> None:
        obj.payment_order.paid = False
        obj.payment_order.save()
        return super().delete_model(request, obj)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            obj.created_by = request.user.subclass

        obj.payment_order.paid = bool(obj.uploaded_receipt)
        obj.payment_order.save()

        obj.save()
        return super().save_model(request, obj, form, change)
