from django.db import models
from django.utils import timezone


class Enquiry(models.Model):
    """Model to store customer enquiries from the contact form"""

    ENQUIRY_STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    # Contact Information
    name = models.CharField(max_length=255, help_text="Customer's full name")
    email = models.EmailField(help_text="Customer's email address")
    mobile = models.CharField(max_length=20, help_text="Customer's mobile number")

    # Enquiry Details
    subject = models.CharField(max_length=500, help_text="Subject of the enquiry")
    message = models.TextField(help_text="Detailed message from customer")

    # Status and Tracking
    status = models.CharField(
        max_length=20,
        choices=ENQUIRY_STATUS_CHOICES,
        default='new',
        help_text="Current status of the enquiry"
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional fields for follow-up
    response = models.TextField(
        blank=True,
        null=True,
        help_text="Response from admin/staff"
    )
    responded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the response was sent"
    )

    class Meta:
        db_table = "enquiry"
        ordering = ['-created_at']
        verbose_name = "Customer Enquiry"
        verbose_name_plural = "Customer Enquiries"

    def __str__(self):
        return f"{self.name} - {self.subject[:50]}{'...' if len(self.subject) > 50 else ''}"

    @property
    def is_new(self):
        return self.status == 'new'

    @property
    def is_resolved(self):
        return self.status in ['resolved', 'closed']
