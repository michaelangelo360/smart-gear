import hashlib
import hmac
from django.conf import settings
from django.utils import timezone
from .models import Transaction, Order, WebhookEvent
from .services import PaystackService
import logging

logger = logging.getLogger(__name__)

def verify_paystack_signature(payload, signature):
    """Verify Paystack webhook signature"""
    expected_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

def process_webhook_event(event_data):
    """Process Paystack webhook event"""
    event_type = event_data.get('event')
    data = event_data.get('data', {})
    
    # Save webhook event for tracking
    webhook_event = WebhookEvent.objects.create(
        event_type=event_type,
        reference=data.get('reference', ''),
        data=event_data
    )
    
    try:
        if event_type == 'charge.success':
            handle_successful_payment(data)
            webhook_event.processed = True
            webhook_event.save()
        
        elif event_type == 'transfer.success':
            handle_successful_transfer(data)
            webhook_event.processed = True
            webhook_event.save()
        
        elif event_type == 'transfer.failed':
            handle_failed_transfer(data)
            webhook_event.processed = True
            webhook_event.save()
        
        logger.info(f"Webhook event {event_type} processed successfully")
        
    except Exception as e:
        logger.error(f"Error processing webhook event {event_type}: {str(e)}")
        raise

def handle_successful_payment(data):
    """Handle successful payment webhook"""
    reference = data.get('reference')
    
    try:
        transaction = Transaction.objects.get(reference=reference)
        
        if transaction.status == 'pending':
            # Verify payment with Paystack
            paystack_service = PaystackService()
            verification_result = paystack_service.verify_payment(reference)
            
            if verification_result['status'] and verification_result['status'] == 'success':
                # Update transaction
                transaction.status = 'success'
                transaction.paystack_reference = data.get('id')
                transaction.payment_method = data.get('channel', '').lower()
                transaction.gateway_response = str(data)
                transaction.paid_at = timezone.now()
                transaction.save()
                
                # Update order status
                order = transaction.order
                order.status = 'paid'
                order.save()
                
                # Update product stock
                for item in order.items.all():
                    product = item.product
                    if product.stock_quantity >= item.quantity:
                        product.stock_quantity -= item.quantity
                        product.save()
                    else:
                        logger.warning(f"Insufficient stock for product {product.name}")
                
                logger.info(f"Payment successful for transaction {reference}")
            else:
                logger.error(f"Payment verification failed for {reference}")
    
    except Transaction.DoesNotExist:
        logger.error(f"Transaction with reference {reference} not found")

def handle_successful_transfer(data):
    """Handle successful transfer webhook"""
    reference = data.get('reference')
    logger.info(f"Transfer successful: {reference}")
    # Implement transfer success logic if needed

def handle_failed_transfer(data):
    """Handle failed transfer webhook"""
    reference = data.get('reference')
    logger.info(f"Transfer failed: {reference}")
    # Implement transfer failure logic if needed

def generate_transaction_reference():
    """Generate unique transaction reference"""
    import uuid
    import time
    timestamp = str(int(time.time()))
    unique_id = str(uuid.uuid4())[:8]
    return f"SG_{timestamp}_{unique_id}".upper()

def calculate_paystack_fees(amount):
    """Calculate Paystack transaction fees for Ghana"""
    # Paystack charges 1.95% for local transactions in Ghana
    # For international transactions, it's 3.5% + GHS 2
    # This is a simplified calculation for local transactions
    fee = amount * 0.0195
    return fee