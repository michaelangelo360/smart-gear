# payments/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal, InvalidOperation
from .models import Order, Transaction
import uuid

User = get_user_model()

# ============================================================================
# ORDER SERIALIZERS
# ============================================================================

class OrderItemSerializer(serializers.Serializer):
    """Serializer for order items (from cart items)"""
    product_id = serializers.IntegerField()
    product_name = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating a new order"""
    shipping_address = serializers.CharField(max_length=500)
    phone_number = serializers.CharField(max_length=20)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_phone_number(self, value):
        """Validate Ghana phone number format"""
        # Remove spaces and special characters
        phone = ''.join(filter(str.isdigit, value))
        
        # Check if it's a valid Ghana number
        if len(phone) == 10 and phone.startswith(('024', '054', '055', '059', '026', '056', '057', '027', '057', '028', '020', '050')):
            return f"+233{phone[1:]}"
        elif len(phone) == 12 and phone.startswith('233'):
            return f"+{phone}"
        elif len(phone) == 13 and phone.startswith('+233'):
            return value
        else:
            raise serializers.ValidationError("Invalid Ghana phone number format")
    
    def validate_shipping_address(self, value):
        """Validate shipping address"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Please provide a complete shipping address")
        return value.strip()

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order details"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user_email', 'user_name', 'status', 
            'status_display', 'total_amount', 'total_amount_formatted',
            'shipping_address', 'phone_number', 'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'order_number', 'user_email', 'created_at', 'updated_at')
    
    def get_user_name(self, obj):
        """Get user's full name"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    
    def get_total_amount_formatted(self, obj):
        """Format total amount for display"""
        return f"GHS {obj.total_amount:,.2f}"

class OrderListSerializer(serializers.ModelSerializer):
    """Simplified serializer for order listing"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    total_amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display', 
            'total_amount', 'total_amount_formatted', 'created_at'
        ]
    
    def get_total_amount_formatted(self, obj):
        return f"GHS {obj.total_amount:,.2f}"

# ============================================================================
# TRANSACTION SERIALIZERS
# ============================================================================

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction details"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    amount_formatted = serializers.SerializerMethodField()
    currency_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'order_number', 'user_email', 'amount', 
            'amount_formatted', 'currency', 'currency_display', 'status', 
            'status_display', 'payment_method', 'gateway_response', 
            'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'reference', 'created_at', 'updated_at')
    
    def get_amount_formatted(self, obj):
        """Format amount for display"""
        return f"GHS {obj.amount:,.2f}"
    
    def get_currency_display(self, obj):
        """Display currency with symbol"""
        return f"{obj.currency} (Ghana Cedis)"

class TransactionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for transaction listing"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'order_number', 'amount', 'amount_formatted',
            'status', 'status_display', 'created_at'
        ]
    
    def get_amount_formatted(self, obj):
        return f"GHS {obj.amount:,.2f}"

# ============================================================================
# PAYMENT INITIALIZATION SERIALIZERS
# ============================================================================

class PaymentInitializeSerializer(serializers.Serializer):
    """Serializer for payment initialization"""
    order_id = serializers.UUIDField()
    callback_url = serializers.URLField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False)
    
    def validate_order_id(self, value):
        """Validate that order exists and belongs to user"""
        user = self.context['request'].user
        try:
            order = Order.objects.get(id=value, user=user, status='pending')
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError(
                "Order not found or not eligible for payment"
            )
    
    def validate_callback_url(self, value):
        """Validate callback URL"""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("Callback URL must start with http:// or https://")
        return value

class PaymentResponseSerializer(serializers.Serializer):
    """Serializer for payment initialization response"""
    status = serializers.BooleanField()
    message = serializers.CharField()
    authorization_url = serializers.URLField()
    access_code = serializers.CharField()
    reference = serializers.CharField()
    transaction_id = serializers.UUIDField()

# ============================================================================
# PAYMENT VERIFICATION SERIALIZERS
# ============================================================================

class PaymentVerificationSerializer(serializers.Serializer):
    """Serializer for payment verification response"""
    status = serializers.BooleanField()
    reference = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    transaction_date = serializers.DateTimeField()
    gateway_response = serializers.CharField()
    channel = serializers.CharField()
    
class PaymentStatusSerializer(serializers.Serializer):
    """Serializer for payment status check"""
    reference = serializers.CharField()
    status = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    order_number = serializers.CharField()
    paid_at = serializers.DateTimeField(allow_null=True)

# ============================================================================
# WEBHOOK SERIALIZERS
# ============================================================================

class WebhookEventSerializer(serializers.Serializer):
    """Serializer for webhook event data"""
    event = serializers.CharField()
    data = serializers.JSONField()
    
    def validate_event(self, value):
        """Validate webhook event type"""
        allowed_events = [
            'charge.success',
            'charge.failed', 
            'transfer.success',
            'transfer.failed'
        ]
        if value not in allowed_events:
            raise serializers.ValidationError(f"Unsupported event type: {value}")
        return value

# ============================================================================
# REFUND SERIALIZERS
# ============================================================================

class RefundCreateSerializer(serializers.Serializer):
    """Serializer for creating refunds"""
    transaction_reference = serializers.CharField()
    amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False
    )
    reason = serializers.CharField(max_length=500)
    customer_note = serializers.CharField(max_length=500, required=False)
    
    def validate_transaction_reference(self, value):
        """Validate that transaction exists and is refundable"""
        try:
            transaction = Transaction.objects.get(
                reference=value, 
                status='success'
            )
            return value
        except Transaction.DoesNotExist:
            raise serializers.ValidationError(
                "Transaction not found or not eligible for refund"
            )
    
    def validate_amount(self, value):
        """Validate refund amount"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Refund amount must be greater than 0")
        return value

class RefundSerializer(serializers.Serializer):
    """Serializer for refund details"""
    id = serializers.CharField()
    transaction_reference = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    status = serializers.CharField()
    reason = serializers.CharField()
    created_at = serializers.DateTimeField()

# ============================================================================
# REPORTS SERIALIZERS
# ============================================================================

class SalesReportSerializer(serializers.Serializer):
    """Serializer for sales reports"""
    period = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    successful_transactions = serializers.IntegerField()
    failed_transactions = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(default='GHS')

class PaymentMethodStatsSerializer(serializers.Serializer):
    """Serializer for payment method statistics"""
    method = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

# ============================================================================
# UTILITY SERIALIZERS
# ============================================================================

class PaymentMethodSerializer(serializers.Serializer):
    """Serializer for available payment methods"""
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    available = serializers.BooleanField()
    supported_currencies = serializers.ListField(
        child=serializers.CharField(),
        default=['GHS']
    )

class CurrencySerializer(serializers.Serializer):
    """Serializer for currency information"""
    code = serializers.CharField()
    name = serializers.CharField()
    symbol = serializers.CharField()
    
class PaymentConfigSerializer(serializers.Serializer):
    """Serializer for payment configuration"""
    currency = CurrencySerializer()
    payment_methods = PaymentMethodSerializer(many=True)
    minimum_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    maximum_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

# ============================================================================
# ERROR SERIALIZERS
# ============================================================================

class PaymentErrorSerializer(serializers.Serializer):
    """Serializer for payment errors"""
    error = serializers.CharField()
    message = serializers.CharField()
    code = serializers.CharField(required=False)
    details = serializers.JSONField(required=False)

class ValidationErrorSerializer(serializers.Serializer):
    """Serializer for validation errors"""
    field = serializers.CharField()
    message = serializers.CharField()
    code = serializers.CharField(required=False)