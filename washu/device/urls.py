
from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^coordinator/heartbeat', HeartBeatCheckerView.as_view(), name="heartbeat"),
]
