import os
import sys

sys.path.append(os.path.abspath(".."))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'washu.settings')

import django

django.setup()

from django.utils import timezone
from device.models import SmartPlugEvent

print( SmartPlugEvent.objects.all())
