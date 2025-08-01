# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 
            'phone_number', 'password', 'password_confirm'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'phone_number': {'required': False},
        }

    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_username(self, value):
        """Validate username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_phone_number(self, value):
        """Validate Ghana phone number format"""
        if not value:
            return value
        
        # Remove spaces and special characters
        phone = ''.join(filter(str.isdigit, value))
        
        # Check if it's a valid Ghana number
        if phone.startswith('0') and len(phone) == 10:
            # Convert local format to international
            return f"+233{phone[1:]}"
        elif phone.startswith('233') and len(phone) == 12:
            return f"+{phone}"
        elif value.startswith('+233') and len(value) == 13:
            return value
        else:
            raise serializers.ValidationError(
                "Please enter a valid Ghana phone number (e.g., +233240123456 or 0240123456)"
            )

    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Password confirmation doesn't match."
            })
        return attrs

    def create(self, validated_data):
        """Create user with validated data"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate login credentials"""
        email = attrs.get('email', '').lower()
        password = attrs.get('password')

        if email and password:
            # Try to authenticate with email
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                # Check if user exists
                if User.objects.filter(email=email).exists():
                    raise serializers.ValidationError(
                        'Invalid password. Please check your password and try again.'
                    )
                else:
                    raise serializers.ValidationError(
                        'No account found with this email address.'
                    )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Your account has been disabled. Please contact support.'
                )
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError(
                'Please provide both email and password.'
            )
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'phone_number', 'date_of_birth', 'is_verified',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'email', 'username', 'is_verified', 'created_at', 'updated_at')

    def validate_phone_number(self, value):
        """Validate Ghana phone number format"""
        if not value:
            return value
        
        # Remove spaces and special characters
        phone = ''.join(filter(str.isdigit, value))
        
        # Check if it's a valid Ghana number
        if phone.startswith('0') and len(phone) == 10:
            return f"+233{phone[1:]}"
        elif phone.startswith('233') and len(phone) == 12:
            return f"+{phone}"
        elif value.startswith('+233') and len(value) == 13:
            return value
        else:
            raise serializers.ValidationError(
                "Please enter a valid Ghana phone number"
            )


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        """Validate new password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New password confirmation doesn't match."
            })
        return attrs


class UserListSerializer(serializers.ModelSerializer):
    """Simplified serializer for user listing (admin use)"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'full_name', 
            'is_verified', 'is_active', 'created_at'
        )