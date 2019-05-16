from django.views import View
from django.http import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from .models import *
from common.hk_restapi import get_smartplug_api_client


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


@method_decorator(csrf_exempt, name='dispatch')
class SmartPlugTurnOnOffView(View):
    def post(self, request):
        # TODO(choiking10) make form
        if "serial_number" not in request.POST or "onoff" not in request.POST:
            return HttpResponseBadRequest()
        try:
            plug = SmartPlug.objects.get(pk=request.POST["serial_number"])
        except ObjectDoesNotExist:
            return HttpResponseNotFound()

        hk = get_smartplug_api_client()

        hk.onoff(plug.serial_number, int(request.POST["onoff"]))

        return HttpResponse('')


