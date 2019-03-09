from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import random

# Create your models here.

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    validation_pin = models.CharField(max_length=6)


    def __str__(self):
        return self.user.username

class Bill(models.Model):
    favourite = models.ManyToManyField(Account, blank=True, symmetrical=False, related_name='favourites')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='bills')
    number = models.IntegerField()
    balance = models.IntegerField(default=0)

    def __init__(self, *args, **kwargs):
        kwargs['number'] = random.randint(100000000000, 999999999999)
        super().__init__(*args, **kwargs)

    def __str__(self):
        a = str(self.number)
        a = ' '.join([a[i:i+3] for i in range(0, len(a), 3)])
        return a

class Card(models.Model):
    pin = models.IntegerField()
    bill = models.OneToOneField('banking.Bill', on_delete=models.CASCADE)

class Transfer(models.Model):
    sender = models.ForeignKey('banking.Bill', on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey('banking.Bill', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    date = models.DateTimeField(
                    default = timezone.now)
    quota = models.IntegerField()
    who = models.CharField(max_length=50)

    def __str__(self):
        return 'from: '+self.sender.__str__()+' to: '+self.receiver.__str__()

    def update(self):
        self.date = timezone.now()
        self.sender.balance -= self.quota
        self.sender.save()

        self.receiver.balance += self.quota
        self.receiver.save()
