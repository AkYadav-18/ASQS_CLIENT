from django.db import models
from django.contrib.auth.models import User
from UniversalBrandCertification import settings

class Standards(models.Model):
    Standard_name = models.CharField(max_length=255)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.Standard_name}"

    class Meta:
        db_table = "Standards"
