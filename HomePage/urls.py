from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('services/', views.services_page, name='services'),
    path('about-us/', views.about_us_page, name='about_us'),
    path('submit-enquiry/', views.submit_enquiry_ajax, name='submit_enquiry_ajax'),
    path('check-certificate/', views.check_certificate, name='check_certificate'),
    path('enquiries/', views.enquiry_management, name='enquiries'),
    path('enquiries/update-status/<int:enquiry_id>/', views.update_enquiry_status, name='update_enquiry_status'),
    path('enquiries/add-response/<int:enquiry_id>/', views.add_enquiry_response, name='add_enquiry_response'),
]
