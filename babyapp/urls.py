from django.urls import path
from .views import *

urlpatterns=[
    path('authtoken/',Registeruser.as_view()),
    path('authlogin/',LoginView.as_view(),name='logins'),
    path('logoutt/',logoutview.as_view),

    path('children/', ChildListCreateView.as_view(), name='child-list'),
    path('children/<int:pk>/', ChildDetailView.as_view(), name='child-detail'),

    path('vax-program-names/', VaxProgramNameListCreateView.as_view(), name='vax-program-name-list'),
    path('vax-program-names/<int:pk>/', VaxProgramNameDetailView.as_view(), name='vax-program-name-detail'),

    path('vax-cycle-names/', VaxCycleNameListCreateView.as_view(), name='vax-cycle-name-list'),
    path('vax-cycle-names/<int:pk>/', VaxCycleNameDetailView.as_view(), name='vax-cycle-name-detail'),

    path('vax-names/', VaxNameListCreateView.as_view(), name='vax-name-list'),
    path('vax-names/<int:pk>/', VaxNameDetailView.as_view(), name='vax-name-detail'),

    path('vax-programs/', VaxProgramListCreateView.as_view(), name='vax-program-list'),
    path('vax-programs/<int:pk>/', VaxProgramDetailView.as_view(), name='vax-program-detail'),

    path('vax-cycles/', VaxCycleListCreateView.as_view(), name='vax-cycle-list'),
    path('vax-cycles/<int:pk>/', VaxCycleDetailView.as_view(), name='vax-cycle-detail'),

    path('vaxes/', VaxListCreateView.as_view(), name='vax-list'),
    path('vaxes/<int:pk>/', VaxDetailView.as_view(), name='vax-detail'),

    
    path('send_mail_date/',send_mail_to_parent),
    




]