from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from .models import History
from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    name = serializers.CharField(style={'input_type': 'first_name'}, write_only=True) 
    
    
    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'password2']
        extra_kwargs = {
            'password' : {'write_only': True}
        }
        
    
    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        
        if not re.search(r'[a-zA-Z]', password):
            raise serializers.ValidationError('Password must contain at least one alphabet.')
        
        if not re.search(r'\d', password):
            raise serializers.ValidationError('Password must contain at least one digit.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError('Password must contain at least one special character.')
        
        return password
    
    
  
    def create(self, validated_data):
        email = validated_data['email']
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError({'error': 'User with this email already exists.'})

        password = validated_data.pop('password')
        password2 = validated_data.pop('password2')

        if password != password2:
            raise serializers.ValidationError({'error': 'Passwords do not match.'})

        user = User.objects.create(
            email=email,
            username=email,  
            first_name=validated_data['name']
        )
        user.set_password(password)
        user.save()
        return user
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def authenticate_user(self, email, password):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
            else:
                raise serializers.ValidationError('Incorrect password.')
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')


    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = self.authenticate_user(email, password)

        if user:
            data['user'] = user
        else:
            raise serializers.ValidationError('Invalid email or password')

        return data
    

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'