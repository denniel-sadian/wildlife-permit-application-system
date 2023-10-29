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


class BasePermitEmailView(EmailContextMixin, TemplatedHTMLEmailMessageView):

    def __init__(self, user, permit, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.permit = permit

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['permit'] = self.permit
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


class ScheduledInspectionEmailView(BaseApplicationEmailView):
    subject_template_name = 'permits/emails/inspection_scheduled/subject.txt'
    body_template_name = 'permits/emails/inspection_scheduled/body.txt'
    html_body_template_name = 'permits/emails/inspection_scheduled/body.html'


class AssignedScheduledInspectionEmailView(BaseApplicationEmailView):
    subject_template_name = 'permits/emails/inspection_assigned/subject.txt'
    body_template_name = 'permits/emails/inspection_assigned/body.txt'
    html_body_template_name = 'permits/emails/inspection_assigned/body.html'


class SignedInspectionEmailView(BaseApplicationEmailView):
    subject_template_name = 'permits/emails/inspection_signed/subject.txt'
    body_template_name = 'permits/emails/inspection_signed/body.txt'
    html_body_template_name = 'permits/emails/inspection_signed/body.html'


class PermitCreatedEmailView(BasePermitEmailView):
    subject_template_name = 'permits/emails/permit_created/subject.txt'
    body_template_name = 'permits/emails/permit_created/body.txt'
    html_body_template_name = 'permits/emails/permit_created/body.html'


class PermitReleasedEmailView(BasePermitEmailView):
    subject_template_name = 'permits/emails/permit_released/subject.txt'
    body_template_name = 'permits/emails/permit_released/body.txt'
    html_body_template_name = 'permits/emails/permit_released/body.html'


class PermitValidatedEmailView(BasePermitEmailView):
    subject_template_name = 'permits/emails/permit_validated/subject.txt'
    body_template_name = 'permits/emails/permit_validated/body.txt'
    html_body_template_name = 'permits/emails/permit_validated/body.html'


class PermitExpiredEmailView(BasePermitEmailView):
    subject_template_name = 'permits/emails/permit_expired/subject.txt'
    body_template_name = 'permits/emails/permit_expired/body.txt'
    html_body_template_name = 'permits/emails/permit_expired/body.html'
