from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
import json
import logging
from .models import Order, Transaction, WebhookEvent
from .serializers import (
    OrderSerializer, OrderCreateSerializer, 
    TransactionSerializer, PaymentInitializeSerializer
)
from .services import PaystackService
from .utils import verify_paystack_signature, process_webhook_event, generate_transaction_reference
from products.models import Cart

logger = logging.getLogger(__name__)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if user has items in cart
        try:
            cart = Cart.objects.get(user=request.user)
            if not cart.items.exists():
                return Response({
                    'error': 'Your cart is empty'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({
                'error': 'Cart not found'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        return Response({
            'message': 'Order created successfully',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_201_CREATED)

class PaymentInitializeView(generics.GenericAPIView):
    serializer_class = PaymentInitializeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        callback_url = serializer.validated_data.get('callback_url')
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Create transaction record
            reference = generate_transaction_reference()
            transaction = Transaction.objects.create(
                order=order,
                user=request.user,
                reference=reference,
                amount=order.total_amount,
                currency='GHS'
            )
            
            # Initialize payment with Paystack
            paystack_service = PaystackService()
            
            metadata = {
                'order_id': str(order.id),
                'order_number': order.order_number,
                'user_id': request.user.id,
                'transaction_id': str(transaction.id)
            }
            
            result = paystack_service.initialize_payment(
                email=request.user.email,
                amount=order.total_amount,
                reference=reference,
                callback_url=callback_url,
                metadata=metadata
            )
            
            if result['status']:
                transaction.paystack_reference = result['reference']
                transaction.save()
                
                return Response({
                    'status': True,
                    'message': 'Payment initialized successfully',
                    'data': {
                        'authorization_url': result['authorization_url'],
                        'access_code': result['access_code'],
                        'reference': result['reference'],
                        'transaction_id': str(transaction.id)
                    }
                })
            else:
                transaction.status = 'failed'
                transaction.save()
                return Response({
                    'status': False,
                    'message': 'Payment initialization failed'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Order.DoesNotExist:
            return Response({
                'error': 'Order not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Payment initialization error: {str(e)}")
            return Response({
                'error': 'Payment initialization failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def payments_overview(request):
    """API overview for payments endpoints"""
    return Response({
        'message': 'SmartGear Payments API',
        'version': '1.0',
        'currency': 'GHS (Ghana Cedis)',
        'country': 'Ghana',
        'endpoints': {
            'orders': {
                'list': '/api/v1/payments/orders/',
                'create': '/api/v1/payments/orders/create/',
                'detail': '/api/v1/payments/orders/{id}/',
            },
            'payments': {
                'initialize': '/api/v1/payments/initialize/',
                'verify': '/api/v1/payments/verify/{reference}/',
            },
            'transactions': {
                'list': '/api/v1/payments/transactions/',
                'detail': '/api/v1/payments/transactions/{id}/',
            },
            'webhooks': {
                'paystack': '/api/v1/payments/webhook/paystack/',
            },
        },
        'features': [
            'Paystack Ghana Integration',
            'Mobile Money Support', 
            'Card Payments',
            'Bank Transfer',
            'Real-time Webhooks'
        ],
        'status': 'active'
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_payment(request, reference):
    """Verify payment status"""
    try:
        transaction = Transaction.objects.get(reference=reference, user=request.user)
        
        if transaction.status == 'success':
            return Response({
                'status': True,
                'message': 'Payment already verified',
                'data': TransactionSerializer(transaction).data
            })
        
        # Verify with Paystack
        paystack_service = PaystackService()
        result = paystack_service.verify_payment(reference)
        
        if result['status']:
            if result['status'] == 'success':
                transaction.status = 'success'
                transaction.payment_method = result.get('channel', '').lower()
                transaction.gateway_response = str(result)
                transaction.paid_at = timezone.now()
                transaction.save()
                
                # Update order status
                order = transaction.order
                order.status = 'paid'
                order.save()
                
                return Response({
                    'status': True,
                    'message': 'Payment verified successfully',
                    'data': TransactionSerializer(transaction).data
                })
            else:
                transaction.status = 'failed'
                transaction.gateway_response = str(result)
                transaction.save()
                
                return Response({
                    'status': False,
                    'message': f"Payment {result['status']}",
                    'data': TransactionSerializer(transaction).data
                })
        else:
            return Response({
                'status': False,
                'message': result.get('message', 'Verification failed')
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Transaction.DoesNotExist:
        return Response({
            'error': 'Transaction not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Payment verification error: {str(e)}")
        return Response({
            'error': 'Payment verification failed'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paystack_webhook(request):
    """Handle Paystack webhook events"""
    payload = request.body
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
    
    # Verify webhook signature
    if not verify_paystack_signature(payload, signature):
        logger.warning("Invalid webhook signature")
        return HttpResponse(status=400)
    
    try:
        event_data = json.loads(payload)
        process_webhook_event(event_data)
        
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return HttpResponse(status=500)

class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)