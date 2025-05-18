from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

# Create your models here.
class Token(models.Model):
    user = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=255)