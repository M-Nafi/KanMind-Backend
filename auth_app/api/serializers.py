from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from auth_app.models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'fullname': {'required': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        if not validated_data.get('email'):
            raise serializers.ValidationError({'email': 'Email is required'})
        if not validated_data.get('fullname'):
            raise serializers.ValidationError({'fullname': 'Fullname is required'})
        validated_data.setdefault('username', validated_data['email'])
        return super().create(validated_data)
    
    
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']