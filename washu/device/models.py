from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Coordinator(models.Model):
    mac = models.CharField(max_length=17, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    active = models.BooleanField(default=False)

    def __str__(self):
        return "{}[{}]".format(self.name, self.mac)


class SmartPlug(models.Model):
    serial_number = models.CharField(max_length=20, primary_key=True)
    coordinator = models.ForeignKey(Coordinator, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=32)

    def __str__(self):
        return "{}[{}]".format(self.name, self.serial_number)


class SmartPlugOwner(models.Model):
    COORD = 1
    FAMILY = 2
    GUEST = 3
    GRANT = [(COORD, "coordinator"), (FAMILY, "family"), (GUEST, "guest")]

    smartplug = models.ForeignKey(Coordinator, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    grant = models.IntegerField(choices=GRANT)
    name = models.CharField(max_length=32)

    def __str__(self):
        return "{}[{}] {}".format(self.user, self.grant, self.smartplug)
