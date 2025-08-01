# payments/urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'payments'

urlpatterns = [
    # Orders Management
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<uuid:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Payment Processing
    path('initialize/', views.PaymentInitializeView.as_view(), name='payment-initialize'),
    path('verify/<str:reference>/', views.verify_payment, name='payment-verify'),
    path('callback/', views.payment_callback, name='payment-callback'),
    
    # Webhooks
    path('webhook/paystack/', csrf_exempt(views.paystack_webhook), name='paystack-webhook'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    
    # Payment Methods & Status
    path('methods/', views.payment_methods, name='payment-methods'),
    path('status/<str:reference>/', views.payment_status, name='payment-status'),
    
    # Refunds (for future use)
    path('refunds/', views.RefundListView.as_view(), name='refund-list'),
    path('refunds/create/', views.create_refund, name='create-refund'),
    
    # Reports and Analytics (admin only)
    path('reports/daily/', views.daily_sales_report, name='daily-sales-report'),
    path('reports/monthly/', views.monthly_sales_report, name='monthly-sales-report'),
    
    # Test endpoints (development only)
    path('test/paystack/', views.test_paystack_connection, name='test-paystack'),
    
    # API endpoints overview
    path('', views.payments_api_overview, name='payments-overview'),
]

# Additional URL patterns for nested resources (if needed)
order_patterns = [
    path('orders/<uuid:order_id>/items/', views.OrderItemListView.as_view(), name='order-items'),
    path('orders/<uuid:order_id>/transactions/', views.OrderTransactionListView.as_view(), name='order-transactions'),
    path('orders/<uuid:order_id>/cancel/', views.cancel_order, name='cancel-order'),
]

# Add nested patterns to main urlpatterns
urlpatterns += order_patterns