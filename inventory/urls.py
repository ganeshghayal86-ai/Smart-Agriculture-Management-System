
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('add-inventory/', views.add_inventory, name='add_inventory'),
    path('edit-inventory/<int:id>/', views.edit_inventory, name='edit_inventory'),
    path('delete-inventory/<int:id>/', views.delete_inventory, name='delete_inventory'),
    path('add-usage/', views.add_inventory_usage, name='add_inventory_usage'),
    path('usage-history/', views.usage_history, name='usage_history'),
    path('reports/', views.inventory_reports, name='inventory_reports'),
    path('download-pdf/', views.download_inventory_pdf, name='download_inventory_pdf'),
]
