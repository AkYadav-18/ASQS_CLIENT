from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    """Admin interface for managing customer enquiries"""

    list_display = [
        'name', 'email', 'mobile', 'subject_short', 'status',
        'created_at', 'is_responded'
    ]

    list_filter = [
        'status', 'created_at', 'responded_at'
    ]

    search_fields = [
        'name', 'email', 'mobile', 'subject', 'message'
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'mobile')
        }),
        ('Enquiry Details', {
            'fields': ('subject', 'message', 'status')
        }),
        ('Response', {
            'fields': ('response', 'responded_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    actions = ['mark_as_in_progress', 'mark_as_resolved', 'mark_as_closed']

    def subject_short(self, obj):
        """Display shortened subject"""
        if len(obj.subject) > 50:
            return f"{obj.subject[:50]}..."
        return obj.subject
    subject_short.short_description = "Subject"

    def is_responded(self, obj):
        """Show if enquiry has been responded to"""
        if obj.responded_at:
            return format_html(
                '<span style="color: green;">✓ Responded</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Not Responded</span>'
            )
    is_responded.short_description = "Response Status"

    def mark_as_in_progress(self, request, queryset):
        """Mark selected enquiries as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(
            request,
            f'{updated} enquiry(ies) marked as in progress.'
        )
    mark_as_in_progress.short_description = "Mark as In Progress"

    def mark_as_resolved(self, request, queryset):
        """Mark selected enquiries as resolved"""
        updated = queryset.update(status='resolved')
        self.message_user(
            request,
            f'{updated} enquiry(ies) marked as resolved.'
        )
    mark_as_resolved.short_description = "Mark as Resolved"

    def mark_as_closed(self, request, queryset):
        """Mark selected enquiries as closed"""
        updated = queryset.update(status='closed')
        self.message_user(
            request,
            f'{updated} enquiry(ies) marked as closed.'
        )
    mark_as_closed.short_description = "Mark as Closed"

    def save_model(self, request, obj, form, change):
        """Auto-set responded_at when response is added"""
        if obj.response and not obj.responded_at:
            obj.responded_at = timezone.now()
        super().save_model(request, obj, form, change)
