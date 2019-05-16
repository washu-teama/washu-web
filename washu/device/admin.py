from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ["mac", "user", "name"]


@admin.register(SmartPlug)
class SmartPlugAdmin(admin.ModelAdmin):
    list_display = ["serial_number", "coordinator", "name"]


@admin.register(SmartPlugOwner)
class SmartPlugOwnerAdmin(admin.ModelAdmin):
    list_display = ["smartplug", "user", 'grant', 'name']
