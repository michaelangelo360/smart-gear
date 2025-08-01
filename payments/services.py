import requests
import logging
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from .models import Transaction, Order

logger = logging.getLogger(__name__)

class PaystackService:
    """Service class for Paystack API integration"""
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = settings.PAYSTACK_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, method, endpoint, data=None):
        """Make HTTP request to Paystack API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=self.headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack API request failed: {str(e)}")
            raise Exception(f"Payment service error: {str(e)}")
    
    def initialize_payment(self, email, amount, reference, callback_url=None, metadata=None):
        """Initialize payment transaction"""
        # Convert amount to kobo (Paystack expects amount in kobo)
        amount_kobo = int(amount * 100)
        
        data = {
            'email': email,
            'amount': amount_kobo,
            'reference': reference,
            'currency': 'GHS',
        }
        
        if callback_url:
            data['callback_url'] = callback_url
        
        if metadata:
            data['metadata'] = metadata
        
        logger.info(f"Initializing payment for {email}, amount: {amount}, reference: {reference}")
        
        response = self._make_request('POST', '/transaction/initialize', data)
        
        if response.get('status'):
            return {
                'status': True,
                'authorization_url': response['data']['authorization_url'],
                'access_code': response['data']['access_code'],
                'reference': response['data']['reference']
            }
        else:
            raise Exception(f"Payment initialization failed: {response.get('message', 'Unknown error')}")
    
    def verify_payment(self, reference):
        """Verify payment transaction"""
        logger.info(f"Verifying payment with reference: {reference}")
        
        response = self._make_request('GET', f'/transaction/verify/{reference}')
        
        if response.get('status'):
            data = response['data']
            return {
                'status': True,
                'reference': data['reference'],
                'amount': Decimal(data['amount']) / 100,  # Convert from kobo to naira
                'currency': data['currency'],
                'transaction_date': data['transaction_date'],
                'status': data['status'],
                'gateway_response': data['gateway_response'],
                'channel': data['channel'],
                'customer': data['customer'],
                'authorization': data.get('authorization', {}),
                'metadata': data.get('metadata', {})
            }
        else:
            return {
                'status': False,
                'message': response.get('message', 'Verification failed')
            }
    
    def list_transactions(self, page=1, per_page=50):
        """List transactions"""
        params = {
            'page': page,
            'perPage': per_page
        }
        
        response = self._make_request('GET', '/transaction')
        return response
    
    def fetch_transaction(self, transaction_id):
        """Fetch single transaction"""
        response = self._make_request('GET', f'/transaction/{transaction_id}')
        return response
    
    def create_customer(self, email, first_name, last_name, phone=None):
        """Create customer on Paystack"""
        data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
        }
        
        if phone:
            data['phone'] = phone
        
        response = self._make_request('POST', '/customer', data)
        return response
    
    def create_refund(self, transaction_reference, amount=None, currency='GHS', customer_note=None, merchant_note=None):
        """Create refund for a transaction"""
        data = {
            'transaction': transaction_reference,
            'currency': currency,
        }
        
        if amount:
            data['amount'] = int(amount * 100)  # Convert to kobo
        
        if customer_note:
            data['customer_note'] = customer_note
        
        if merchant_note:
            data['merchant_note'] = merchant_note
        
        response = self._make_request('POST', '/refund', data)
        return response
