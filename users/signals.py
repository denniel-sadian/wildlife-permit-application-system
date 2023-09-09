from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import Group

from .models import User, Admin, Client, Permittee


def add_to_correct_group_if_not_yet_added(user: User):
    '''Add the user to thier correct group.'''
    group = Group.objects.get(name=user.role.label)
    if (group not in user.groups.all()):
        user.groups.add(group)


@receiver(post_save, sender=Admin)
def post_save_admin(sender, instance: Admin, created, **kwargs):
    """Admins' post-save signal."""
    if created:
        add_to_correct_group_if_not_yet_added(instance)


@receiver(user_logged_in)
def client_first_login(sender, user, request, **kwargs):
    """Clients' login signal."""
    if user.type is Client.__name__ and not user.is_initial_password_changed:
        # TODO: Get all attached concerns in the temporary permittee record and attach them to the new client
        found_temp_permittee = Permittee.objects.filter(
            first_name__icontains=user.first_name, last_name__icontains=user.last_name)

        # Make sure the temporary permitee is now deleted because the client registered already
        if found_temp_permittee is not None:
            found_temp_permittee.delete()
