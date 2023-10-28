from django_yubin.message_views import TemplatedHTMLEmailMessageView

from users.emails import EmailContextMixin


class SubmittedApplicationEmailView(EmailContextMixin, TemplatedHTMLEmailMessageView):
    subject_template_name = 'permits/emails/application_submitted/subject.txt'
    body_template_name = 'permits/emails/application_submitted/body.txt'
    html_body_template_name = 'permits/emails/application_submitted/body.html'

    def __init__(self, user, application, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.application = application

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        return context

    def render_to_message(self, *args, **kwargs):
        assert 'to' not in kwargs  # this should only be sent to the user
        kwargs['to'] = (self.user.email, )
        return super().render_to_message(*args, **kwargs)
