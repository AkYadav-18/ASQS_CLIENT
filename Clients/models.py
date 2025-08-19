from django.db import models
from django.contrib.auth.models import User

from Partners.models import Partner
from UniversalBrandCertification import settings

class Client(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True, help_text="Client's email address")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Client's phone number")
    address = models.TextField()
    address2 = models.TextField(blank=True, null=True)
    address3 = models.TextField(blank=True, null=True)

    # Certification Details
    certification_number = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    standard = models.CharField(max_length=255, blank=True, null=True)
    certification_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    recertification_date = models.DateField(blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)

    # Accreditation & Scope
    accreditation_body = models.CharField(max_length=255, blank=True, null=True)
    scope = models.TextField(blank=True, null=True)

    # Dropdowns / Choices
    CERTIFICATION_STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked'),
    ]
    certification_status = models.CharField(
        max_length=20, choices=CERTIFICATION_STATUS_CHOICES, default='active'
    )

    partner = models.ForeignKey(Partner,on_delete=models.SET_NULL, null=True, blank=True)

    CERTIFICATION_TYPE_CHOICES = [
        ('initial', 'Initial'),
        ('renewal', 'Renewal'),
        ('surveillance', 'Surveillance'),
    ]
    
    certification_type = models.CharField(
        max_length=20, choices=CERTIFICATION_TYPE_CHOICES, blank=True, null=True
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.certification_number}"

    def save(self, *args, **kwargs):
        """Override save to track status changes"""
        # Check if this is an update (not a new record)
        if self.pk:
            try:
                old_instance = Client.objects.get(pk=self.pk)
                old_status = old_instance.certification_status
                new_status = self.certification_status

                # If status changed, record it
                if old_status != new_status:
                    super().save(*args, **kwargs)  # Save first

                    # Import here to avoid circular imports
                    from .status_history import ClientStatusHistory
                    ClientStatusHistory.record_status_change(
                        client=self,
                        old_status=old_status,
                        new_status=new_status,
                        user=getattr(self, '_changed_by', None),
                        reason=getattr(self, '_change_reason', None)
                    )
                    return
            except Client.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # For new records, create initial status history
        if not hasattr(self, '_status_history_created'):
            from .status_history import ClientStatusHistory
            ClientStatusHistory.record_status_change(
                client=self,
                old_status=None,
                new_status=self.certification_status,
                user=getattr(self, '_changed_by', None),
                reason="Initial status"
            )
            self._status_history_created = True

    class Meta:
        db_table = "Client"

