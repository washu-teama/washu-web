import logging

from django.views import View
from django.http import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, reverse
from django.http import HttpResponse
from common.utils import get_default_context
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from common.hk_restapi import get_smartplug_api_client
from common.hk_restapi import HKDeviceOfflineException, HKBaseException

log = logging.getLogger('django')


@method_decorator(csrf_exempt, name='dispatch')
class HeartBeatCheckerView(View):
    def post(self, request):
        if "mac" not in request.POST:
            return HttpResponseBadRequest()
        try:
            coordinator = Coordinator.objects.get(pk=request.POST["mac"])
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        coordinator.check_heartbeat()

        return HttpResponse('')


class SmartPlugTurnOnOffView(LoginRequiredMixin, View):
    def get(self, request):
        # TODO(choiking10) make form
        if "serial_number" not in request.GET or "onoff" not in request.GET:
            return HttpResponseBadRequest()
        try:
            plug = SmartPlug.objects.get(pk=request.GET["serial_number"])
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        redirect_to = reverse("smartplug-list")
        if "redirect_to" in request.GET:
            redirect_to = request.GET["redirect_to"]

        try:
            plug.coordinator.onoff(plug.serial_number, int(request.GET["onoff"]))
        except HKDeviceOfflineException:
            plug.status = SmartPlug.DISCONNECT
            plug.save()
            return HttpResponseRedirect(redirect_to=redirect_to)
        except HKBaseException as e:
            log.error("unknown error [{}]".format(e))
            return HttpResponseRedirect(redirect_to=redirect_to)

        plug.status = int(request.GET["onoff"])
        plug.save()

        return HttpResponseRedirect(redirect_to=redirect_to)


class SmartPlugListView(LoginRequiredMixin, View):
    def get(self, request):
        update_device_info()
        sp = SmartPlug.objects.all()
        lists = []
        for plug in sp:
            onoff_url = ""
            if plug.status != SmartPlug.DISCONNECT:
                toggle = SmartPlug.ON if plug.status == SmartPlug.OFF else SmartPlug.OFF
                onoff_url = reverse("onoff") + "?serial_number={}&onoff={}&redirect_to={}".format(
                            plug.serial_number, toggle, reverse("smartplug-list"))

            lists.append({
                "name": plug.name + (" - offline" if plug.status == SmartPlug.DISCONNECT else ""),
                "status": SmartPlug.STATUS_STATIC[plug.status],
                "onoff_url": onoff_url,
                "serial_number": plug.serial_number
            })
        return render(request, 'smartplug/list.html',
                      get_default_context(request, lists=lists))


class SmartPlugConfigView(LoginRequiredMixin, View):
    def get(self, request, serial_number):
        try:
            plug = SmartPlug.objects.get(pk=serial_number)
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        events = SmartPlugEvent.objects.filter(smartplug=plug, user=request.user)

        return render(request, 'smartplug/config.html',
                      get_default_context(request, plug=plug, lists=events))


class SmartPlugEventDeleteView(LoginRequiredMixin, View):
    def post(self, request, serial_number, id):
        try:
            plug = SmartPlug.objects.get(pk=serial_number)
            SmartPlugEvent.objects.get(pk=id, smartplug=plug, user=request.user).delete()
        except ObjectDoesNotExist:
            return HttpResponseNotFound()
        return HttpResponseRedirect(reverse("events", kwargs={"serial_number": serial_number}))


class SmartPlugEventCreateView(LoginRequiredMixin, View):
    def get(self, request, serial_number):
        try:
            plug = SmartPlug.objects.get(pk=serial_number)
        except ObjectDoesNotExist:
            return HttpResponseNotFound()
        events = SmartPlugEvent.objects.filter(smartplug=plug, user=request.user)
        return render(request, 'smartplug/event_create.html',
                      get_default_context(request, plug=plug, lists=events))

    def post(self, request, serial_number):
        try:
            plug = SmartPlug.objects.get(pk=serial_number)
        except ObjectDoesNotExist:
            return HttpResponseNotFound()
        SmartPlugEvent(smartplug=plug,
                       user=request.user,
                       event=int(request.POST["when"]),
                       do=int(request.POST["do"])).save()
        return HttpResponseRedirect(reverse("events", kwargs={"serial_number": serial_number}))


def update_device_info():
    coordinators = Coordinator.objects.all()

    for coordinator in coordinators:
        serials = []
        for plug in SmartPlug.objects.filter(coordinator=coordinator):
            serials.append(plug.serial_number)
        data = coordinator.get_device_power(serials)

        for plug_data in data:
            try:
                plug = SmartPlug.objects.get(pk=plug_data["sn"])
                if plug_data["online"] == 0:
                    plug.status = SmartPlug.DISCONNECT
                else:
                    plug.status = plug_data["switch"][0]
                plug.save()
            except BaseException as e:
                log.error(e)
