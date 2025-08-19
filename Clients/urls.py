from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('clients/', views.add_client, name='clients'),
    path('clients/get/<int:client_id>/', views.get_client, name='get_client'),
    path('clients/delete/<int:client_id>/', views.delete_client, name='delete_client'),
    path('clients/export/', views.export_clients_excel, name='export_clients_excel'),
]
