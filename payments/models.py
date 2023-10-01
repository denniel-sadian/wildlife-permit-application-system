from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

from permits.models import (
    PermitApplication
)


class PaymentOrder(models.Model):
    no = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    nature_of_doc_being_secured = models.CharField(
        'Nature of Application/Permit/Documents being secured', max_length=255)
    client = models.ForeignKey(
        'users.Client', on_delete=models.CASCADE)
    permit_application = models.OneToOneField(
        PermitApplication, on_delete=models.CASCADE)
    prepared_by = models.ForeignKey(
        'users.Admin', on_delete=models.CASCADE, related_name='prepared_order_of_payments')
    approved_by = models.ForeignKey(
        'users.Admin', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def total(self):
        total = self.items.aggregate(
            total=Coalesce(
                Sum('amount', output_field=models.DecimalField()),
                Decimal('0.0')
            )
        )['total']
        return total

    def __str__(self) -> str:
        return str(self.no)


class ORItem(models.Model):
    order_of_payment = models.ForeignKey(
        PaymentOrder, on_delete=models.CASCADE, related_name='items')
    legal_basis = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order of Payment Item"


class PaymentType(models.TextChoices):
    OTC = 'OTC', 'On the counter'
    ONLINE = 'ONLINE', 'Online'


class Payment(models.Model):
    receipt_no = models.CharField(max_length=255)
    payment_order = models.OneToOneField(
        PaymentOrder, on_delete=models.CASCADE)
    uploaded_receipt = models.FileField(
        upload_to='receipts/', null=True, blank=True)
    json_response = models.JSONField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=PaymentType.choices)
