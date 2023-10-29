import logging

from django.views.generic import RedirectView
from django.views.generic.detail import SingleObjectMixin, DetailView
from django.conf import settings
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt

import paymongo

from biodiversity.context_processors import custom_global_vars

from users.views import CustomLoginRequiredMixin
from users.models import Client

from .models import PaymentOrder
from .signals import online_payment_successful


logger = logging.getLogger(__name__)


class PayViaGcashRedirectView(CustomLoginRequiredMixin, SingleObjectMixin, RedirectView):
    model = PaymentOrder

    def get_queryset(self):
        return super().get_queryset().filter(client=self.request.user.subclass)

    def get_redirect_url(self, *args, **kwargs):
        payment_order: PaymentOrder = self.get_object(
            self.get_queryset())
        if payment_order.extra_data is None:
            payment_order.extra_data = {}

        if payment_order.paid:
            return reverse_lazy(
                'update_application', args=[payment_order.permi_application.id])

        # Create the payment intent
        paymongo.api_key = settings.PAYMONGO['SECRET_KEY']
        payload = {
            'amount': int(str(payment_order.total).replace('.', '')),
            'currency': 'PHP',
            'payment_method_allowed': ['gcash'],
            'statement_descriptor': settings.PAYMONGO['STATEMENT_DESCRIPTOR'],
            'description': f'Payment Order #{payment_order.no} for {payment_order.permit_application.get_permit_type_display()} application.',
            'metadata': {
                'or_no': payment_order.no
            }
        }
        payment_intent = paymongo.PaymentIntent.create(payload)
        payment_order.extra_data['payment_intent_id'] = payment_intent.id
        payment_order.save()

        # Create the payment method
        client: Client = self.request.user.subclass
        payload = {
            'type': 'gcash',
            'billing': {
                'name': client.name,
                'email': client.email,
                'phone': str(client.phone_number)
            }
        }
        payment_method = paymongo.PaymentMethod.create(payload)
        if client.extra_data is None:
            client.extra_data = {}
        client.extra_data['payment_method_id'] = payment_method.id

        # Attach the payment intent to the payment method
        domain = custom_global_vars(self.request)['DOMAIN']
        return_url = domain+reverse_lazy(
            'authorization_complete', args=[payment_order.id])
        payload = {
            'payment_method': payment_method.id,
            'return_url': return_url
        }
        attachment = paymongo.PaymentIntent.attach(payment_intent.id, payload)

        return attachment.next_action['redirect']['url']


class AuthorizationCompleteDetailView(CustomLoginRequiredMixin, DetailView):
    model = PaymentOrder

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(client=self.request.user.subclass)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_intent_id = self.request.GET['payment_intent_id']
        payment_intent = paymongo.PaymentIntent.retrieve(payment_intent_id)
        context['payment_intent'] = payment_intent

        if payment_intent.status == 'succeeded':
            online_payment_successful.send(
                sender=self.__class__,
                payment_order=self.object,
                payment_intent=payment_intent
            )

        return context


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        logger.info('PayMongo webhook data: %s', str(request.POST))
