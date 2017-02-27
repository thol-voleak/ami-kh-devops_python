from django.db import models
from django.contrib.auth.models import User


class Authentications(models.Model):
    user = models.ForeignKey(User)
    access_token = models.CharField(max_length=256)
    last_updated = models.DateTimeField(null=True, blank=True)
