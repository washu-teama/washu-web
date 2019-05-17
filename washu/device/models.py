from datetime import datetime, timedelta
from logging import getLogger

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.templatetags.static import static

from common.hk_restapi import SmartPlugAPIClient, HKBaseException, HKAccessTokenException
# Create your models here.

log = getLogger('django')


class Coordinator(models.Model):
    LIVE_TIME = 120  # seconds
    RETRY = 1

    mac = models.CharField(max_length=17, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    last_signal = models.DateTimeField(default=timezone.now)
    hk_id = models.CharField(max_length=100, default="")
    hk_pwd = models.CharField(max_length=200, default="")
    access_token = models.CharField(max_length=200, default="")
    access_token_expired_at = models.DateTimeField(default=timezone.now)
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

    def get_hk_client(self):
        config = settings.HK_NETWORKS_CONFIG
        api_client = SmartPlugAPIClient(client_id=config["client_id"], client_secret=config["client_secret"])
        if self.access_token_expired_at <= timezone.now():
            api_client.login(self.hk_id, self.hk_pwd)
            api_client.get_token()
            self.access_token = api_client.access_token
            self.access_token_expired_at = api_client.access_token_expired_at
            self.save()
        else:
            api_client.set_token(self.access_token, self.access_token_expired_at)
        return api_client

    def onoff(self, serial_number, state, retry=RETRY):
        try:
            return self.get_hk_client().onoff(serial_number, state)
        except HKAccessTokenException as e:
            log.error("[on/off fail] Access token error: [{}]".format(e))
            self.access_token_expired_at = timezone.now()
            self.save()
            if retry >= 1:
                return self.onoff(serial_number, state, retry-1)

    def get_device_info(self, device="all", retry=RETRY):
        try:
            return self.get_hk_client().get_device_info(device)
        except HKAccessTokenException as e:
            log.error("[on/off fail] Access token error: [{}]".format(e))
            self.access_token_expired_at = timezone.now()
            self.save()
            if retry >= 1:
                return self.get_device_info(device, retry-1)

    def get_device_power(self, serial_numbers: list, retry=RETRY):
        try:
            return self.get_hk_client().get_device_power(serial_numbers)
        except HKAccessTokenException as e:
            log.error("[on/off fail] Access token error: [{}]".format(e))
            self.access_token_expired_at = timezone.now()
            self.save()
            if retry >= 1:
                return self.get_device_power(serial_numbers, retry-1)

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
