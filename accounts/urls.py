# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Additional user endpoints
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    
    # Account management
    path('deactivate/', views.DeactivateAccountView.as_view(), name='deactivate-account'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify-email'),
    
    # API overview
    path('', views.auth_overview, name='auth-overview'),
]