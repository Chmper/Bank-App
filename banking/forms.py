from django import forms
from .models import Account, Transfer, Bill
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username', 'email', 'password',)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'input100', 'placeholder': 'username'})
        self.fields['email'].widget.attrs.update({'class': 'input100', 'placeholder': 'email'})
        self.fields['password'].widget.attrs.update({'class': 'input100', 'placeholder': 'password'})

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('validation_pin',)

    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.fields['validation_pin'].widget.attrs.update({'class': 'input100', 'placeholder': 'pin'})

class UserLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', )

class TransferForm(forms.ModelForm):
    receiver = forms.CharField(max_length=12, min_length=12)
    quota = forms.CharField(max_length=10000)
    class Meta:
        model = Transfer
        fields = ('who', 'title',)


class SelfTransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ('receiver', 'sender', 'quota',)

    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options')
        super(SelfTransferForm, self).__init__(*args, **kwargs)
        self.fields['receiver'].queryset = options
        self.fields['sender'].queryset = options

class PeriodicTransfer(forms.ModelForm):
    choices = (
        ('d','day'),
        ('m','month'),
        ('y', 'year'))

    receiver = forms.CharField()
    quota = forms.CharField(max_length=10000)
    counter = forms.IntegerField(widget=forms.TextInput)
    selects = forms.ChoiceField(choices=choices)

    class Meta:
        model = Transfer
        fields = ('who', 'title',)
