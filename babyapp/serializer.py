from django.contrib.auth.models import User

from .models import *
from  rest_framework import serializers

from rest_framework import serializers
import re 

#serializer for registration
class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=12, write_only=True)
    phone_output = serializers.SerializerMethodField(read_only=True)  # New read-only field for output

    class Meta:
        model = User
        fields = ['id','username', 'email', 'first_name', 'last_name', 'phone', 'phone_output', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        email_regex = r'^[a-z]+[0-9]*[*_]?[a-z0-9]*@gmail.com'  # Example regex for email validation

        if not re.match(email_regex, value):
            raise serializers.ValidationError("Invalid email format")

        return value

    def validate_phone(self, value):
        phone_regex = r'^[9876][0-9]{9}$'  # Example regex for phone number validation

        if not re.match(phone_regex, value):
            raise serializers.ValidationError("Invalid phone number format")

        return value

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)  # Retrieve phone from validated data

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])

        if phone is not None:
            user.phone = phone 

        user.save()
        return user

    def get_phone_output(self, obj):
        return obj.phone if hasattr(obj, 'phone') else None
       

#
class loginserializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField(max_length=30)





class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'

class VaxProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaxProgram
        fields = '__all__'

class VaxCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaxCycle
        fields = '__all__'

class VaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vax
        fields = '__all__'

class VaxProgramNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaxProgramName
        fields = '__all__'

class VaxCycleNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaxCycleName
        fields = '__all__'

class VaxNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaxName
        fields = '__all__'