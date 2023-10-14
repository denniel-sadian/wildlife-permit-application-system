from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from .models import (
    User,
    Client,
    Admin,
    Cashier,
    Signatory
)

from .signals import user_created


class CustomUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False


class BaseUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'title', 'gender'),
        }),
    )
    add_form = CustomUserCreationForm

    list_display = ('username', 'email', 'first_name', 'title',
                    'last_name', 'is_active',
                    'date_joined', 'last_login')
    fieldsets = (
        ('Authentication', {'fields': ('username',)}),
        ('User Information', {
         'fields': ('first_name', 'last_name', 'gender', 'email', 'phone_number', 'title')}),
        ('Important dates', {'fields': ('date_joined',)}),
        (
            'Permissions',
            {
                "fields": (
                    "is_active",
                    'groups',
                    'user_permissions'
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change) -> None:
        super().save_model(request, obj, form, change)
        if not change:
            user = User.objects.get(id=obj.id)
            user_created.send_robust(sender=self.__class__, user=user)


@admin.register(Admin)
class AdminAdmin(BaseUserAdmin):
    pass


@admin.register(Cashier)
class CashierAdmin(BaseUserAdmin):
    pass


@admin.register(Signatory)
class SignatoryAdmin(BaseUserAdmin):
    pass


@admin.register(Client)
class ClientAdmin(BaseUserAdmin):
    pass
