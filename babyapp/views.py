from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import *
from rest_framework.response import Response
from rest_framework import generics
from django.db import transaction

from rest_framework import status

from rest_framework.authentication import BasicAuthentication,TokenAuthentication

from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse

from django.core.mail import send_mail
from babyvaccinepro.settings import EMAIL_HOST_USER

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import os




#register parent
class Registeruser(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create a token for the registered user
            token, created = Token.objects.get_or_create(user=user)
            
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
            return Response({'data': serializer.data, 'token': token.key}, status=status.HTTP_201_CREATED)
        
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


class VaxNameListCreateView(generics.ListCreateAPIView):
    queryset = VaxName.objects.all()
    serializer_class = VaxNameSerializer

class VaxNameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaxName.objects.all()
    serializer_class = VaxNameSerializer







    
from .tasks import *
from django_celery_beat.models import PeriodicTask,CrontabSchedule
import json


#celery function to send mail

def send_mail_to_parent(request):
    send_mail_based_on_dates.delay() 
    return JsonResponse({"message": "Email sending initiated."}, status=200)

# class SendMailToParentView(APIView):
#     def post(self, request):
#         send_mail_based_on_dates.delay()
#         return Response({"message": "Email sending initiated."}, status=status.HTTP_200_OK)


# class SendMailToParentView(APIView):
#     def get(self, request):
#         send_mail_based_on_dates.delay()
#         return Response({"message": "Email sending initiated."}, status=status.HTTP_200_OK)









class VaxCycleAPIView(generics.ListCreateAPIView):
   queryset = Vax_Cycle.objects.all()
   serializer_class = VaxCycleSerializer
    

class VaxCycleDelete_Update(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vax_Cycle.objects.all()
    serializer_class = VaxCycleSerializer
    
class VaxAPIView(generics.ListCreateAPIView):
   queryset=Vax.objects.all()
   serializer_class=VaxSerializer
    
class VaxDelete_Update(generics.RetrieveUpdateDestroyAPIView):
   queryset=Vax.objects.all()
   serializer_class=VaxSerializer





#vaccine dates
    

def vaccination_dates_view(request, child_id):
    child = get_object_or_404(Child, pk=child_id)
    vaccination_dates = child.get_vaccination_dates()

    # Example: Convert vaccination dates to strings for JSON response
    vaccination_dates_str = [str(date) for date in vaccination_dates]

    return JsonResponse({'vaccination_dates': vaccination_dates_str})
    



class ChatbotAPI(APIView):
    def __init__(self):
        super().__init__()
        # Read PDF and initialize necessary components
        os.environ["OPENAI_API_KEY"] = "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"
        pdfreader = PdfReader(r"C:\Users\User\Dr-baby\dr-babyvaccine\Dr.baby.pdf")
        raw_text = ''
        for page in pdfreader.pages:
            content = page.extract_text()
            if content:
                raw_text += content

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=800,
            chunk_overlap=200,
            length_function=len,
        )
        texts = text_splitter.split_text(raw_text)

        embeddings = OpenAIEmbeddings()
        self.document_search = FAISS.from_texts(texts, embeddings)

        self.chain = load_qa_chain(OpenAI(), chain_type="stuff")

    def post(self, request):
        user_input = request.data.get('user_input')

        if user_input.lower() == 'exit':
            return Response({"response": "Goodbye!"}, status=status.HTTP_200_OK)

        # Your existing response logic
        bot_response = self.get_response(user_input)
        return Response({"response": bot_response}, status=status.HTTP_200_OK)

    def get_response(self, user_input):
        if user_input.lower() in ["hi", "hello", "hey", "hy", "hai"]:
            return "Hello, welcome to Dr Baby. How can I assist you today!"
        elif user_input.lower() in ["bye", "by", "thank you", "thanks"]:
            return "bye"
        else:
            docs = self.document_search.similarity_search(user_input)
            return self.chain.run(input_documents=docs, question=user_input)
        

#vaccine names
        
class VaccineListView(APIView):
    def post(self,request):
        a=VaccineNameSerializer(data=request.data)
        if a.is_valid():
            a.save()
        return Response(a.data)
    def get(self,request):
        qs=vaccine_names.objects.all()
        a=VaccineNameSerializer(qs,many=True)
        return Response(a.data)
    


class VaccineProgramsListCreateView(generics.ListCreateAPIView):
    queryset = VaccinePrograms.objects.all()
    serializer_class = VaccineProgramSerializer

class VaccineProgramsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaccinePrograms.objects.all()
    serializer_class = VaccineProgramSerializer



class HospitalsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Filter hospitals with available slots
        hospitals = Hospitals.objects.filter(slots_available__gt=0)
        serializer = HospitalsSerializer(hospitals, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = HospitalsSerializer(data=request.data)

        if serializer.is_valid():
            # Save Hospitals instance
            hospital_instance = serializer.save()

            # If vaccine_names data is present, add it to the hospital_instance
            vaccine_names_data = request.data.get('programs_available', [])
            if vaccine_names_data:
                # Create a new VaccinePrograms instance
                programs_instance = VaccinePrograms.objects.create()

                # Add vaccine_names to the programs_instance
                for vaccine_id in vaccine_names_data:
                    # Retrieve vaccine_names instance using the provided ID
                    try:
                        vaccine_name_instance = vaccine_names.objects.get(id=vaccine_id)
                        programs_instance.vaccines.add(vaccine_name_instance)
                    except vaccine_names.DoesNotExist:
                        return Response(
                            {"error": f"Vaccine with ID {vaccine_id} does not exist."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Save the VaccinePrograms instance to get an ID
                programs_instance.save()

                # Add the VaccinePrograms instance to hospital_instance
                hospital_instance.programs_available.add(programs_instance)

                # Get the vaccine names in the response
                vaccine_names_response = [vaccine.vaccine for vaccine in programs_instance.vaccines.all()]
                serializer.data['vaccine_names'] = vaccine_names_response

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    

class VaccineBookingList(APIView):
    def get(self, request):
        bookings = VaccineBooking.objects.all()
        serializer = VaccineBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VaccineBookingSerializer(data=request.data)

        if serializer.is_valid():
            hospital_id = request.data.get('hospital')
            program_id = request.data.get('vaccine_program')

            try:
                hospital = Hospitals.objects.get(pk=hospital_id)
                program = VaccinePrograms.objects.get(pk=program_id)
            except (Hospitals.DoesNotExist, VaccinePrograms.DoesNotExist):
                return Response({'message': 'Hospital or vaccine program not found'}, status=status.HTTP_404_NOT_FOUND)

            if hospital.slots_available > 0 and program in hospital.programs_available.all():
                with transaction.atomic():
                    hospital.slots_available -= 1
                    hospital.save()

                    serializer.validated_data['hospital'] = hospital
                    serializer.validated_data['vaccine_program'] = program
                    vaccine_booking = serializer.save()

                    send_booking_confirmation_mail(vaccine_booking.parent_email, vaccine_booking.hospital.name, vaccine_booking.vaccine_program.id)

                return Response({'message': 'Booking successful'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Invalid booking request'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_booking_confirmation_mail(parent_email, hospital_name, vaccine_program_id):
    vaccine_program = VaccinePrograms.objects.get(pk=vaccine_program_id)

    subject = 'Vaccine Booking Confirmation'
    message = f'Thank you for booking the vaccine program at {hospital_name}!\n'
    message += 'Vaccines included:\n'
    for vaccine in vaccine_program.vaccines.all():
        message += f'- {vaccine}\n'

    from_email = 'amrithababy142@gmail.com'  # Replace with your email
    recipient_list = [parent_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    return Response({'message': 'Booking successful'}, status=status.HTTP_201_CREATED)




from django.http import Http404

class VaccineProgramsAPI(APIView):
    def get_object(self, pk):
        try:
            return VaccinePrograms.objects.get(pk=pk)
        except VaccinePrograms.DoesNotExist:
            raise Http404

    def get(self, request, pk=None, format=None):
        if pk:
            # Get a specific vaccine program and its status
            vaccine_program = self.get_object(pk)
            statuses = VaccineStatus.objects.filter(program=vaccine_program)
            
            data = []

            for status in statuses:
                serializer_status = VaccineStatusSerializer(status)
                program_data = {
                    'program': VaccineProgramSerializer(vaccine_program).data,
                    'statuses': [
                        {
                            'status': {
                                'id': status.id,
                                'program': status.program.id,
                                'child_name': status.child_name.first_name,
                                'is_taken': status.is_taken
                            }
                        }
                    ]
                }
                data.append(program_data)

            if not data:
                return Response({'is_taken': False})
                
            return Response(data)
        else:
            # Get status for all vaccine programs
            vaccine_programs = VaccinePrograms.objects.all()
            data = []

            for program in vaccine_programs:
                statuses = VaccineStatus.objects.filter(program=program)
                program_data = {
                    'program': VaccineProgramSerializer(program).data,
                    'statuses': []
                }

                for status in statuses:
                    status_data = {
                        'status': {
                            'id': status.id,
                            'program': status.program.id,
                            'child_name': status.child_name.first_name,
                            'is_taken': status.is_taken
                        }
                    }
                    program_data['statuses'].append(status_data)

                data.append(program_data)

            return Response(data)

    def post(self, request, pk=None, format=None):
        if pk:
            # Update the status of a specific vaccine program
            vaccine_program = self.get_object(pk)
            child_name = request.data.get('child_name')  # Retrieve the child name from the request data

            try:
                child = Child.objects.get(first_name=child_name)  # Retrieve the Child instance using the name
            except Child.DoesNotExist:
                return Response({'error': f'Child with name {child_name} not found'}, status=status.HTTP_404_NOT_FOUND)

            status, created = VaccineStatus.objects.get_or_create(program=vaccine_program, child_name=child)
            
            # Use 'is_taken' as the field name, and ensure it's a boolean
            is_taken = request.data.get('is_taken', False)
            is_taken = is_taken.lower() == 'true'  # Convert to boolean if needed
            
            status.is_taken = is_taken
            status.save()

            # Check if the vaccine is taken and return the appropriate status
            result_status = 'Taken' if status.is_taken else 'Pending'

            return Response({'status': result_status})
        else:
            # Create a new vaccine status with child details
            pass