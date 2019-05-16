
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from .views import *

urlpatterns = [
    url(r'^login/', LogIn.as_view(), name="login"),
    url(r'^logout/', LogOut.as_view(), name="logout"),
    url(r'^signup/', SignUp.as_view(), name="signup"),
]