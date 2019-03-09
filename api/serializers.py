from django.contrib.auth.models import User
from banking.models import Bill, Account
from rest_framework import serializers

'''
    SERIALIZERS is used to transform the data into JSON
'''


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'pk')

class BillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bill
        fields = ('pk', 'account', 'number', 'balance')

class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ('user', 'validation_pin')
