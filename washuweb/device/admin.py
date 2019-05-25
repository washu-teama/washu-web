from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display = ["mac", "user", "name", "last_signal", "is_alive"]

    def is_alive(self, obj):
        return obj.is_alive()
    is_alive.allow_tags = True


@admin.register(SmartPlug)
class SmartPlugAdmin(admin.ModelAdmin):
    list_display = ["serial_number", "coordinator", "name"]


@admin.register(SmartPlugEvent)
class SmartPlugEventAdmin(admin.ModelAdmin):
    list_display = ["smartplug", "user", 'event', 'do']


@admin.register(SmartPlugOwner)
class SmartPlugOwnerAdmin(admin.ModelAdmin):
    list_display = ["smartplug", "user", 'grant', 'name']

