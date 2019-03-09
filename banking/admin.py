from django.contrib import admin
from .models import Account, Bill, Card, Transfer

admin.site.register(Account)
admin.site.register(Bill)
admin.site.register(Card)
admin.site.register(Transfer)
