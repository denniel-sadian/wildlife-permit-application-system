from django_yubin.message_views import TemplatedHTMLEmailMessageView

from users.emails import EmailContextMixin


class BaseApplicationEmailView(EmailContextMixin, TemplatedHTMLEmailMessageView):

    def __init__(self, user, application, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.application = application

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = self.application
        return context


class SubmittedApplicationEmailView(BaseApplicationEmailView):
    subject_template_name = 'permits/emails/application_submitted/subject.txt'
    body_template_name = 'permits/emails/application_submitted/body.txt'
    html_body_template_name = 'permits/emails/application_submitted/body.html'


class UnsubmittedApplicationEmailView(BaseApplicationEmailView):
    subject_template_name = 'permits/emails/application_unsubmitted/subject.txt'
    body_template_name = 'permits/emails/application_unsubmitted/body.txt'
    html_body_template_name = 'permits/emails/application_unsubmitted/body.html'


class AcceptedApplicationEmailView(BaseApplicationEmailView):
    subject_template_name = 'permits/emails/application_accepted/subject.txt'
    body_template_name = 'permits/emails/application_accepted/body.txt'
    html_body_template_name = 'permits/emails/application_accepted/body.html'


class ReturnedApplicationEmailView(BaseApplicationEmailView):
    subject_template_name = 'permits/emails/application_returned/subject.txt'
    body_template_name = 'permits/emails/application_returned/body.txt'
    html_body_template_name = 'permits/emails/application_returned/body.html'
