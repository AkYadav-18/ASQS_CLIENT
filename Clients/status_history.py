from django.db import models
from django.contrib.auth.models import User
from UniversalBrandCertification import settings
from .models import Client


class ClientStatusHistory(models.Model):
    """
    Model to track certification status changes for clients
    This enables historical analytics and audit trails
    """
    client = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name='status_history'
    )
    
    # Status information
    old_status = models.CharField(
        max_length=20, 
        choices=Client.CERTIFICATION_STATUS_CHOICES,
        null=True, 
        blank=True,
        help_text="Previous certification status"
    )
    
    new_status = models.CharField(
        max_length=20, 
        choices=Client.CERTIFICATION_STATUS_CHOICES,
        help_text="New certification status"
    )
    
    # Change metadata
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Optional reason for change
    reason = models.TextField(
        blank=True, 
        null=True,
        help_text="Reason for status change"
    )
    
    # Additional context
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes about the status change"
    )
    
    class Meta:
        db_table = "client_status_history"
        ordering = ['-changed_at']
        verbose_name = "Client Status History"
        verbose_name_plural = "Client Status Histories"
        
        # Index for performance on analytics queries
        indexes = [
            models.Index(fields=['client', 'changed_at']),
            models.Index(fields=['new_status', 'changed_at']),
            models.Index(fields=['changed_at']),
        ]
    
    def __str__(self):
        if self.old_status:
            return f"{self.client.name}: {self.old_status} → {self.new_status} ({self.changed_at.strftime('%Y-%m-%d')})"
        else:
            return f"{self.client.name}: Initial status {self.new_status} ({self.changed_at.strftime('%Y-%m-%d')})"
    
    @classmethod
    def record_status_change(cls, client, old_status, new_status, user=None, reason=None, notes=None):
        """
        Convenience method to record a status change
        """
        return cls.objects.create(
            client=client,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            reason=reason,
            notes=notes
        )
    
    @classmethod
    def get_status_timeline_data(cls, months=6):
        """
        Get status timeline data for analytics charts
        Returns data for the last N months
        """
        from datetime import date, timedelta
        from django.db.models import Count, Q
        
        today = date.today()
        timeline_data = []
        
        for i in range(months - 1, -1, -1):
            # Calculate month boundaries
            if i == 0:
                month_start = today.replace(day=1)
            else:
                year = today.year
                month = today.month - i
                while month <= 0:
                    month += 12
                    year -= 1
                month_start = today.replace(year=year, month=month, day=1)
            
            # Calculate end of month
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)
            
            # Count active and expired clients at the end of this month
            # We need to find the latest status for each client up to month_end
            active_count = 0
            expired_count = 0
            suspended_count = 0
            revoked_count = 0
            
            # Get all clients that existed by this month
            clients_by_month = Client.objects.filter(created_at__date__lte=month_end)
            
            for client in clients_by_month:
                # Get the latest status change for this client up to month_end
                latest_status = cls.objects.filter(
                    client=client,
                    changed_at__date__lte=month_end
                ).order_by('-changed_at').first()
                
                if latest_status:
                    status = latest_status.new_status
                else:
                    # If no status history, use current status
                    status = client.certification_status
                
                if status == 'active':
                    active_count += 1
                elif status == 'expired':
                    expired_count += 1
                elif status == 'suspended':
                    suspended_count += 1
                elif status == 'revoked':
                    revoked_count += 1
            
            timeline_data.append({
                'month': month_start.strftime('%b %Y'),
                'active': active_count,
                'expired': expired_count,
                'suspended': suspended_count,
                'revoked': revoked_count,
                'total': active_count + expired_count + suspended_count + revoked_count
            })
        
        return timeline_data
