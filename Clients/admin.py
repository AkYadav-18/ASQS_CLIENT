from django.contrib import admin
from django.utils.html import format_html
from .models import Client
from .status_history import ClientStatusHistory


class ClientStatusHistoryInline(admin.TabularInline):
    """Inline admin for viewing status history"""
    model = ClientStatusHistory
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_at', 'changed_by', 'reason', 'notes')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Enhanced admin for Client model with status tracking"""

    list_display = [
        'name', 'certification_number', 'country', 'standard',
        'certification_status', 'certification_date', 'expiry_date', 'created_at'
    ]

    list_filter = [
        'certification_status', 'country', 'standard', 'certification_type',
        'created_at', 'certification_date', 'expiry_date'
    ]

    search_fields = ['name', 'certification_number', 'address', 'country']

    readonly_fields = ['created_at', 'created_by']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'address', 'address2', 'address3')
        }),
        ('Certification Details', {
            'fields': (
                'certification_number', 'country', 'standard',
                'certification_date', 'expiry_date', 'recertification_date', 'issue_date'
            )
        }),
        ('Accreditation & Scope', {
            'fields': ('accreditation_body', 'scope')
        }),
        ('Status & Type', {
            'fields': ('certification_status', 'certification_type', 'partner')
        }),
        ('Audit Information', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        })
    )

    inlines = [ClientStatusHistoryInline]

    def save_model(self, request, obj, form, change):
        """Override to track who made the change"""
        obj._changed_by = request.user

        # If status changed, add reason
        if change and 'certification_status' in form.changed_data:
            obj._change_reason = f"Status changed via admin by {request.user.username}"

        super().save_model(request, obj, form, change)


@admin.register(ClientStatusHistory)
class ClientStatusHistoryAdmin(admin.ModelAdmin):
    """Admin for viewing status history"""

    list_display = [
        'client', 'old_status', 'new_status', 'changed_at', 'changed_by'
    ]

    list_filter = ['old_status', 'new_status', 'changed_at']

    search_fields = ['client__name', 'client__certification_number', 'reason']

    readonly_fields = ['client', 'old_status', 'new_status', 'changed_at', 'changed_by']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
