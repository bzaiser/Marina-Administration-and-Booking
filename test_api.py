import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marina_project.settings')
django.setup()

from marina.views import api_bookings
from django.test import RequestFactory
from django.contrib.auth.models import User

factory = RequestFactory()
user = User.objects.first()
request = factory.get('/api/bookings/')
request.user = user

response = api_bookings(request)
print(response.content.decode('utf-8')[:500])
