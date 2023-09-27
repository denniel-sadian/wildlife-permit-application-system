from django.db import models

from permits.models import (
    PermitApplication
)


class OrderOfPayment(models.Model):
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

    def __str__(self) -> str:
        return str(self.no)


class ORItem(models.Model):
    order_of_payment = models.ForeignKey(
        OrderOfPayment, on_delete=models.CASCADE, related_name='items')
    legal_basis = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Order of Payment Item"
