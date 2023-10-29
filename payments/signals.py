import logging

from django.dispatch import receiver
from django.dispatch import Signal
from django.db import transaction

from .models import (
    PaymentOrder,
    Payment,
    PaymentType
)
from .tasks import (
    notify_signatories_about_prepared_payment_order,
    notify_admins_about_signed_payment_order,
    notify_client_about_released_payment_order,
    notify_client_about_paid_payment_order,
    notify_client_about_failed_payment
)


logger = logging.getLogger(__name__)


payment_order_prepared = Signal()
payment_order_signed = Signal()
payment_order_released = Signal()
payment_order_paid = Signal()
online_payment_successful = Signal()
online_payment_failed = Signal()


@receiver(payment_order_prepared)
def receive_application_submitted(sender, payment_order: PaymentOrder, **kwargs):
    logger.info('Payment order %s has been prepared.', payment_order.no)
    notify_signatories_about_prepared_payment_order.delay(
        payment_order_id=payment_order.id)


@receiver(payment_order_signed)
def receive_payment_order_signed(sender, payment_order: PaymentOrder, **kwargs):
    logger.info('Payment order %s has been signed.', payment_order.no)
    notify_admins_about_signed_payment_order.delay(
        payment_order_id=payment_order.id)


@receiver(payment_order_released)
def receive_payment_order_released(sender, payment_order: PaymentOrder, **kwargs):
    logger.info('Payment order %s has been released.', payment_order.no)
    notify_client_about_released_payment_order.delay(
        payment_order_id=payment_order.id)


@receiver(payment_order_paid)
def receive_payment_order_paid(sender, payment_order: PaymentOrder, **kwargs):
    logger.info('Payment order %s has been paid.', payment_order.no)
    notify_client_about_paid_payment_order.delay(
        payment_order_id=payment_order.id)


@receiver(online_payment_successful)
def receive_online_payment_successful(sender, payment_order: PaymentOrder, payment_intent, **kwargs):
    logger.info('Payment order %s has been paid online.', payment_order.no)
    with transaction.atomic():
        payment = Payment.objects.create(
            receipt_no=payment_order.no,
            payment_order=payment_order,
            json_response=vars(payment_intent),
            amount=payment_order.total,
            payment_type=PaymentType.ONLINE
        )
        payment_order.paid = True
        payment_order.save()

        transaction.on_commit(
            lambda: notify_client_about_paid_payment_order.delay(
                payment_order_id=payment_order.id))


@receiver(online_payment_failed)
def receive_online_payment_failed(sender, payment_order: PaymentOrder, **kwargs):
    logger.info(
        'Payment order %s has been was not paid successfully online.', payment_order.no)
    notify_client_about_failed_payment.delay(payment_order_id=payment_order.id)
