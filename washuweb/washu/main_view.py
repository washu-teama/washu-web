from django.views import View
from django.http import *
from django.urls import reverse



class Main(View):
    def get(self, request):
        return HttpResponseRedirect(reverse('smartplug-list'))
