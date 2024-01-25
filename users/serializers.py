# serializers.py
from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'role','phone_number', 'address','password')
        
        extra_kwargs = {
                        "email": {"required": True, "unique": True},

                    "password": {"write_only": True,"required": False},
                    }
        
    def validate_email(self, value):
            existing_users = User.objects.filter(email=value)
            if self.instance:  
                existing_users = existing_users.exclude(pk=self.instance.pk)

            if existing_users.exists():
                raise serializers.ValidationError("This email address is already in use.")
            
            return value
    
    def create(self, validated_data):
      
        validated_data['password'] = make_password(validated_data['password'])

        return super().create(validated_data)


    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.role = validated_data.get('role', instance.role)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        if password is not None:
            instance.set_password(password)
            instance.save()

        return instance
    


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # email = serializers.EmailField()
    # password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        return data