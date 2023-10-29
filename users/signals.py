import uuid

from django.dispatch import receiver
from django.dispatch import Signal
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import Group
from django.db import transaction

from .models import User, Client
from .tasks import send_account_created_email


user_created = Signal()


@receiver(user_created)
def handle_user_created(sender, user: User, **kwargs):
    # Set temporary password, and then send the registration email too
    with transaction.atomic():
        temporary_password = str(uuid.uuid4())
        user.set_password(temporary_password)
        user.save()

        # Send the email
        transaction.on_commit(
            lambda: send_account_created_email.delay(
                user.id, temporary_password))

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
        # now what?
        pass
