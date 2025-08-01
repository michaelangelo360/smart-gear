# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:category_id>/products/', views.CategoryProductsView.as_view(), name='category-products'),
    
    # Products
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured-products'),
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
    path('sku/<str:sku>/', views.ProductBySkuView.as_view(), name='product-by-sku'),
    
    # Cart Management
    path('cart/', views.CartView.as_view(), name='cart-detail'),
    path('cart/add/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('cart/items/', views.CartItemListView.as_view(), name='cart-items'),
    path('cart/items/<int:item_id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path('cart/items/<int:item_id>/update/', views.UpdateCartItemView.as_view(), name='update-cart-item'),
    path('cart/items/<int:item_id>/remove/', views.RemoveCartItemView.as_view(), name='remove-cart-item'),
    path('cart/clear/', views.ClearCartView.as_view(), name='clear-cart'),
    
    # Product Management (Admin)
    path('admin/products/', views.ProductCreateView.as_view(), name='product-create'),
    path('admin/products/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('admin/categories/', views.CategoryCreateView.as_view(), name='category-create'),
    
    # Statistics and Analytics
    path('stats/', views.ProductStatsView.as_view(), name='product-stats'),
    path('categories/<int:category_id>/stats/', views.CategoryStatsView.as_view(), name='category-stats'),
    
    # Wishlist (Future feature)
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', views.AddToWishlistView.as_view(), name='add-to-wishlist'),
    
    # Product Comparison (Future feature)
    path('compare/', views.CompareProductsView.as_view(), name='compare-products'),
    
    # API Overview
    path('overview/', views.products_overview, name='products-overview'),
]