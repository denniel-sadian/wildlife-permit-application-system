from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager

from model_utils.managers import InheritanceManager
from phonenumber_field.modelfields import PhoneNumberField

from permits.models import WildlifeCollectorPermit, WildlifeFarmPermit


class Gender(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'


class ObjectManager(UserManager, InheritanceManager):
    """Manager for User model."""

    def create_superuser(self, username, password, **extra_fields):
        """Create superuser; called by `createsuperuser` management command."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password=password, **extra_fields)

    def get_by_natural_key(self, username):
        """Return `User` with matching natural key."""
        # Use `iexact` filter for case-insensitive matching.
        return self.get(
            **{'{}__iexact'.format(self.model.USERNAME_FIELD): username})


class User(AbstractUser):

    objects = ObjectManager()

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(choices=Gender.choices, max_length=10)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(max_length=14)
    is_initial_password_changed = models.BooleanField(default=False)

    @property
    def subclass(self):
        """Return the User subclass instance."""
        try:
            return self._subclass
        except AttributeError:
            self._subclass = self.__class__.objects.get_subclass(id=self.id)
        return self._subclass

    @property
    def type(self):
        """Return the type of the user."""
        return self.subclass.__class__.__name__

    @property
    def name(self):
        salutation = 'Mr.' if self.gender == Gender.MALE else 'Ms.'
        return salutation + ' ' + str(self)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Client(User):

    class Meta:
        verbose_name = 'Client'

    address = models.CharField(max_length=255)
    business_name = models.CharField(max_length=255)
    agreed_to_terms_and_conditions = models.BooleanField(default=False)

    @property
    def current_wcp(self):
        try:
            wfp = WildlifeCollectorPermit.objects \
                .filter(client=self).latest('created_at')
        except WildlifeCollectorPermit.DoesNotExist:
            wfp = None
        return wfp

    @property
    def current_wfp(self):
        try:
            wfp = WildlifeFarmPermit.objects \
                .filter(client=self).latest('created_at')
        except WildlifeFarmPermit.DoesNotExist:
            wfp = None
        return wfp


class Admin(User):

    class Meta:
        verbose_name = 'Admin'

    def save(self, *args, **kwargs):
        self.is_staff = True
        super().save(*args, **kwargs)


class Permittee(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address = models.TextField()
    farm_name = models.CharField(max_length=255, blank=True, null=True)
    farm_address = models.TextField(blank=True, null=True)
    permittee_photo = models.ImageField(
        upload_to='uploaded-media/', blank=True, null=True)
    farm_photo = models.ImageField(
        upload_to='uploaded-media/', blank=True, null=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name
