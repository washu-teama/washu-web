from django.contrib import admin
from .models import Location
# Register your models here.


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "coordinator", "device_id", "created_at"]

    def is_alive(self, obj):
        return obj.is_alive()
    is_alive.allow_tags = True
