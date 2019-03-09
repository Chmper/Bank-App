from rest_framework import generics
from .serializers import UserSerializer, BillSerializer, AccountSerializer
from banking.models import Bill, Account
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import authentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.http import JsonResponse
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login
import json
import requests
from django.views.decorators.csrf import csrf_protect, csrf_exempt



class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class BillViewSet(viewsets.ModelViewSet):
    serializer_class = BillSerializer
    queryset = Bill.objects.all()

class PaymentView(APIView):

    '''
        pass PUT request like(JSON):
        {
            "pin": STRING actaul_pin,
            "account": STRING account_name,
            "bill": INTEGER bill_number,
            "quota": quota_to_pay
        }
    '''

    def put(self, request, format=None):
        json_data = json.loads(request.body)
        pin = json_data['pin']   # STRING
        account = json_data['account'] # STRING
        bill_number = int(json_data['bill']) # STRING
        quota = json_data['quota']

        ### ACCOUNT VALIDATION ###
        try:
            acc = Account.objects.get(user__username=account)
        except:
            return HttpResponse(status=204, content=b'invalid acc')

        ### PIN VALIDATION ###
        if pin != acc.validation_pin:
            return Response(status=status.HTTP_204_NO_CONTENT, data={'error':'inavlid pin'})

        try:
            bill = Bill.objects.get(number=bill_number)
        except:
            return HttpResponse(status=204, content=b'invalid acc')

        if bill.balance < 0:
            return Response(status=status.HTTP_403_FORBIDDEN)


        ### PUT REQUEST ###
        pk = bill.pk
        balance = bill.balance-int(quota)
        data = { "balance": balance,
                 "account": "http://127.0.0.1:8000/api/acounts/"+str(acc.pk)+"/",
                 "number": bill_number
        }
        data_json = json.dumps(data)
        response = requests.put("http://127.0.0.1:8000/api/bills/1/", json=data)
        return Response(response)

    def get_extra_actions(cls):
        return []

@csrf_protect
@api_view(['POST',])
def put_info(request):
    if request.method == 'POST':
        data = {
                 "balance": 123,
                 "account": "http://127.0.0.1:8000/api/acounts/1/",
                 "number": 616710763180
        }
        data_json = json.dumps(data)
        response = requests.put("http://127.0.0.1:8000/api/bills/1/", data=data_json)
        return Response(response)
    return HttpResponse('ni ma')

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},status=HTTP_200_OK)
