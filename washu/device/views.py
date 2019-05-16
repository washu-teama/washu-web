from django.views import View
from django.http import *
from .forms import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist


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

