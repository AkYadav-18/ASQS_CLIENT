from django.db import models
from django.contrib.auth.models import User
from UniversalBrandCertification import settings

class Partner(models.Model):
    partner_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    person_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    country = models.CharField(max_length=100)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.partner_name} ({self.company_name})"

    class Meta:
        db_table = "Partner"
