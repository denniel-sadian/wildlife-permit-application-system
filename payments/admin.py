from typing import Any
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .models import (
    OrderOfPayment,
    ORItem
)


class OItemInline(admin.StackedInline):
    model = ORItem
    extra = 1


@admin.register(OrderOfPayment)
class OrderOfPaymentAdmin(admin.ModelAdmin):
    list_display = ('no', 'permit_application', 'prepared_by', 'created_at')
    fields = ('no', 'nature_of_doc_being_secured',
              'client', 'permit_application', 'approved_by')
    autocomplete_fields = ('permit_application', 'client')
    inlines = (OItemInline,)
    change_form_template = 'payments/admin/op_changeform.html'

    def get_readonly_fields(self, request, obj=None):
        # If obj is None, it means we are adding a new record
        if obj is None:
            return ()
        # Otherwise, when updating an existing record
        return ('client', 'client', 'permit_application')

    def response_change(self, request, obj: OrderOfPayment):
        if 'view_application' in request.POST:
            path = f'admin:{obj.permit_application._meta.app_label}_{obj.permit_application._meta.model_name}_change'
            return HttpResponseRedirect(reverse_lazy(path, args=[obj.permit_application.id]))
        return super().response_change(request, obj)

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            obj.prepared_by = request.user.subclass

        obj.save()
        return super().save_model(request, obj, form, change)
