from django_yubin.message_views import TemplatedHTMLEmailMessageView


class RegistrationEmailView(TemplatedHTMLEmailMessageView):
    subject_template_name = 'users/emails/registration/subject.txt'
    body_template_name = 'users/emails/registration/body.txt'
    html_body_template_name = 'users/emails/registration/body.html'

    def __init__(self, user, temporary_password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.temporary_password = temporary_password

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        context['temporary_password'] = self.temporary_password
        return context

    def render_to_message(self, *args, **kwargs):
        assert 'to' not in kwargs  # this should only be sent to the user
        kwargs['to'] = (self.user.email, )
        return super().render_to_message(*args, **kwargs)
