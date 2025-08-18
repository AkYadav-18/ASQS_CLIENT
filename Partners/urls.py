from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('partners/', views.add_partner, name='partners'),
    path('partners/get/<int:partner_id>/', views.get_partner, name='get_partner'),
    path('partners/delete/<int:partner_id>/', views.delete_partner, name='delete_partner'),
    path('partners/export/', views.export_partners_excel, name='export_partners_excel'),
]
