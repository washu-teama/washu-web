import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(".."))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'washu.settings')

import django

django.setup()
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from device.models import SmartPlugEvent, SmartPlug, Coordinator
from django.db.models.aggregates import Max
from wauser.models import Location


LEAVE_TIME = 60

enter = SmartPlugEvent.objects.filter(event=SmartPlugEvent.ENTER)
leave = SmartPlugEvent.objects.filter(event=SmartPlugEvent.LEAVE)

def get_id(query):
    return "{}[{}]".format(query["user"], query["coordinator"])


def detect_event():
    unique_recently = Location.objects.values('user', 'coordinator').annotate(recently=Max("created_at"))
    for query in unique_recently:
        print(query)
        pid = get_id(query)
        user = query["user"]
        coordinator = query["coordinator"]
        value = cache.get(pid)
        if value:
            if timezone.now() - query["recently"] >= timedelta(seconds=LEAVE_TIME):
                print(pid + "  leave")
                cache.set(pid, query["recently"], 1)
                leave_processing(user, coordinator)
            else:
                cache.set(pid,  query["recently"], LEAVE_TIME*2)
                print(pid + "in")

        else:
            if timezone.now() - query["recently"] <= timedelta(seconds=LEAVE_TIME):
                print(pid + " enter")
                cache.set(pid,  query["recently"], LEAVE_TIME*2)
                enter_processing(user, coordinator)
            else:
                # nothing
                pass


def enter_processing(user, coordinator):
    plugs = SmartPlug.objects.filter(coordinator=coordinator)
    coordinator = Coordinator.objects.get(pk=coordinator)
    for plug in plugs:
        result = enter.filter(user=user, smartplug=plug)
        for event in result:
            print("enter: user {} turn {} the {}".format(user, event.get_do_display(), plug))
            coordinator.onoff(plug.serial_number, event.do)


def leave_processing(user, coordinator):
    plugs = SmartPlug.objects.filter(coordinator=coordinator)
    coordinator = Coordinator.objects.get(pk=coordinator)
    user = User.objects.get(pk=user)
    for plug in plugs:
        result = leave.filter(user_id=user, smartplug=plug)
        for event in result:
            print("leave: user {} turn {} the {}".format(user, event.get_do_display(), plug))
            coordinator.onoff(plug.serial_number, event.do)


detect_event()

