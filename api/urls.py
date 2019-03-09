from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PaymentView, AccountViewSet, BillViewSet

router = DefaultRouter()
router.register('users', UserViewSet, base_name='user')
router.register('bills', BillViewSet, base_name='bill')
router.register('acounts', AccountViewSet, base_name='account')


urlpatterns =[
    path('payment/', PaymentView.as_view(), name='payment'),
    path('put/', views.put_info, name='put')
]

urlpatterns += router.urls
