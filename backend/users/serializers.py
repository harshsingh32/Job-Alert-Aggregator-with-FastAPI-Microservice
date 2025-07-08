from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, JobPreference

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password_confirm']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')

        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_email_verified', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_email_verified']

class JobPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPreference
        fields = [
            'id', 'keywords', 'location_type', 'desired_location', 
            'experience_level', 'min_salary', 'max_salary', 'job_type',
            'is_active', 'email_notifications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_keywords(self, value):
        if not value.strip():
            raise serializers.ValidationError("Keywords cannot be empty.")
        return value

    def validate(self, attrs):
        min_salary = attrs.get('min_salary')
        max_salary = attrs.get('max_salary')
        
        if min_salary and max_salary and min_salary > max_salary:
            raise serializers.ValidationError("Minimum salary cannot be greater than maximum salary.")
        
        return attrs