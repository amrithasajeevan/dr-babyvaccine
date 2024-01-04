from django.urls import path
from .views import *

urlpatterns=[
    path('authtoken/',Registeruser.as_view()),
    path('authlogin/',LoginView.as_view(),name='logins'),
    path('logoutt/',logoutview.as_view),

    path('childcreate/', ChildListCreateView.as_view(), name='child-list'),
    path('children/<int:pk>/', ChildDetailView.as_view(), name='child-detail'),

    

    path('vax-names/', VaxNameListCreateView.as_view(), name='vax-name-list'),
    path('vax-names/<int:pk>/', VaxNameDetailView.as_view(), name='vax-name-detail'),

    # path('vax-programscreate/', VaxProgramView.as_view(), name='vax-program-list'),
    # path('vax-programs-modify/<int:pk>/', VaxProgramDelete_Update.as_view(), name='vax-program-detail'),

    path('vax-cycles/', VaxCycleAPIView.as_view(), name='vax-cycle-list'),
    path('vax-cycles/<int:pk>/', VaxCycleDelete_Update.as_view(), name='vax-cycle-detail'),

    path('vaxes/', VaxAPIView.as_view(), name='vax-list'),
    path('vaxes/<int:pk>/', VaxDelete_Update.as_view(), name='vax-detail'),


     path('childcreate/<int:child_id>/vaccination-dates/',vaccination_dates_view, name='vaccination_dates'),
    #  path('vaccination/<int:child_id>/', VaccinationProgramView.as_view(), name='vaccination_programs'),
    
    # path('vaccination-dates/<int:child_id>/', VaccinationDatesAPIView.as_view(), name='vaccination-dates'),
   
   

    
    path('send_mail_date/',send_mail_to_parent),
    #  path('send-mail/', SendMailToParentView.as_view(), name='send-mail'),
    

    #chat
    # path('chat/', ChatbotAPI.as_view(), name='chat'),
    path('chatbot/', ChatbotAPI.as_view(), name='chatbot_api'),




]