from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import *
from rest_framework.response import Response
from rest_framework import generics

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
    

# class VaccinationDatesAPIView(APIView):
#     def get(self, request, child_id):
#         child = get_object_or_404(Child, pk=child_id)
#         vaccination_dates = child.get_vaccination_dates()

#         # Example: Convert vaccination dates to strings for JSON response
#         vaccination_dates_str = [str(date) for date in vaccination_dates]

#         return Response({'vaccination_dates': vaccination_dates_str}, status=status.HTTP_200_OK)

#chatbot

# from babyvaccinepro.chat import get_response  # Import necessary functions or classes from chat.py

# class ChatbotAPI(APIView):
#     def post(self, request):
#         user_input = request.data.get('user_input')  # Assuming input JSON contains 'user_input'
#         if user_input.lower() == 'exit':
#             return Response({"response": "Goodbye!"})

#         bot_response = get_response(user_input)  # Use the function from chat.py
#         return Response({"response": bot_response})
    
class ChatbotAPI(APIView):
    def post(self, request):
        user_input = request.data.get('user_input')

        if user_input.lower() == 'exit':
            return Response({"response": "Goodbye!"}, status=status.HTTP_200_OK)

        # Your existing initialization and setup code here
        os.environ["OPENAI_API_KEY"] = "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"
        pdfreader = PdfReader(r"C:\Users\User\babycalender\babyvaccinepro\Dr.baby.pdf")
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
        document_search = FAISS.from_texts(texts, embeddings)

        chain = load_qa_chain(OpenAI(), chain_type="stuff")

        chatbot = ChatBot("DoctorBaby")
        trainer = ListTrainer(chatbot)
        trainer.train("chatterbot.corpus.english")

        # Your existing response logic
        def get_response(user_input):
            if user_input.lower() in ["hi", "hello", "hey", "hy", "hai"]:
                return "Hello, welcome to Dr Baby. How can I assist you today!"
            elif user_input.lower() in ["bye", "by", "thank you", "thanks"]:
                return "bye"
            else:
                docs = document_search.similarity_search(user_input)
                return chain.run(input_documents=docs, question=user_input)

        bot_response = get_response(user_input)
        return Response({"response": bot_response}, status=status.HTTP_200_OK)