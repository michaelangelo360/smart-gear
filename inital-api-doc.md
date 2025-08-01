# SmartGear API Documentation

## Accounts & Products API Reference

### Base URL
```
http://localhost:8000/api/v1/
```

### Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Accounts API

### Overview
The Accounts API handles user registration, authentication, and profile management.

### Base Endpoint
```
/api/v1/auth/
```

### Data Models

#### User Model
```json
{
  "id": "integer",
  "email": "string (unique)",
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "phone_number": "string",
  "date_of_birth": "date (YYYY-MM-DD)",
  "is_verified": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

### 🎯 Endpoints

#### 1. Register User
Create a new user account.

**Endpoint:** `POST /api/v1/auth/register/`  
**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+233240123456",
  "password": "securepassword123",
  "password_confirm": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+233240123456",
    "is_verified": false,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "message": "User registered successfully"
}
```

**Validation Rules:**
- Email must be unique and valid
- Username must be unique
- Password minimum 8 characters
- Phone number should be Ghana format (+233XXXXXXXXX)

---

#### 2. Login User
Authenticate user and get JWT tokens.

**Endpoint:** `POST /api/v1/auth/login/`  
**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+233240123456",
    "is_verified": false
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "message": "Login successful"
}
```

---

#### 3. Get User Profile
Retrieve current user's profile information.

**Endpoint:** `GET /api/v1/auth/profile/`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+233240123456",
  "date_of_birth": "1990-05-15",
  "is_verified": false
}
```

---

#### 4. Update User Profile
Update current user's profile information.

**Endpoint:** `PUT /api/v1/auth/profile/`  
**Authentication:** Required

**Request Body:**
```json
{
  "first_name": "John Updated",
  "last_name": "Doe Updated",
  "phone_number": "+233240123457",
  "date_of_birth": "1990-05-15"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John Updated",
  "last_name": "Doe Updated",
  "phone_number": "+233240123457",
  "date_of_birth": "1990-05-15",
  "is_verified": false
}
```

---

#### 5. Refresh JWT Token
Get a new access token using refresh token.

**Endpoint:** `POST /api/v1/auth/token/refresh/`  
**Authentication:** Not required

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 🛍️ Products API

### Overview
The Products API handles product catalog, categories, and shopping cart functionality.

### Base Endpoint
```
/api/v1/products/
```

### Data Models

#### Category Model
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "is_active": "boolean",
  "created_at": "datetime"
}
```

#### Product Model
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "category": "integer (category_id)",
  "category_name": "string",
  "price": "decimal",
  "discount_price": "decimal (nullable)",
  "effective_price": "decimal (computed)",
  "stock_quantity": "integer",
  "sku": "string (unique)",
  "is_active": "boolean",
  "is_featured": "boolean",
  "is_in_stock": "boolean (computed)",
  "created_at": "datetime"
}
```

#### Cart Model
```json
{
  "id": "integer",
  "user": "integer (user_id)",
  "total_amount": "decimal (computed)",
  "total_items": "integer (computed)",
  "items": "array of cart_items",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Cart Item Model
```json
{
  "id": "integer",
  "product": "object (product details)",
  "quantity": "integer",
  "subtotal": "decimal (computed)",
  "created_at": "datetime"
}
```

---

### 🎯 Endpoints

#### 1. Get Categories
Retrieve all active product categories.

**Endpoint:** `GET /api/v1/products/categories/`  
**Authentication:** Not required

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Smartphones",
    "description": "Latest smartphones and mobile devices",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "name": "Laptops",
    "description": "High-performance laptops and notebooks",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

---

#### 2. Get Products
Retrieve paginated list of products with filtering and search.

**Endpoint:** `GET /api/v1/products/`  
**Authentication:** Not required

**Query Parameters:**
- `page` - Page number (default: 1)
- `search` - Search in name and description
- `category` - Filter by category ID
- `is_featured` - Filter featured products (true/false)
- `ordering` - Sort by field (name, price, -created_at)

**Example:** `GET /api/v1/products/?category=1&is_featured=true&search=iphone&ordering=-created_at`

**Response (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "iPhone 15 Pro",
      "description": "Latest iPhone with A17 Pro chip and titanium design",
      "category": 1,
      "category_name": "Smartphones",
      "price": "12000.00",
      "discount_price": "11500.00",
      "effective_price": "11500.00",
      "stock_quantity": 50,
      "sku": "IP15P-128GB",
      "is_active": true,
      "is_featured": true,
      "is_in_stock": true,
      "created_at": "2024-01-15T00:00:00Z"
    }
  ]
}
```

---

#### 3. Get Product Details
Retrieve detailed information about a specific product.

**Endpoint:** `GET /api/v1/products/{product_id}/`  
**Authentication:** Not required

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "iPhone 15 Pro",
  "description": "Latest iPhone with A17 Pro chip and titanium design. Features include:\n\n- A17 Pro chip with 6-core GPU\n- 48MP Main camera\n- Titanium design\n- USB-C connectivity",
  "category": 1,
  "category_name": "Smartphones",
  "price": "12000.00",
  "discount_price": "11500.00",
  "effective_price": "11500.00",
  "stock_quantity": 50,
  "sku": "IP15P-128GB",
  "is_active": true,
  "is_featured": true,
  "is_in_stock": true,
  "created_at": "2024-01-15T00:00:00Z"
}
```

---

#### 4. Get User Cart
Retrieve current user's shopping cart.

**Endpoint:** `GET /api/v1/products/cart/`  
**Authentication:** Required

**Response (200 OK):**
```json
{
  "id": 1,
  "total_amount": "23500.00",
  "total_items": 3,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "iPhone 15 Pro",
        "price": "12000.00",
        "effective_price": "11500.00",
        "sku": "IP15P-128GB"
      },
      "quantity": 2,
      "subtotal": "23000.00",
      "created_at": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "product": {
        "id": 3,
        "name": "USB-C Charger",
        "price": "250.00",
        "effective_price": "250.00",
        "sku": "USBC-65W"
      },
      "quantity": 2,
      "subtotal": "500.00",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

#### 5. Add Item to Cart
Add a product to the user's shopping cart.

**Endpoint:** `POST /api/v1/products/cart/add/`  
**Authentication:** Required

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response (201 Created):**
```json
{
  "message": "Item added to cart successfully",
  "cart_item": {
    "id": 1,
    "product": {
      "id": 1,
      "name": "iPhone 15 Pro",
      "price": "12000.00",
      "effective_price": "11500.00",
      "sku": "IP15P-128GB"
    },
    "quantity": 2,
    "subtotal": "23000.00",
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

**Notes:**
- If item already exists in cart, quantities are merged
- Product must be active and in stock
- Quantity must be positive integer

---

#### 6. Update Cart Item
Update the quantity of an item in the cart.

**Endpoint:** `PUT /api/v1/products/cart/update/{cart_item_id}/`  
**Authentication:** Required

**Request Body:**
```json
{
  "quantity": 3
}
```

**Response (200 OK):**
```json
{
  "message": "Cart item updated successfully",
  "cart_item": {
    "id": 1,
    "product": {
      "id": 1,
      "name": "iPhone 15 Pro",
      "effective_price": "11500.00"
    },
    "quantity": 3,
    "subtotal": "34500.00"
  }
}
```

**Notes:**
- Setting quantity to 0 removes the item
- Quantity must not exceed available stock

---

#### 7. Remove Item from Cart
Remove an item from the user's cart.

**Endpoint:** `DELETE /api/v1/products/cart/remove/{cart_item_id}/`  
**Authentication:** Required

**Response (204 No Content):**
```json
{
  "message": "Item removed from cart successfully"
}
```

---

## 📊 Response Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Resource deleted successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

---

## 🚨 Error Response Format

All API errors follow this consistent format:

```json
{
  "error": "Error message",
  "details": {
    "field_name": ["Specific validation error"]
  }
}
```

### Common Validation Errors

#### User Registration
```json
{
  "error": "Validation failed",
  "details": {
    "email": ["User with this email already exists."],
    "password": ["Password must be at least 8 characters long."]
  }
}
```

#### Add to Cart
```json
{
  "error": "Validation failed",
  "details": {
    "product_id": ["Product not found or not active."],
    "quantity": ["Not enough stock available."]
  }
}
```

---

## 🔧 Usage Examples

### JavaScript/Fetch Examples

#### Register User
```javascript
const response = await fetch('/api/v1/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'johndoe',
    first_name: 'John',
    last_name: 'Doe',
    phone_number: '+233240123456',
    password: 'securepassword123',
    password_confirm: 'securepassword123'
  })
});

const data = await response.json();
if (response.ok) {
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
}
```

#### Get Products with Authentication
```javascript
const token = localStorage.getItem('access_token');
const response = await fetch('/api/v1/products/cart/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
});

const cart = await response.json();
```

#### Add to Cart
```javascript
const token = localStorage.getItem('access_token');
const response = await fetch('/api/v1/products/cart/add/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    product_id: 1,
    quantity: 2
  })
});
```

### cURL Examples

#### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### Get Products
```bash
curl -X GET "http://localhost:8000/api/v1/products/?category=1&is_featured=true"
```

#### Add to Cart
```bash
curl -X POST http://localhost:8000/api/v1/products/cart/add/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

---

## 🌍 Ghana-Specific Features

### Phone Number Validation
The API validates Ghana phone numbers in these formats:
- `+233XXXXXXXXX` (international format)
- `0XXXXXXXXXX` (local format - converted to international)

### Currency
All prices are in **Ghana Cedis (GHS)**:
- Format: `"12000.00"` (string with 2 decimal places)
- Display: `GHS 12,000.00`

### Featured Products
Products marked as featured appear in:
- Homepage product listings
- Special promotions
- Mobile app featured sections

---

## 📝 Notes

1. **Pagination**: All list endpoints use cursor-based pagination with `page` parameter
2. **Filtering**: Products support multiple filter combinations
3. **Search**: Text search works across product name and description
4. **Stock Management**: Cart operations respect product stock levels
5. **User Isolation**: Users can only access their own cart and profile data
6. **Token Expiry**: Access tokens expire after 1 hour, refresh tokens after 7 days