from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager

from model_utils.managers import InheritanceManager
from phonenumber_field.modelfields import PhoneNumberField


class Manager(UserManager, InheritanceManager):
    """Manager for User model."""

    def create_superuser(self, username, password, **extra_fields):
        """Create superuser; called by `createsuperuser` management command."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            username, email=None, password=password, **extra_fields)

    def get_by_natural_key(self, username):
        """Return `User` with matching natural key."""
        # Use `iexact` filter for case-insensitive matching.
        return self.get(
            **{'{}__iexact'.format(self.model.USERNAME_FIELD): username})


class User(AbstractUser):

    class Role(models.TextChoices):
        CLIENT = 'CLIENT', 'Client'
        ADMIN = 'ADMIN', 'Admin'

    objects = Manager()

    role = models.CharField(choices=Role.choices, max_length=50)
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)

    @property
    def subclass(self):
        """Return the User subclass instance."""
        if self._subclass is None:
            self._subclass = self.__class__.objects.get_subclass(id=self.id)
        return self._subclass

    @property
    def type(self):
        """Return the type of the user."""
        return self.subclass.__class__.__name__


class Client(User):
    address = models.CharField(max_length=255)
    contact_number = PhoneNumberField(max_length=14)


class Admin(User):
    new_field = models.CharField(max_length=255)
