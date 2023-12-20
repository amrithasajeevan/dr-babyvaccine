from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import *
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.authentication import BasicAuthentication,TokenAuthentication
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse

from django.core.mail import send_mail
from babyvaccinepro.settings import EMAIL_HOST_USER




#register parent
class Registeruser(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Get the email of the registered user
            user_email = user.email
            
            # Your email sending logic using the user's email
            subject = 'Welcome to Dr.baby'
            message = f'Congratulations,\n' \
                       f'You have successfully registered with our website.\n' \
                       f'username: {user.email}\n' \
                       f'WELCOME'

            send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email], fail_silently=False)

            # Assuming token creation or any other response data you want to send back
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#user login 
    
class LoginView(APIView):
    serializer_class = loginserializer 

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            user = User.objects.get(email=email)

            if user is not None and check_password(password, user.password):
                login(request,user)
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class logoutview(APIView):
    def post(self,request):
        logout(request)
        return Response({'msg':'logout successfully'})


#child details get and post
class ChildListCreateView(generics.ListCreateAPIView):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer

#child details delete and update
    
class ChildDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer

class VaxProgramNameListCreateView(generics.ListCreateAPIView):
    queryset = VaxProgramName.objects.all()
    serializer_class = VaxProgramNameSerializer

class VaxProgramNameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaxProgramName.objects.all()
    serializer_class = VaxProgramNameSerializer

class VaxCycleNameListCreateView(generics.ListCreateAPIView):
    queryset = VaxCycleName.objects.all()
    serializer_class = VaxCycleNameSerializer

class VaxCycleNameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaxCycleName.objects.all()
    serializer_class = VaxCycleNameSerializer

class VaxNameListCreateView(generics.ListCreateAPIView):
    queryset = VaxName.objects.all()
    serializer_class = VaxNameSerializer

class VaxNameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaxName.objects.all()
    serializer_class = VaxNameSerializer

class VaxProgramListCreateView(generics.ListCreateAPIView):
    queryset = VaxProgram.objects.all()
    serializer_class = VaxProgramSerializer

class VaxProgramDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaxProgram.objects.all()
    serializer_class = VaxProgramSerializer

class VaxCycleListCreateView(generics.ListCreateAPIView):
    queryset = VaxCycle.objects.all()
    serializer_class = VaxCycleSerializer

class VaxCycleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaxCycle.objects.all()
    serializer_class = VaxCycleSerializer

class VaxListCreateView(generics.ListCreateAPIView):
    queryset = Vax.objects.all()
    serializer_class = VaxSerializer

class VaxDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vax.objects.all()
    serializer_class = VaxSerializer




    
from .tasks import *
from django_celery_beat.models import PeriodicTask,CrontabSchedule
import json


#celery function to

def send_mail_to_parent(request):
    send_mail_based_on_dates.delay() 
    return HttpResponse("done")


