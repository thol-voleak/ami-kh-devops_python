from django.db import models
from jsonfield import JSONField
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
    permissions = JSONField(null=True, blank=True)


from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json

class JSONField(models.TextField):
    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""
        value = json.loads(value)
        assert isinstance(value, dict)
        return value

    def get_db_prep_save(self, value):
        """Convert our JSON object to a string before we save"""
        if value == "":
            return None
        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        return super(JSONField, self).get_db_prep_save(value)