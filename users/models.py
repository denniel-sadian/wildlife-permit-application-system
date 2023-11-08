from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager

from model_utils.managers import InheritanceManager
from phonenumber_field.modelfields import PhoneNumberField
from django_resized import ResizedImageField

from permits.models import (
    Status,
    WildlifeCollectorPermit,
    WildlifeFarmPermit
)

from .mixins import ModelMixin, validate_file_size, validate_file_extension


class Gender(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'


class ObjectManager(UserManager, InheritanceManager):
    """Manager for User model."""

    def create_superuser(self, username, email, password, **extra_fields):
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


class User(ModelMixin, AbstractUser):

    objects = ObjectManager()

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField('Position', max_length=100, null=True)
    gender = models.CharField(choices=Gender.choices, max_length=10)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(max_length=14)
    is_initial_password_changed = models.BooleanField(default=False)
    signature_image = ResizedImageField(
        upload_to='signs/', null=True, blank=True,
        validators=[validate_file_size, validate_file_extension])
    extra_data = models.JSONField(default=dict)

    @property
    def name(self):
        salutation = 'Mr.' if self.gender == Gender.MALE else 'Ms.'
        return salutation + ' ' + str(self)

    @property
    def pronoun(self):
        pronoun = 'he' if self.gender == Gender.MALE else 'she'
        return pronoun

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Client(User):

    class Meta:
        verbose_name = 'Client'

    address = models.CharField(max_length=255)
    agreed_to_terms_and_conditions = models.BooleanField(default=False)

    @property
    def current_wcp(self):
        try:
            wcp = WildlifeCollectorPermit.objects \
                .filter(client=self, status=Status.RELEASED) \
                .latest('-created_at')
        except WildlifeCollectorPermit.DoesNotExist:
            wcp = None
        return wcp

    @property
    def current_wfp(self):
        try:
            wfp = WildlifeFarmPermit.objects \
                .filter(client=self, status=Status.RELEASED) \
                .latest('-created_at')
        except WildlifeFarmPermit.DoesNotExist:
            wfp = None
        return wfp

    @property
    def current_farm_name(self):
        return WildlifeFarmPermit.objects \
            .filter(client=self) \
            .latest('-created_at').farm_name


class Admin(User):

    class Meta:
        verbose_name = 'Admin'

    def save(self, *args, **kwargs):
        self.is_staff = True
        super().save(*args, **kwargs)


class Signatory(User):

    class Meta:
        verbose_name = 'Signatory'
        verbose_name_plural = 'Signatories'

    def save(self, *args, **kwargs):
        self.is_staff = True
        super().save(*args, **kwargs)


class Cashier(User):

    class Meta:
        verbose_name = 'Cashier'

    def save(self, *args, **kwargs):
        self.is_staff = True
        super().save(*args, **kwargs)


class Validator(User):

    class Meta:
        verbose_name = 'Validator'

    def save(self, *args, **kwargs):
        self.is_staff = True
        super().save(*args, **kwargs)
