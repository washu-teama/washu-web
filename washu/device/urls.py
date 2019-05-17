
from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^coordinator/heartbeat', HeartBeatCheckerView.as_view(), name="heartbeat"),

    url(r'^smartplug/onoff', SmartPlugTurnOnOffView.as_view(), name="onoff"),
    url(r'^smartplug/list', SmartPlugListView.as_view(), name="smartplug-list"),
    # status - 모든 정보를 다 가져오는 것
    # nearby - 가까운 디바이스 정보만 가져오는 것
    # event handling - 들어왔을 때, 나갔을 때 등 이벤트 헨들링

    #url(r'^smartplug/status', SmartPlugTurnOnOffView.as_view(), name="turn-on-off"),
]
