from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from auth_app.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    - Includes a repeated_password field to ensure password confirmation.
    - Validates that 'password' and 'repeated_password' match.
    - Ensures email uniqueness (raises error if already registered).
    - Hashes the password before saving the user.
    - Sets the 'username' field to the provided email if not explicitly given.
    - Returns the created User instance.
    """
    repeated_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'fullname': {'required': True},
        }

    def validate_email(self, value):
        """
        Validates an email address to ensure it is not already registered.

        - Raises a ValidationError with a message "Email is already registered" if the email address is already in use.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        validated_data['password'] = make_password(validated_data['password'])
        validated_data.setdefault('username', validated_data['email'])
        return super().create(validated_data)
    
    
class MemberSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for user membership representation.

    - Exposes only basic user information: id, fullname, and email.
    - Intended for contexts where sensitive fields (like password) should not be included.
    """
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']