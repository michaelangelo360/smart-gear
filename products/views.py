from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, Product, Cart, CartItem
from .serializers import (
    CategorySerializer, ProductSerializer, 
    CartSerializer, CartItemSerializer
)

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = []

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = []

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = cart
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            cart_item = serializer.save()
            return Response({
                'message': 'Item added to cart successfully',
                'cart_item': CartItemSerializer(cart_item).data
            }, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        cart_item.delete()
        
        return Response({
            'message': 'Item removed from cart successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({
            'error': 'Cart item not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        
        quantity = request.data.get('quantity', 1)
        if quantity <= 0:
            cart_item.delete()
            return Response({
                'message': 'Item removed from cart'
            }, status=status.HTTP_204_NO_CONTENT)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return Response({
            'message': 'Cart item updated successfully',
            'cart_item': CartItemSerializer(cart_item).data
        })
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({
            'error': 'Cart item not found'
        }, status=status.HTTP_404_NOT_FOUND)
