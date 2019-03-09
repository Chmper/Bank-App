from django.urls import path
from . import views
from django.contrib.auth.views import login


urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.log_in, name='login'),
    path('log_out', views.log_out, name='log_out'),
    path('register', views.UserFormView.as_view(), name='register'),
    path('set_pin', views.AccountFormView.as_view(), name='set_pin'),
    path('home', views.HomeView.as_view(), name='home'),
    ### TRANSFERS ###
    path('history', views.TransferHistoryView.as_view(), name='history'),
    path('transfers', views.transfers, name='transfers'),
    path('transfer', views.NormalTransferView.as_view(), name='normal_transfer'),
    path('self_transfer', views.SelfTransferView.as_view(), name='self_transfer'),
    path('periodic', views.PeriodicTransferView.as_view(), name='periodic'),
    path('periodics', views.TaskView.as_view(), name='tasks'),
    ### BILLS ###
    path('bills', views.BillsView.as_view(), name='bills'),
    path('create_bill', views.BillCreateView.as_view(), name='create_bill'),

    ### ADRESS_BOOK ###
    path('adress_book', views.AdressBookView.as_view(), name='address_book'),
    path('add_address', views.AddAddressView.as_view(), name='add_address'),
    path('adress_book/<int:pk>', views.OneAdressView.as_view(), name='one_address')
]
