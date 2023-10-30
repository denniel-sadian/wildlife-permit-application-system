import logging

from django.dispatch import receiver
from django.dispatch import Signal
from django.db import transaction
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _

from users.models import User

from permits.models import PermitApplication

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
    notify_client_about_failed_payment,
    notify_client_about_refunded_payment
)


logger = logging.getLogger(__name__)


payment_order_prepared = Signal()
payment_order_signed = Signal()
payment_order_released = Signal()
payment_order_paid = Signal()
online_payment_successful = Signal()
online_payment_failed = Signal()
online_payment_refunded = Signal()


@receiver(payment_order_prepared)
def receive_payment_order_prepared(sender, payment_order: PaymentOrder, **kwargs):
    message = f'Payment order {payment_order.no} has been prepared.'
    logger.info(message)
    notify_signatories_about_prepared_payment_order.delay(
        payment_order_id=payment_order.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=payment_order.permit_application.id,
            object_repr=_(str(payment_order.permit_application)),
            action_flag=CHANGE,
            change_message=_(message)
        )


@receiver(payment_order_signed)
def receive_payment_order_signed(sender, payment_order: PaymentOrder, **kwargs):
    message = f'Payment order {payment_order.no} has been signed.'
    logger.info(message)
    notify_admins_about_signed_payment_order.delay(
        payment_order_id=payment_order.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=payment_order.permit_application.id,
            object_repr=_(str(payment_order.permit_application)),
            action_flag=CHANGE,
            change_message=_(message)
        )


@receiver(payment_order_released)
def receive_payment_order_released(sender, payment_order: PaymentOrder, **kwargs):
    message = f'Payment order {payment_order.no} has been released.'
    logger.info(message)
    notify_client_about_released_payment_order.delay(
        payment_order_id=payment_order.id)
    if isinstance(sender, User):
        content_type = ContentType.objects.get_for_model(PermitApplication)
        LogEntry.objects.log_action(
            user_id=sender.id,
            content_type_id=content_type.id,
            object_id=payment_order.permit_application.id,
            object_repr=_(str(payment_order.permit_application)),
            action_flag=CHANGE,
            change_message=_(message)
        )


@receiver(payment_order_paid)
def receive_payment_order_paid(sender, payment_order: PaymentOrder, **kwargs):
    message = f'Payment order {payment_order.no} has been paid.'
    logger.info(message)
    notify_client_about_paid_payment_order.delay(
        payment_order_id=payment_order.id)

    content_type = ContentType.objects.get_for_model(PermitApplication)
    LogEntry.objects.log_action(
        user_id=payment_order.client.id,
        content_type_id=content_type.id,
        object_id=payment_order.permit_application.id,
        object_repr=_(str(payment_order.permit_application)),
        action_flag=CHANGE,
        change_message=_(message)
    )


@receiver(online_payment_successful)
def receive_online_payment_successful(sender, payment_order: PaymentOrder, payment_intent, **kwargs):
    message = f'Payment order {payment_order.no} has been paid online.'
    logger.info(message)
    with transaction.atomic():
        Payment.objects.create(
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

    content_type = ContentType.objects.get_for_model(PermitApplication)
    LogEntry.objects.log_action(
        user_id=payment_order.client.id,
        content_type_id=content_type.id,
        object_id=payment_order.permit_application.id,
        object_repr=_(str(payment_order.permit_application)),
        action_flag=CHANGE,
        change_message=_(message)
    )


@receiver(online_payment_failed)
def receive_online_payment_failed(sender, payment_order: PaymentOrder, **kwargs):
    message = f'Payment order {payment_order.no} was not paid successfully online.'
    logger.info(message)
    notify_client_about_failed_payment.delay(payment_order_id=payment_order.id)

    content_type = ContentType.objects.get_for_model(PermitApplication)
    LogEntry.objects.log_action(
        user_id=payment_order.client.id,
        content_type_id=content_type.id,
        object_id=payment_order.permit_application.id,
        object_repr=_(str(payment_order.permit_application)),
        action_flag=CHANGE,
        change_message=_(message)
    )


@receiver(online_payment_refunded)
def receive_online_payment_refunded(sender, payment_order: PaymentOrder, **kwargs):
    message = f'Payment order {payment_order.no} has been refunded.'
    logger.info(message)
    with transaction.atomic():
        payment_order.paid = False
        payment_order.save()
        if hasattr(payment_order, 'payment'):
            payment_order.payment.delete()

        transaction.on_commit(
            lambda: notify_client_about_refunded_payment.delay(
                payment_order_id=payment_order.id))

    content_type = ContentType.objects.get_for_model(PermitApplication)
    LogEntry.objects.log_action(
        user_id=payment_order.client.id,
        content_type_id=content_type.id,
        object_id=payment_order.permit_application.id,
        object_repr=_(str(payment_order.permit_application)),
        action_flag=CHANGE,
        change_message=_(message)
    )
