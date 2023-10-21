from datetime import datetime

from typing import Any

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse_lazy

from permits.models import Signature

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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            payment_order = PaymentOrder.objects.get(id=object_id)
        except PaymentOrder.DoesNotExist:
            payment_order = None

        extra_context = extra_context or {}
        extra_context['current_user_has_signed'] = False
        for sign in payment_order.signatures:
            if sign.person == request.user:
                extra_context['current_user_has_signed'] = True
                break

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):
        if 'remove_sign' in request.POST:
            Signature.remove(request.user, obj)
            self.message_user(
                request, 'Your signature has been removed.',
                level=messages.SUCCESS)
            return HttpResponseRedirect('.')

        if 'add_sign' in request.POST:
            if Signature.create(request.user, obj):
                self.message_user(
                    request,
                    'Your signature has been attached.',
                    level=messages.SUCCESS)
                return HttpResponseRedirect('.')
            else:
                self.message_user(
                    request,
                    'Sorry, but you cannot sign yet without your position or signature. '
                    'Please complete your profile first.',
                    level=messages.WARNING)
                return HttpResponseRedirect(reverse_lazy('profile'))

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

        if 'release' in request.POST:
            obj.released_at = datetime.now()
            obj.save()

            self.message_user(
                request, 'Payment record has been released, and the client has been notified already.', level=messages.SUCCESS)
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
