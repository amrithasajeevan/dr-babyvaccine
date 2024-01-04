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





# class ChildSerializer(serializers.ModelSerializer):
#     parent_username = serializers.CharField(write_only=True, source='parent')

#     class Meta:
#         model = Child
#         fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'sex', 'parent_username']

#     def create(self, validated_data):
#         parent_username = validated_data.pop('parent')
#         parent_user = User.objects.get(username=parent_username)

#         child = Child.objects.create(
#             parent=parent_user,
#             **validated_data
#         )
#         return child
    

# class ChildSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=Child
#         fields="__all__"
class ChildSerializer(serializers.ModelSerializer):
    parent_username = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Child
        fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'sex', 'parent_username']

    def create(self, validated_data):
        parent_username = validated_data.pop('parent_username', None)

        try:
            parent_user = User.objects.get(username=parent_username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Parent user does not exist")

        validated_data['parent'] = parent_user
        child = Child.objects.create(**validated_data)
        return child

class VaxNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaxName
        fields = '__all__'


class VaxCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vax_Cycle
        fields = '__all__'

class VaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vax
        fields = '__all__'


