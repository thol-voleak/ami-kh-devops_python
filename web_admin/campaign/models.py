from django.db import models

class terms_mapping(models.Model):
    term = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    updated_by = models.CharField(max_length=128)
    created_at = models.DateTimeField(null=False)
    updated_at = models.DateTimeField(null=False)
