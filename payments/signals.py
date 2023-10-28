import logging

from django.dispatch import receiver
from django.dispatch import Signal

from .models import (
    PaymentOrder
)
from .tasks import (
    notify_signatories_about_prepared_payment_order
)


logger = logging.getLogger(__name__)


payment_order_prepared = Signal()


@receiver(payment_order_prepared)
def receive_application_submitted(sender, payment_order: PaymentOrder, **kwargs):
    logger.info('Payment order %s has been prepared.', payment_order.no)
    notify_signatories_about_prepared_payment_order.delay(
        payment_order_id=payment_order.id)
