from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from auth_app.models import User


class RegisterSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'fullname': {'required': True},
        }

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
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']