from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
import hashlib
import time

from bibmanage.models import Bibgroup

class AccessLvl(models.Model):
    accesslvl = models.CharField(max_length=50)
    # user, bibliographer, bibmanager

    def __str__(self):
        return f"{self.accesslvl}"

class CustomUser(AbstractUser):
    # add additional fields in here
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    devkey = models.CharField(max_length=50, null=True, blank=True)
    bibgroup = models.ForeignKey(Bibgroup, on_delete=models.CASCADE, blank=True, null=True)
    accesslvl = models.ForeignKey(AccessLvl, on_delete=models.CASCADE, blank=True, null=True)
    manager = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} {self.email}"