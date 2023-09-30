from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Client,
    Admin,
    Cashier,
    Permittee
)


class BaseUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_active', 'is_initial_password_changed',
                    'date_joined', 'last_login')
    fieldsets = (
        ('Authentication', {'fields': ('username', 'password')}),
        ('Personal Information', {
         'fields': ('first_name', 'last_name', 'gender', 'email', 'phone_number')}),
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


@admin.register(Admin)
class AdminAdmin(BaseUserAdmin):
    pass


@admin.register(Cashier)
class CashierAdmin(BaseUserAdmin):
    pass


@admin.register(Client)
class ClientAdmin(BaseUserAdmin):
    pass


@admin.register(Permittee)
class PermitteeAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',
                    'address', 'farm_name', 'farm_address')
    search_fields = list_display
    ordering = list_display
