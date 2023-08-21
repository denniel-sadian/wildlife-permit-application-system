from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import Group

from .models import User, Admin


def add_to_correct_group_if_not_yet_added(user: User):
    group = Group.objects.get(name=user.role.label)
    if (group not in user.groups.all()):
        user.groups.add(group)


@receiver(post_save, sender=Admin)
def post_save_admin(sender, instance, created, **kwargs):
    """Admins' post-save signal."""
    if created:
        add_to_correct_group_if_not_yet_added(instance)
