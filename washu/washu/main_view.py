from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from common.utils import get_default_context



class Main(View):
    def get(self, request):
        return render(request, 'washu_main.html',
                      get_default_context(request))
