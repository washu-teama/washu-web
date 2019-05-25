from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from device.models import Coordinator

# Create your models here.


class Location(models.Model):
    LIVE_TIME = 120  # seconds
    RETRY = 1

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    coordinator = models.ForeignKey(Coordinator, null=True, on_delete=models.SET_NULL)
    device_id = models.CharField(max_length=200, default="")
    device_name = models.CharField(max_length=200, default="")
    created_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created = timezone.now()
        return super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return "{}[{}]".format(self.user, self.coordinator)
