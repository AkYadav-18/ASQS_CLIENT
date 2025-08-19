from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('standards/', views.add_standards, name='standards'),
    path('standards/get/<int:standard_id>/', views.get_standard, name='get_standard'),
    path('standards/delete/<int:standard_id>/', views.delete_standard, name='delete_standard'),
]
