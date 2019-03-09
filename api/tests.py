from django.test import TestCase

# Create your tests here.
from django.test import Client

client = Client()
response = client.post(url, content_type='application/json')
