# products/views.py
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Category, Product, Cart, CartItem
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateUpdateSerializer, CartSerializer, CartItemSerializer,
    AddToCartSerializer, UpdateCartItemSerializer, ProductSearchSerializer
)

# API Overview
@swagger_auto_schema(
    method='get',
    operation_description="Get products API overview",
    responses={200: "Products API endpoints overview"},
    tags=['Products Overview']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def products_overview(request):
    """Products API overview"""
    return Response({
        'message': 'SmartGear Products API',
        'version': '1.0',
        'endpoints': {
            'categories': '/api/v1/products/categories/',
            'products': '/api/v1/products/',
            'featured_products': '/api/v1/products/featured/',
            'search': '/api/v1/products/search/',
            'cart': '/api/v1/products/cart/',
            'add_to_cart': '/api/v1/products/cart/add/',
        },
        'features': [
            'Product Catalog',
            'Category Management',
            'Shopping Cart',
            'Product Search & Filtering',
            'Featured Products',
            'Stock Management',
            'Ghana Cedis Pricing'
        ]
    })

# =============================================================================
# CATEGORY VIEWS
# =============================================================================

class CategoryListView(generics.ListAPIView):
    """List all active categories"""
    queryset = Category.objects.filter(is_active=True).order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get list of product categories",
        responses={200: CategorySerializer(many=True)},
        tags=['Categories']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CategoryDetailView(generics.RetrieveAPIView):
    """Get category details"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get category details by ID",
        responses={
            200: CategorySerializer,
            404: "Category not found"
        },
        tags=['Categories']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CategoryProductsView(generics.ListAPIView):
    """Get products in a specific category"""
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_description="Get products in a specific category",
        manual_parameters=[
            openapi.Parameter('category_id', openapi.IN_PATH, description="Category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in product name/description", type=openapi.TYPE_STRING),
            openapi.Parameter('is_featured', openapi.IN_QUERY, description="Filter featured products", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING),
        ],
        responses={200: ProductListSerializer(many=True)},
        tags=['Categories']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.filter(
            category_id=category_id,
            is_active=True
        ).select_related('category')

class CategoryCreateView(generics.CreateAPIView):
    """Create new category (Admin only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Create new category (Admin only)",
        request_body=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: "Validation errors",
            403: "Admin access required"
        },
        tags=['Categories']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# =============================================================================
# PRODUCT VIEWS
# =============================================================================

class ProductListView(generics.ListAPIView):
    """List all active products with filtering and search"""
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_description="Get paginated list of products with filtering and search",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in name/description/SKU", type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('is_featured', openapi.IN_QUERY, description="Filter featured products", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field (name, price, -created_at)", type=openapi.TYPE_STRING),
        ],
        responses={200: ProductListSerializer(many=True)},
        tags=['Products']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProductDetailView(generics.RetrieveAPIView):
    """Get detailed product information"""
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get detailed product information by ID",
        responses={
            200: ProductDetailSerializer,
            404: "Product not found"
        },
        tags=['Products']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class FeaturedProductsView(generics.ListAPIView):
    """Get featured products"""
    queryset = Product.objects.filter(is_active=True, is_featured=True).select_related('category')
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    ordering = ['-created_at']

    @swagger_auto_schema(
        operation_description="Get list of featured products",
        responses={200: ProductListSerializer(many=True)},
        tags=['Products']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProductSearchView(generics.ListAPIView):
    """Advanced product search"""
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Advanced product search with multiple filters",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search term", type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER),
            openapi.Parameter('is_featured', openapi.IN_QUERY, description="Featured products only", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('in_stock_only', openapi.IN_QUERY, description="In stock products only", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field", type=openapi.TYPE_STRING),
        ],
        responses={200: ProductListSerializer(many=True)},
        tags=['Products']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Search term
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(sku__icontains=search)
            )
        
        # Category filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Price range filters
        min_price = self.request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Featured filter
        is_featured = self.request.query_params.get('is_featured')
        if is_featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # In stock filter
        in_stock_only = self.request.query_params.get('in_stock_only')
        if in_stock_only == 'true':
            queryset = queryset.filter(stock_quantity__gt=0)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering in ['name', '-name', 'price', '-price', 'created_at', '-created_at', 'stock_quantity', '-stock_quantity']:
            queryset = queryset.order_by(ordering)
        
        return queryset

class ProductBySkuView(generics.RetrieveAPIView):
    """Get product by SKU"""
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'sku'

    @swagger_auto_schema(
        operation_description="Get product by SKU",
        responses={
            200: ProductDetailSerializer,
            404: "Product not found"
        },
        tags=['Products']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

class ProductCreateView(generics.CreateAPIView):
    """Create new product (Admin only)"""
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Create new product (Admin only)",
        request_body=ProductCreateUpdateSerializer,
        responses={
            201: ProductCreateUpdateSerializer,
            400: "Validation errors",
            403: "Admin access required"
        },
        tags=['Products']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ProductUpdateView(generics.UpdateAPIView):
    """Update product (Admin only)"""
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Update product (Admin only)",
        request_body=ProductCreateUpdateSerializer,
        responses={
            200: ProductCreateUpdateSerializer,
            400: "Validation errors",
            403: "Admin access required",
            404: "Product not found"
        },
        tags=['Products']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update product (Admin only)",
        request_body=ProductCreateUpdateSerializer,
        responses={
            200: ProductCreateUpdateSerializer,
            400: "Validation errors",
            403: "Admin access required",
            404: "Product not found"
        },
        tags=['Products']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

# =============================================================================
# CART VIEWS
# =============================================================================

class CartView(generics.RetrieveAPIView):
    """Get user's shopping cart"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current user's shopping cart",
        responses={
            200: CartSerializer,
            401: "Authentication required"
        },
        tags=['Shopping Cart']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(generics.CreateAPIView):
    """Add item to shopping cart"""
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add item to shopping cart",
        request_body=AddToCartSerializer,
        responses={
            201: openapi.Response(
                description="Item added to cart successfully",
                examples={
                    "application/json": {
                        "message": "Item added to cart successfully",
                        "cart_item": {
                            "id": 1,
                            "product": {"id": 1, "name": "iPhone 15"},
                            "quantity": 2,
                            "subtotal": "23000.00"
                        }
                    }
                }
            ),
            400: "Validation errors",
            401: "Authentication required"
        },
        tags=['Shopping Cart']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Check if item already exists in cart
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not item_created:
                # Update existing item quantity
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response({
                'message': 'Item added to cart successfully',
                'cart_item': CartItemSerializer(cart_item).data
            }, status=status.HTTP_201_CREATED)
            
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

class CartItemListView(generics.ListAPIView):
    """List items in user's cart"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get list of items in user's cart",
        responses={
            200: CartItemSerializer(many=True),
            401: "Authentication required"
        },
        tags=['Shopping Cart']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related('product', 'product__category')

class CartItemDetailView(generics.RetrieveAPIView):
    """Get cart item details"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get cart item details",
        responses={
            200: CartItemSerializer,
            401: "Authentication required",
            404: "Cart item not found"
        },
        tags=['Shopping Cart']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related('product')

    def get_object(self):
        item_id = self.kwargs['item_id']
        return self.get_queryset().get(id=item_id)

class UpdateCartItemView(APIView):
    """Update cart item quantity"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update cart item quantity",
        request_body=UpdateCartItemSerializer,
        responses={
            200: openapi.Response(
                description="Cart item updated successfully",
                examples={
                    "application/json": {
                        "message": "Cart item updated successfully",
                        "cart_item": {
                            "id": 1,
                            "quantity": 3,
                            "subtotal": "34500.00"
                        }
                    }
                }
            ),
            400: "Validation errors",
            401: "Authentication required",
            404: "Cart item not found"
        },
        tags=['Shopping Cart']
    )
    def put(self, request, item_id):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            
            serializer = UpdateCartItemSerializer(
                data=request.data,
                context={'cart_item': cart_item}
            )
            serializer.is_valid(raise_exception=True)
            
            quantity = serializer.validated_data['quantity']
            
            if quantity == 0:
                cart_item.delete()
                return Response({
                    'message': 'Item removed from cart'
                }, status=status.HTTP_204_NO_CONTENT)
            else:
                cart_item.quantity = quantity
                cart_item.save()
                
                return Response({
                    'message': 'Cart item updated successfully',
                    'cart_item': CartItemSerializer(cart_item).data
                })
                
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)

class RemoveCartItemView(APIView):
    """Remove item from cart"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Remove item from cart",
        responses={
            204: "Item removed successfully",
            401: "Authentication required",
            404: "Cart item not found"
        },
        tags=['Shopping Cart']
    )
    def delete(self, request, item_id):
        try:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            
            return Response({
                'message': 'Item removed from cart successfully'
            }, status=status.HTTP_204_NO_CONTENT)
            
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)

class ClearCartView(APIView):
    """Clear all items from cart"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Clear all items from cart",
        responses={
            200: openapi.Response(
                description="Cart cleared successfully",
                examples={
                    "application/json": {
                        "message": "Cart cleared successfully"
                    }
                }
            ),
            401: "Authentication required"
        },
        tags=['Shopping Cart']
    )
    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        
        return Response({
            'message': 'Cart cleared successfully'
        })

# =============================================================================
# STATISTICS & ANALYTICS VIEWS
# =============================================================================

class ProductStatsView(APIView):
    """Get product statistics"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get product statistics",
        responses={
            200: openapi.Response(
                description="Product statistics",
                examples={
                    "application/json": {
                        "total_products": 150,
                        "active_products": 140,
                        "featured_products": 25,
                        "out_of_stock": 10,
                        "categories_count": 8,
                        "average_price": "5500.00"
                    }
                }
            )
        },
        tags=['Statistics']
    )
    def get(self, request):
        stats = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'featured_products': Product.objects.filter(is_featured=True, is_active=True).count(),
            'out_of_stock': Product.objects.filter(stock_quantity=0, is_active=True).count(),
            'categories_count': Category.objects.filter(is_active=True).count(),
            'average_price': Product.objects.filter(is_active=True).aggregate(Avg('price'))['price__avg'] or 0,
        }
        
        return Response(stats)

class CategoryStatsView(APIView):
    """Get category statistics"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get statistics for a specific category",
        responses={
            200: openapi.Response(
                description="Category statistics",
                examples={
                    "application/json": {
                        "category_name": "Smartphones",
                        "total_products": 25,
                        "active_products": 22,
                        "featured_products": 5,
                        "average_price": "8500.00"
                    }
                }
            ),
            404: "Category not found"
        },
        tags=['Statistics']
    )
    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id, is_active=True)
            products = Product.objects.filter(category=category)
            
            stats = {
                'category_name': category.name,
                'total_products': products.count(),
                'active_products': products.filter(is_active=True).count(),
                'featured_products': products.filter(is_featured=True, is_active=True).count(),
                'average_price': products.filter(is_active=True).aggregate(Avg('price'))['price__avg'] or 0,
            }
            
            return Response(stats)
            
        except Category.DoesNotExist:
            return Response({
                'error': 'Category not found'
            }, status=status.HTTP_404_NOT_FOUND)

# =============================================================================
# FUTURE FEATURES (PLACEHOLDER VIEWS)
# =============================================================================

class WishlistView(APIView):
    """User wishlist (Future feature)"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user wishlist (Coming soon)",
        responses={200: "Wishlist feature coming soon"},
        tags=['Future Features']
    )
    def get(self, request):
        return Response({
            'message': 'Wishlist feature coming soon',
            'user': request.user.email
        })

class AddToWishlistView(APIView):
    """Add to wishlist (Future feature)"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add product to wishlist (Coming soon)",
        responses={200: "Wishlist feature coming soon"},
        tags=['Future Features']
    )
    def post(self, request):
        return Response({
            'message': 'Add to wishlist feature coming soon'
        })

class CompareProductsView(APIView):
    """Compare products (Future feature)"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Compare multiple products (Coming soon)",
        responses={200: "Product comparison feature coming soon"},
        tags=['Future Features']
    )
    def get(self, request):
        return Response({
            'message': 'Product comparison feature coming soon'
        })