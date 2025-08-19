from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified')
    list_filter = ('is_staff', 'is_active', 'is_verified', 'is_superuser', 'groups')

    fieldsets = (
        (None, {
            'fields': (
                'username', 
                'email', 
                'first_name',      # Add first_name
                'last_name',       # Add last_name
                'password', 
                'phone', 
                'is_verified'
            )
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'first_name',     # Add first_name in creation form
                'last_name',      # Add last_name in creation form
                'password1',
                'password2',
                'is_staff',
                'is_active',
                'is_verified'
            ),
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
