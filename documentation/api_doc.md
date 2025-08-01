# SmartGear Payment System API Documentation

## Overview
SmartGear is a comprehensive e-commerce payment system built with Django REST Framework and integrated with Paystack payment gateway. The system handles user authentication, product management, cart functionality, order processing, and secure payment transactions.

## Features
- **User Authentication**: JWT-based authentication with registration and login
- **Product Management**: Categories, products, and inventory management
- **Cart System**: Add, update, remove items from cart
- **Order Management**: Create and track orders
- **Payment Integration**: Paystack payment gateway integration
- **Webhook Handling**: Real-time payment status updates
- **Transaction Tracking**: Complete transaction history
- **API Documentation**: Swagger/OpenAPI documentation

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (for Celery)
- Paystack Account

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd smartgear
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_NAME=smartgear_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
PAYSTACK_SECRET_KEY=sk_test_your_paystack_secret_key
PAYSTACK_PUBLIC_KEY=pk_test_your_paystack_public_key
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Database Setup
```bash
# Create PostgreSQL database
createdb smartgear_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Load Sample Data (Optional)
```bash
python manage.py loaddata fixtures/categories.json
python manage.py loaddata fixtures/products.json
```

### 5. Start Development Server
```bash
python manage.py runserver
```

### 6. Start Celery Worker (Optional)
```bash
celery -A smartgear worker -l info
```

## API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register/` | Register new user | No |
| POST | `/api/v1/auth/login/` | User login | No |
| GET/PUT | `/api/v1/auth/profile/` | Get/Update user profile | Yes |
| POST | `/api/v1/auth/token/` | Get JWT token | No |
| POST | `/api/v1/auth/token/refresh/` | Refresh JWT token | No |

### Product Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/products/categories/` | List categories | No |
| GET | `/api/v1/products/` | List products | No |
| GET | `/api/v1/products/{id}/` | Get product details | No |
| GET | `/api/v1/products/cart/` | Get user cart | Yes |
| POST | `/api/v1/products/cart/add/` | Add item to cart | Yes |
| PUT | `/api/v1/products/cart/update/{item_id}/` | Update cart item | Yes |
| DELETE | `/api/v1/products/cart/remove/{item_id}/` | Remove from cart | Yes |

### Payment Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/payments/orders/` | List user orders | Yes |
| POST | `/api/v1/payments/orders/create/` | Create new order | Yes |
| GET | `/api/v1/payments/orders/{id}/` | Get order details | Yes |
| POST | `/api/v1/payments/initialize/` | Initialize payment | Yes |
| GET | `/api/v1/payments/verify/{reference}/` | Verify payment | Yes |
| POST | `/api/v1/payments/webhook/paystack/` | Paystack webhook | No |
| GET | `/api/v1/payments/transactions/` | List transactions | Yes |
| GET | `/api/v1/payments/transactions/{id}/` | Get transaction details | Yes |

## API Usage Examples

### 1. User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+233240123456",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### 2. User Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 3. Add Item to Cart
```bash
curl -X POST http://localhost:8000/api/v1/products/cart/add/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### 4. Create Order
```bash
curl -X POST http://localhost:8000/api/v1/payments/orders/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "shipping_address": "123 Tech Street, East Legon, Accra, Ghana",
    "phone_number": "+233240123456",
    "notes": "Please deliver during office hours"
  }'
```

### 5. Initialize Payment
```bash
curl -X POST http://localhost:8000/api/v1/payments/initialize/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "callback_url": "https://yourfrontend.com/payment/callback"
  }'
```

### 6. Verify Payment
```bash
curl -X GET http://localhost:8000/api/v1/payments/verify/{reference}/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Response Formats

### Success Response
```json
{
  "status": true,
  "message": "Operation successful",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "status": false,
  "error": "Error message",
  "details": {
    // Error details if applicable
  }
}
```

## Webhook Configuration

### Paystack Webhook Setup
1. Login to your Paystack dashboard
2. Go to Settings > Webhooks
3. Add webhook URL: `https://yourdomain.com/api/v1/payments/webhook/paystack/`
4. Select events: `charge.success`, `transfer.success`, `transfer.failed`

### Webhook Events Handled
- `charge.success`: Payment successful
- `transfer.success`: Transfer successful
- `transfer.failed`: Transfer failed

## Security Features

### Authentication
- JWT-based authentication
- Token refresh mechanism
- User session management

### Payment Security
- Webhook signature verification
- Transaction reference validation
- Secure payment processing

### Data Protection
- Input validation and sanitization
- SQL injection protection
- XSS protection

## Testing

### Unit Tests
```bash
python manage.py test
```

### API Testing with Postman
Import the provided Postman collection and environment files.

## Deployment

### Production Settings
1. Set `DEBUG=False`
2. Configure production database
3. Set up static file serving
4. Configure HTTPS
5. Set up monitoring and logging

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "smartgear.wsgi:application"]
```

## Monitoring & Logging

### Logging Configuration
- Application logs stored in `smartgear.log`
- Payment-specific logs for transaction tracking
- Error logging for debugging

### Health Checks
- Database connection status
- Paystack API connectivity
- Redis connection (if using Celery)

## Support & Maintenance

### Common Issues
1. **Payment verification fails**: Check Paystack credentials
2. **Webhook not received**: Verify webhook URL and signature
3. **Database connection errors**: Check database configuration

### Performance Optimization
- Database query optimization
- Caching strategies
- Background task processing with Celery

## API Documentation
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`
- JSON Schema: `http://localhost:8000/swagger.json`