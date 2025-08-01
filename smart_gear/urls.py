from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import TemplateView

# Optional: API Documentation (uncomment when you install drf-yasg)
# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# schema_view = get_schema_view(
#     openapi.Info(
#         title="SmartGear API",
#         default_version='v1',
#         description="API for SmartGear - Tech Gadgets & Accessories Store (Ghana)",
#         terms_of_service="https://www.smartgear.com/terms/",
#         contact=openapi.Contact(email="api@smartgear.com"),
#         license=openapi.License(name="MIT License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'Welcome to SmartGear API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'auth': '/api/v1/auth/',
                'products': '/api/v1/products/',
                'payments': '/api/v1/payments/',
            },
            'docs': {
                'swagger': '/swagger/',
                'redoc': '/redoc/',
            }
        },
        'status': 'active'
    })

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API root
    path('api/', api_root, name='api-root'),
    
    # API v1 endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/payments/', include('payments.urls')),
    
    # API Documentation (uncomment when drf-yasg is installed)
    # path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Home page (optional)
    path('', api_root, name='home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

