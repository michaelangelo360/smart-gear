# products/serializers.py
from rest_framework import serializers
from decimal import Decimal
from .models import Category, Product, Cart, CartItem

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'is_active', 
            'products_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_products_count(self, obj):
        """Get count of active products in this category"""
        return obj.products.filter(is_active=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Simplified serializer for product listing"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    price_formatted = serializers.SerializerMethodField()
    effective_price_formatted = serializers.SerializerMethodField()
    discount_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'category_name', 'price', 
            'discount_price', 'effective_price', 'price_formatted',
            'effective_price_formatted', 'discount_percentage',
            'stock_quantity', 'sku', 'is_active', 'is_featured', 
            'is_in_stock', 'created_at'
        ]

    def get_price_formatted(self, obj):
        """Format price for display"""
        return f"GHS {obj.price:,.2f}"

    def get_effective_price_formatted(self, obj):
        """Format effective price for display"""
        return f"GHS {obj.effective_price:,.2f}"


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual product"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    effective_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    price_formatted = serializers.SerializerMethodField()
    effective_price_formatted = serializers.SerializerMethodField()
    discount_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    is_in_stock = serializers.BooleanField(read_only=True)
    savings_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'category_details', 'price', 'discount_price', 'effective_price',
            'price_formatted', 'effective_price_formatted', 'savings_amount',
            'discount_percentage', 'stock_quantity', 'sku', 'weight',
            'dimensions', 'is_active', 'is_featured', 'is_in_stock',
            'created_at', 'updated_at'
        ]

    def get_price_formatted(self, obj):
        """Format price for display"""
        return f"GHS {obj.price:,.2f}"

    def get_effective_price_formatted(self, obj):
        """Format effective price for display"""
        return f"GHS {obj.effective_price:,.2f}"

    def get_savings_amount(self, obj):
        """Calculate savings amount if there's a discount"""
        if obj.discount_price and obj.discount_price < obj.price:
            savings = obj.price - obj.discount_price
            return f"GHS {savings:,.2f}"
        return None


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price', 'discount_price',
            'stock_quantity', 'sku', 'weight', 'dimensions', 
            'is_active', 'is_featured'
        ]

    def validate_price(self, value):
        """Validate price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_discount_price(self, value):
        """Validate discount price"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Discount price must be greater than 0")
        return value

    def validate_sku(self, value):
        """Validate SKU is unique"""
        instance = getattr(self, 'instance', None)
        if Product.objects.filter(sku=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Product with this SKU already exists")
        return value.upper()

    def validate(self, attrs):
        """Cross-field validation"""
        price = attrs.get('price')
        discount_price = attrs.get('discount_price')
        
        if discount_price and price and discount_price >= price:
            raise serializers.ValidationError({
                'discount_price': 'Discount price must be less than regular price'
            })
        
        return attrs


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    subtotal_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 'subtotal',
            'subtotal_formatted', 'created_at', 'updated_at'
        ]

    def get_subtotal_formatted(self, obj):
        """Format subtotal for display"""
        return f"GHS {obj.subtotal:,.2f}"

    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            product = Product.objects.get(id=value, is_active=True)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")

    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value

    def validate(self, attrs):
        """Validate stock availability"""
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')
        
        if product_id and quantity:
            try:
                product = Product.objects.get(id=product_id)
                if quantity > product.stock_quantity:
                    raise serializers.ValidationError({
                        'quantity': f'Only {product.stock_quantity} units available'
                    })
            except Product.DoesNotExist:
                pass  # This will be caught by product_id validation
        
        return attrs

    def create(self, validated_data):
        """Create or update cart item"""
        cart = self.context['cart']
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': validated_data['quantity']}
        )
        
        if not created:
            # Update existing item quantity
            cart_item.quantity += validated_data['quantity']
            cart_item.save()
        
        return cart_item


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_amount_formatted = serializers.SerializerMethodField()
    total_items = serializers.IntegerField(read_only=True)
    total_unique_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'total_amount', 'total_amount_formatted',
            'total_items', 'total_unique_items', 'created_at', 'updated_at'
        ]

    def get_total_amount_formatted(self, obj):
        """Format total amount for display"""
        return f"GHS {obj.total_amount:,.2f}"


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            product = Product.objects.get(id=value, is_active=True)
            if not product.is_in_stock:
                raise serializers.ValidationError("Product is out of stock")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

    def validate(self, attrs):
        """Validate stock availability"""
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity')
        
        if product_id and quantity:
            product = Product.objects.get(id=product_id)
            if quantity > product.stock_quantity:
                raise serializers.ValidationError({
                    'quantity': f'Only {product.stock_quantity} units available'
                })
        
        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=0)
    
    def validate_quantity(self, value):
        """Validate quantity against stock"""
        cart_item = self.context.get('cart_item')
        if cart_item and value > 0:
            if value > cart_item.product.stock_quantity:
                raise serializers.ValidationError(
                    f'Only {cart_item.product.stock_quantity} units available'
                )
        return value


class ProductSearchSerializer(serializers.Serializer):
    """Serializer for product search parameters"""
    search = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    is_featured = serializers.BooleanField(required=False)
    in_stock_only = serializers.BooleanField(required=False,)