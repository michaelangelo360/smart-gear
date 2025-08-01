from django.urls import path
from django.views.generic import TemplateView
from django.http import JsonResponse

# Temporary views (replace with actual views when you create them)
def auth_list_view(request):
    return JsonResponse({
        'endpoints': {
            'register': '/api/v1/auth/register/',
            'login': '/api/v1/auth/login/',
            'profile': '/api/v1/auth/profile/',
            'token': '/api/v1/auth/token/',
            'token_refresh': '/api/v1/auth/token/refresh/',
        }
    })

def register_view(request):
    return JsonResponse({'message': 'Register endpoint - Coming soon'})

def login_view(request):
    return JsonResponse({'message': 'Login endpoint - Coming soon'})

def profile_view(request):
    return JsonResponse({'message': 'Profile endpoint - Coming soon'})

def token_view(request):
    return JsonResponse({'message': 'Token endpoint - Coming soon'})

def token_refresh_view(request):
    return JsonResponse({'message': 'Token refresh endpoint - Coming soon'})

app_name = 'accounts'

urlpatterns = [
    path('', auth_list_view, name='auth-list'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', profile_view, name='profile'),
    
    # JWT Token endpoints (for future use)
    path('token/', token_view, name='token_obtain_pair'),
    path('token/refresh/', token_refresh_view, name='token_refresh'),
]
