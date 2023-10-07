import uuid

from django.dispatch import receiver
from django.dispatch import Signal
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import Group

from .models import User, Client, Permittee
from .emails import RegistrationEmailView


user_created = Signal()


@receiver(user_created)
def handle_user_created(sender, user: User, **kwargs):
    # Set temporary password, and then send the registration email too
    temporary_password = str(uuid.uuid4())
    user.set_password(temporary_password)
    user.save()
    RegistrationEmailView(user, temporary_password).send()

    # Assign the user to the right group
    try:
        group = Group.objects.get(name=user.type)
        if group not in user.groups.all():
            user.groups.add(group)
    except Group.DoesNotExist:
        pass


@receiver(user_logged_in)
def client_first_login(sender, user: User, request, **kwargs):
    """Clients' login signal."""
    if user.type is Client.__name__ and not user.is_initial_password_changed:
        found_temp_permittee = Permittee.objects.filter(
            first_name__icontains=user.first_name, last_name__icontains=user.last_name).first()
        if found_temp_permittee:

            # Assign the present permits
            for permit in found_temp_permittee.temporarily_assigned_permits.all():
                permit.client = user.subclass
                permit.permittee = None
                permit.save()

            found_temp_permittee.delete()
