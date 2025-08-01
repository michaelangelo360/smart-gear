# accounts/views.py
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    ChangePasswordSerializer,
    UserListSerializer
)

User = get_user_model()

# API Overview
@swagger_auto_schema(
    method='get',
    operation_description="Get authentication API overview",
    responses={200: "Authentication endpoints overview"},
    tags=['Authentication Overview']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def auth_overview(request):
    """Authentication API overview"""
    return Response({
        'message': 'SmartGear Authentication API',
        'version': '1.0',
        'endpoints': {
            'register': '/api/v1/auth/register/',
            'login': '/api/v1/auth/login/', 
            'profile': '/api/v1/auth/profile/',
            'change_password': '/api/v1/auth/change-password/',
            'token': '/api/v1/auth/token/',
            'token_refresh': '/api/v1/auth/token/refresh/',
            'current_user': '/api/v1/auth/me/',
        },
        'features': [
            'JWT Authentication',
            'User Registration',
            'Profile Management',
            'Password Change',
            'Email Verification',
            'Ghana Phone Number Support'
        ]
    })

class RegisterView(generics.CreateAPIView):
    """Register a new user account"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "johndoe",
                            "first_name": "John",
                            "last_name": "Doe"
                        },
                        "access": "jwt_access_token",
                        "refresh": "jwt_refresh_token",
                        "message": "User registered successfully"
                    }
                }
            ),
            400: "Validation errors"
        },
        tags=['Authentication']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    """Login user and get JWT tokens"""
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Login with email and password",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "johndoe"
                        },
                        "access": "jwt_access_token",
                        "refresh": "jwt_refresh_token",
                        "message": "Login successful"
                    }
                }
            ),
            400: "Invalid credentials"
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current user profile",
        responses={
            200: UserProfileSerializer,
            401: "Authentication required"
        },
        tags=['User Profile']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update current user profile",
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Validation errors",
            401: "Authentication required"
        },
        tags=['User Profile']
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update current user profile",
        request_body=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Validation errors",
            401: "Authentication required"
        },
        tags=['User Profile']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class CurrentUserView(generics.RetrieveAPIView):
    """Get current authenticated user"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get current authenticated user details",
        responses={
            200: UserProfileSerializer,
            401: "Authentication required"
        },
        tags=['User Profile']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):
    """Change user password"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                examples={
                    "application/json": {
                        "message": "Password changed successfully"
                    }
                }
            ),
            400: "Validation errors",
            401: "Authentication required"
        },
        tags=['User Profile']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        })

class UserListView(generics.ListAPIView):
    """List all users (admin only)"""
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get list of all users (admin only)",
        responses={
            200: UserListSerializer(many=True),
            401: "Authentication required",
            403: "Admin access required"
        },
        tags=['User Management']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class DeactivateAccountView(generics.GenericAPIView):
    """Deactivate user account"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Deactivate current user account",
        responses={
            200: openapi.Response(
                description="Account deactivated successfully",
                examples={
                    "application/json": {
                        "message": "Account deactivated successfully"
                    }
                }
            ),
            401: "Authentication required"
        },
        tags=['User Profile']
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()
        
        return Response({
            'message': 'Account deactivated successfully'
        })

class VerifyEmailView(generics.GenericAPIView):
    """Verify user email (placeholder)"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Verify user email address",
        responses={
            200: openapi.Response(
                description="Email verification status",
                examples={
                    "application/json": {
                        "message": "Email verification feature coming soon",
                        "email": "user@example.com",
                        "is_verified": False
                    }
                }
            ),
            401: "Authentication required"
        },
        tags=['User Profile']
    )
    def post(self, request, *args, **kwargs):
        return Response({
            'message': 'Email verification feature coming soon',
            'email': request.user.email,
            'is_verified': request.user.is_verified
        })