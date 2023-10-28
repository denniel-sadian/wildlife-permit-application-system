from django_yubin.message_views import TemplatedHTMLEmailMessageView

from users.emails import EmailContextMixin


class BasePaymentOrderEmailView(EmailContextMixin, TemplatedHTMLEmailMessageView):

    def __init__(self, user, payment_order, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.payment_order = payment_order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_order'] = self.payment_order
        return context


class PreparedPaymentOrderEmailView(BasePaymentOrderEmailView):
    subject_template_name = 'payments/emails/paymentorder_preped/subject.txt'
    body_template_name = 'payments/emails/paymentorder_preped/body.txt'
    html_body_template_name = 'payments/emails/paymentorder_preped/body.html'


class SignedPaymentOrderEmailView(BasePaymentOrderEmailView):
    subject_template_name = 'payments/emails/paymentorder_signed/subject.txt'
    body_template_name = 'payments/emails/paymentorder_signed/body.txt'
    html_body_template_name = 'payments/emails/paymentorder_signed/body.html'
