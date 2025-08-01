# payments/urls.py (Fixed to match your existing views.py)
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Orders Management (matches your existing views)
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Payment Processing (matches your existing views)
    path('initialize/', views.PaymentInitializeView.as_view(), name='payment-initialize'),
    path('verify/<str:reference>/', views.verify_payment, name='payment-verify'),
    
    # Webhooks (matches your existing views)
    path('webhook/paystack/', views.paystack_webhook, name='paystack-webhook'),
    
    # Transactions (matches your existing views)
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    
    # Additional endpoints (you can add these views later)
    path('', views.payments_overview, name='payments-overview'),
]