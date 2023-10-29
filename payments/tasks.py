from celery import shared_task

from django.contrib.auth.models import Group

from users.models import (
    User
)

from permits.tasks import get_admins_who_can_receive_emails

from .models import (
    PaymentOrder
)
from .emails import (
    PreparedPaymentOrderEmailView,
    SignedPaymentOrderEmailView,
    ReleasedPaymentOrderEmailView,
    PaidPaymentOrderEmailView
)


def get_paymentorder_signatories_who_can_receive_emails():
    group = Group.objects.get(name='Payment Order Signatory')
    signatories = User.objects.filter(
        groups=group, is_active=True, is_initial_password_changed=True)
    return signatories


@shared_task
def notify_signatories_about_prepared_payment_order(payment_order_id):
    payment_order = PaymentOrder.objects.get(id=payment_order_id)
    signatories = get_paymentorder_signatories_who_can_receive_emails()
    for signatory in signatories:
        PreparedPaymentOrderEmailView(signatory, payment_order).send()


@shared_task
def notify_admins_about_signed_payment_order(payment_order_id):
    payment_order = PaymentOrder.objects.get(id=payment_order_id)
    admins = get_admins_who_can_receive_emails()
    for admin in admins:
        SignedPaymentOrderEmailView(admin, payment_order).send()


@shared_task
def notify_client_about_released_payment_order(payment_order_id):
    payment_order = PaymentOrder.objects.get(id=payment_order_id)
    ReleasedPaymentOrderEmailView(
        payment_order.permit_application.client, payment_order).send()


@shared_task
def notify_client_about_paid_payment_order(payment_order_id):
    payment_order = PaymentOrder.objects.get(id=payment_order_id)
    users = get_admins_who_can_receive_emails()
    users.append(payment_order.permit_application.client)
    for user in users:
        PaidPaymentOrderEmailView(user, payment_order).send()
