from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.template import RequestContext
from .models import Bill, Account, Transfer, Card
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import generic
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.views.generic import View
from django.db import transaction
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.http import Http404, HttpResponseRedirect
from .forms import UserForm, PeriodicTransfer, AccountForm, TransferForm, SelfTransferForm
from background_task import background
from background_task.models import Task
from django.core import serializers


def index(request):
    try:
        User.objects.get(username=request.user.username)
        return redirect('home')
    except:
        return render(request, 'registration/index.html')

class HomeView(generic.ListView):
    template_name = 'banking/overview.html'
    context_object_name = 'transfers'
    model = Account

    def get_queryset(self):
        bills = self.request.user.account.bills.all()

        queryset =  Bill.objects.none()

        for bill in bills:
            queryset = queryset | Transfer.objects.filter(Q(sender=bill) | Q(receiver=bill))
        return queryset.order_by('-date')[:5]

    def get_context_data(self, **kwargs):
        sum = 0
        for bill in self.request.user.account.bills.all():
            sum += bill.balance
        context = super().get_context_data(**kwargs)
        context['sum'] = sum
        return context

###############################################################################

class UserFormView(View):
    form_class = UserForm
    template_name = 'registration/register.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            username = form.cleaned_data['username']
            password = form.cleaned_data['username']
            email = form.cleaned_data['username']

            user.set_password(password)
            user.save()

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('set_pin')

        return HttpResponse('blad')

class AccountFormView(View):
    template_name = 'registration/set_pin.html'
    form_class = AccountForm

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            account = form.save(commit=False)

            pin = form.cleaned_data['validation_pin']

            account.user = self.request.user
            account.save()
            Bill.objects.create(account=account)

            return HttpResponseRedirect(reverse_lazy('home'))

        else:
            return HttpResponseRedirect(reverse_lazy('set_pin', {'message'}))

def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse('asd')

def log_out(request):
    logout(request)
    return redirect('index')

###############################################################################

def transfers(request):
    return render(request, 'banking/transfers.html')

class NormalTransferView(View):
    form_class = TransferForm
    template_name = 'banking/normal_transfer.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            transfer = form.save(commit=False)
            sender = request.user.account.bills.all()[0]

            title = form.cleaned_data['title']
            receiver_bill = form.cleaned_data['receiver']
            who = form.cleaned_data['who']
            quota = int(form.cleaned_data['quota'])

            try:
                receiver_bill = Bill.objects.get(number=int(receiver_bill))
            except:
                return HttpResponse('There\'s no bill liek this')


            sender.balance -= quota
            receiver_bill.balance += quota
            sender.save()
            receiver_bill.save()

            transfer.sender = sender
            transfer.title = title
            transfer.who = who
            transfer.quota = quota
            transfer.receiver = receiver_bill
            transfer.save()

            return redirect('home')

class SelfTransferView(View):
    template_name = 'banking/self_transfer.html'
    form_class = SelfTransferForm

    def get(self, request):
        form = self.form_class(options=self.get_options())
        return render(request, self.template_name, {'form': form, 'is_avaiable:': True})

    def post(self, request):
        form = self.form_class(request.POST, options=self.get_options())

        if form.is_valid():
            transfer = form.save(commit=False)

            sender = form.cleaned_data['sender']
            receiver = form.cleaned_data['receiver']
            quota = form.cleaned_data['quota']

            sender.balance -= quota
            receiver.balance += quota
            sender.save()
            receiver.save()

            transfer.sender = sender
            transfer.quota = quota
            transfer.receiver = receiver
            transfer.save()

            return redirect('home')

    def get_options(self):
        return Bill.objects.filter(account=self.request.user.account)


class TransferHistoryView(generic.ListView):
    model = Transfer
    context_object_name = 'transfers'
    template_name = 'banking/history.html'

    def get_queryset(self):
        return Transfer.objects.all().order_by('-date')

class PeriodicTransferView(View):
    template_name = 'banking/periodic_transfer.html'
    form_class = PeriodicTransfer

    @background(schedule=60)
    def send_trasnfer(sender, receiver, quota, title, who):
        sender = Bill.objects.get(number=sender)
        receiver = Bill.objects.get(number=receiver)
        print('hejka')
        Transfer(sender=sender, receiver=receiver, quota=quota, title=title, who=who).save()

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            transfer = form.save(commit=False)
            sender = request.user.account.bills.all()[0]

            title = form.cleaned_data['title']
            receiver_bill = form.cleaned_data['receiver']
            who = form.cleaned_data['who']
            quota = int(form.cleaned_data['quota'])
            selects = form.cleaned_data['selects']
            counter = int(form.cleaned_data['counter'])

            try:
                receiver_bill = Bill.objects.get(number=int(receiver_bill))
            except:
                return HttpResponse('There\'s no bill liek this')


            sender.balance -= quota
            receiver_bill.balance += quota
            sender.save()
            receiver_bill.save()

            transfer.sender = sender
            transfer.title = title
            transfer.who = who
            transfer.quota = quota
            transfer.receiver = receiver_bill
            transfer.save()

            if selects == 'd':
                seconds = 24*60*60*counter
                self.send_trasnfer(
                    sender = sender.number,
                    receiver = receiver_bill.number,
                    quota = quota,
                    title = title,
                    who = who, repeat=24*60*60*counter)

#send_trasnfer(self, sender, receiver, quota, title, who):
            return redirect('home')

class TaskView(generic.ListView):
    model = Task
    template_name = 'banking/tasks.html'

###############################################################################

class BillsView(generic.ListView):
    model = Bill
    template_name = 'banking/bills.html'
    context_object_name = 'bills'

    def get_queryset(self):
        return Bill.objects.filter(account=self.request.user.account)

class BillCreateView(View):
    def get(self, request, *args, **kwrags):
        Bill(account=self.request.user.account).save()
        return HttpResponseRedirect('bills')

###############################################################################

class AdressBookView(generic.ListView):
    model = Bill
    template_name = 'banking/book_list.html'

class OneAdressView(generic.DetailView):
    model = Bill
    template_name = 'banking/book_list.html'
    context_object_name = 'bill'

class AddAddressView(View):
    template_name = 'banking/add_address.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        data = request.POST.dict()
        number = data.get('number')

        try:
            bill = Bill.objects.get(number=number)
        except:
            return render(request, 'banking/book_list.html', context={'message': 'Theres no bill like this'})

        request.user.account.favourites.add(bill)
        request.user.account.save()

        return HttpResponseRedirect('adress_book')
