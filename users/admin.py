from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Client, Admin


@admin.register(Admin)
class AdminAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'last_login')
    fieldsets = (
        ('Authentication', {'fields': ('username', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Important dates', {'fields': ('date_joined',)}),
        (
            'Permissions',
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "groups"
                ),
            },
        ),
    )

@admin.register(Client)
class ClientAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'last_login')
    fieldsets = (
        ('Authentication', {'fields': ('username', 'password', 'is_active')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'business_name', 'email', 'phone_number')}),
        ('Important dates', {'fields': ('date_joined',)})
    )
