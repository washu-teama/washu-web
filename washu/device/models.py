from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.templatetags.static import static
# Create your models here.


class Coordinator(models.Model):
    LIVE_TIME = 120  # seconds

    mac = models.CharField(max_length=17, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    last_signal = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created = timezone.now()
        return super(Coordinator, self).save(*args, **kwargs)

    def check_heartbeat(self):
        self.last_signal = timezone.now()
        self.save()

    def is_alive(self):
        if self.last_signal + timedelta(seconds=self.LIVE_TIME) < timezone.now():
            return False
        return True

    def __str__(self):
        return "{}[{}]".format(self.name, self.mac)


class SmartPlug(models.Model):
    OFF = 0
    ON = 1
    DISCONNECT = 2
    STATUS = [(DISCONNECT, "disconnect"), (ON, "on"), (OFF, "off")]
    STATUS_STATIC = [static("img/off.png"), static("img/on.png"), static("img/disconnect.png")]

    serial_number = models.CharField(max_length=20, primary_key=True)
    coordinator = models.ForeignKey(Coordinator, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=32)
    status = models.IntegerField(choices=STATUS, default=DISCONNECT)
    created_at = models.DateTimeField(editable=False, default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created = timezone.now()
            ret = super(SmartPlug, self).save(*args, **kwargs)
            return ret
        else:
            return super(SmartPlug, self).save(*args, **kwargs)

    def __str__(self):
        return "{}[{}]".format(self.name, self.serial_number)


class SmartPlugOwner(models.Model):
    COORD = 1
    FAMILY = 2
    GUEST = 3
    GRANT = [(COORD, "coordinator"), (FAMILY, "family"), (GUEST, "guest")]
    id = models.AutoField(primary_key=True)
    smartplug = models.ForeignKey(SmartPlug, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grant = models.IntegerField(choices=GRANT)
    name = models.CharField(max_length=32)

    def __str__(self):
        return "{}[{}] {}".format(self.user, self.grant, self.smartplug)


@receiver(post_save, sender=SmartPlug)
def create_relation_between_smartplug_and_coordinator(sender, instance, created, **kwargs):
    if created:
        SmartPlugOwner(
            smartplug=instance,
            user=instance.coordinator.user,
            name=instance.name,
            grant=SmartPlugOwner.COORD
        ).save()
