from typing import Any
from django.contrib import admin

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

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        if not change:
            obj.prepared_by = request.user.subclass

        obj.save()
        return super().save_model(request, obj, form, change)
