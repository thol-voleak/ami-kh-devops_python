from django.db import models
from django.contrib.auth.models import User


class Authentications(models.Model):
    user = models.OneToOneField(User, unique=True)
    system_user_id = models.CharField(max_length=128)
    username = models.CharField(max_length=256)
    firstname = models.CharField(max_length=256, null=True)
    lastname = models.CharField(max_length=256, null=True)
    mobile_number = models.CharField(max_length=128, null=True)
    email = models.CharField(max_length=256, null=True)
    access_token = models.CharField(max_length=256)
    correlation_id = models.CharField(max_length=128, null=True, blank=True)
    last_updated_timestamp = models.DateTimeField(null=True, blank=True)
    created_timestamp = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
