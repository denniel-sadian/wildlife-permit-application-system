from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.models import ContentType

from users.mixins import ModelMixin, validate_file_extension, validate_amount
from permits.models import (
    PermitApplication,
    Signature
)


class PaymentOrder(ModelMixin, models.Model):
    no = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    nature_of_doc_being_secured = models.CharField(
        'Nature of Application/Permit/Documents being secured', max_length=255)
    client = models.ForeignKey(
        'users.Client', on_delete=models.CASCADE)
    permit_application = models.OneToOneField(
        PermitApplication, on_delete=models.CASCADE, null=True, blank=True)
    prepared_by = models.ForeignKey(
        'users.Admin', on_delete=models.CASCADE, related_name='prepared_payment_orders')
    paid = models.BooleanField(default=False)

    @property
    def total(self):
        total = self.items.aggregate(
            total=Coalesce(
                Sum('amount', output_field=models.DecimalField()),
                Decimal('0.0')
            )
        )['total']
        return total

    @property
    def signature(self):
        try:
            model_type = ContentType.objects.get_for_model(self.__class__)
            return Signature.objects.get(content_type__id=model_type.id, object_id=self.subclass.id)
        except Signature.DoesNotExist:
            return None

    def __str__(self) -> str:
        return str(self.no)


class PaymentOrderItem(models.Model):
    payment_order = models.ForeignKey(
        PaymentOrder, on_delete=models.CASCADE, related_name='items')
    legal_basis = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_amount])

    class Meta:
        verbose_name = "Payment Order Item"


class PaymentType(models.TextChoices):
    OTC = 'OTC', 'On the counter'
    ONLINE = 'ONLINE', 'Online'


class Payment(ModelMixin, models.Model):
    receipt_no = models.CharField(max_length=255)
    payment_order = models.OneToOneField(
        PaymentOrder, on_delete=models.CASCADE)
    uploaded_receipt = models.FileField(
        upload_to='receipts/', null=True, blank=True,
        validators=[validate_file_extension])
    json_response = models.JSONField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[validate_amount])
    payment_type = models.CharField(max_length=50, choices=PaymentType.choices)

    def __str__(self):
        return str(self.receipt_no)
