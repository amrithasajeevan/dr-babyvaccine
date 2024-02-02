from django.contrib.auth.models import User

from .models import *
from  rest_framework import serializers

from rest_framework import serializers
import re 
from rest_framework import status

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
        fields = ['id', 'first_name', 'last_name', 'date_of_birth', 'sex', 'parent_username','Location']

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


class VaccineNameSerializer(serializers.ModelSerializer):
    class Meta:
        model= vaccine_names
        fields='__all__'


class VaccineProgramSerializer(serializers.ModelSerializer):
    vaccines = VaccineNameSerializer(many=True, read_only=True)
    class Meta:
        model=VaccinePrograms
        fields=['id','vaccines']

class HospitalsSerializer(serializers.ModelSerializer):
    programs_available = serializers.PrimaryKeyRelatedField(
        queryset=VaccinePrograms.objects.all(),
        many=True,
        required=False
    )
    programs_details = serializers.SerializerMethodField()

    class Meta:
        model = Hospitals
        fields = ('id', 'name', 'location', 'slots_available', 'programs_available', 'programs_details')

    def get_programs_details(self, obj):
        programs_available = obj.programs_available.all()
        return [{'vaccines': [vaccine.vaccine for vaccine in program.vaccines.all()]} for program in programs_available]

    def create(self, validated_data):
        programs_data = validated_data.pop('programs_available', [])
        hospital = Hospitals.objects.create(**validated_data)

        for program_instance in programs_data:
            hospital.programs_available.add(program_instance)

        return hospital



class VaccineBookingSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(write_only=True)
    parent_email = serializers.EmailField(write_only=True)
    booking_date = serializers.DateTimeField(read_only=True)
    parent_id = serializers.IntegerField(read_only=True, source='parent_name.id')
    hospital_name = serializers.CharField(read_only=True, source='hospital.name')  # Assuming 'name' is the field on Hospitals model

    class Meta:
        model = VaccineBooking
        fields = ['id', 'parent_name', 'parent_email', 'hospital_name', 'vaccine_program', 'booking_date', 'parent_id']

    def create(self, validated_data):
        parent_name = validated_data.pop('parent_name')
        parent_email = validated_data.pop('parent_email')

        # Find the user by username or any other criteria
        user = User.objects.get(username=parent_name)

        # Retrieve the VaccinePrograms instance based on the provided ID
        program_id = validated_data.get('vaccine_program').id  # Extract ID from VaccinePrograms object

        try:
            vaccine_program = VaccinePrograms.objects.get(pk=program_id)
        except VaccinePrograms.DoesNotExist:
            raise serializers.ValidationError({'message': 'Vaccine program not found'}, code='program_not_found')

        # Create the VaccineBooking instance with the found user and program
        vaccine_booking = VaccineBooking.objects.create(
            parent_name=user,
            parent_email=parent_email,
            hospital=validated_data['hospital'],
            vaccine_program=vaccine_program  # Use the retrieved instance
        )

        return vaccine_booking


# class VaccineStatusSerializer(serializers.ModelSerializer):
#     program = VaccineProgramSerializer()

#     class Meta:
#         model = VaccineStatus
#         fields = ['id', 'program', 'is_taken']
    

class VaccineStatusSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source='child_name.first_name', read_only=True)
    class Meta:
        model = VaccineStatus
        fields = ['id', 'program', 'child_name', 'is_taken']

    