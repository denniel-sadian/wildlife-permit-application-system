from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect


class AdminMixin:

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            obj = self.model.objects.get(id=object_id)
        except self.model.DoesNotExist:
            obj = None

        extra_context = extra_context or {}
        extra_context['current_user_has_signed'] = False
        if obj:
            for sign in obj.signatures:
                if sign.person == request.user:
                    extra_context['current_user_has_signed'] = True
                    break

        extra_context['user_has_edit_perm'] = request.user.subclass.has_perm(
            f'{self.model._meta.app_label}.change_{self.model._meta.model_name}')

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):
        from permits.models import Signature
        if 'remove_sign' in request.POST:
            Signature.remove(request.user, obj)
            self.message_user(
                request, 'Your signature has been removed.',
                level=messages.SUCCESS)
            return HttpResponseRedirect('.')

        if 'add_sign' in request.POST:
            if Signature.create(request.user, obj):
                self.message_user(
                    request,
                    'Your signature has been attached.',
                    level=messages.SUCCESS)
                return HttpResponseRedirect('.')
            else:
                self.message_user(
                    request,
                    'Sorry, but you cannot sign yet without your position or signature. '
                    'Please complete your profile first.',
                    level=messages.WARNING)
                return HttpResponseRedirect(reverse_lazy('profile'))

        return super().response_change(request, obj)


class ModelMixin:

    @property
    def subclass(self):
        """Return the model subclass instance."""
        try:
            return self._subclass
        except AttributeError:
            self._subclass = self.__class__.objects.get_subclass(id=self.id)
        return self._subclass

    @property
    def type(self):
        """Return the type."""
        return self.subclass.__class__.__name__

    @property
    def admin_url(self):
        path = f'admin:{self._meta.app_label}_{self._meta.model_name}_change'
        return reverse_lazy(path, args=[self.id])

    @property
    def signatures(self):
        from permits.models import Signature
        model_type = ContentType.objects.get_for_model(self.__class__)
        return Signature.objects.filter(content_type__id=model_type.id, object_id=self.id)


def validate_file_extension(value):
    accepted_types = ['pdf', 'jpg', 'jpeg', 'png']
    for i in accepted_types:
        if value.name.lower().endswith('.'+i):
            return
    raise ValidationError(
        'File types that are only allowed: ' + (', ').join(accepted_types))


def validate_amount(value):
    if value < 0:
        raise ValidationError(f'Really, {str(value)}?')
