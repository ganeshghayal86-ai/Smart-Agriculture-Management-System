
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-crop/', views.add_crop, name='add_crop'),
    path('view-crops/', views.view_crops, name='view_crops'),
    path('edit-crop/<int:id>/', views.edit_crop, name='edit_crop'),
    path('delete-crop/<int:id>/', views.delete_crop, name='delete_crop'),

    path('crop-recommendation/', views.crop_recommendation, name='crop_recommendation'),
    path('weather/', views.weather_information, name='weather'),
    path('disease-detection/', views.disease_detection, name='disease_detection'),
    path('disease-history/', views.disease_history, name='disease_history'),
    path('delete-disease-history/<int:id>/', views.delete_disease_history, name='delete_disease_history'),

    # Irrigation Management
    path('irrigation/', views.irrigation_dashboard, name='irrigation_dashboard'),
    path('add-irrigation/', views.add_irrigation, name='add_irrigation'),
    path('irrigation-history/', views.irrigation_history, name='irrigation_history'),
    path('edit-irrigation/<int:id>/', views.edit_irrigation, name='edit_irrigation'),
    path('delete-irrigation/<int:id>/', views.delete_irrigation, name='delete_irrigation'),

    # Soil Health Management
    path('soil-health/', views.soil_dashboard, name='soil_dashboard'),
    path('add-soil-test/', views.add_soil_test, name='add_soil_test'),
    path('soil-test-reports/', views.soil_test_list, name='soil_test_list'),
    path(
    'soil-test-detail/<int:test_id>/',
    views.soil_test_detail,
    name='soil_test_detail'
),
    path(
    'edit-soil-test/<int:test_id>/',
    views.edit_soil_test,
    name='edit_soil_test'
),
    path(
    'delete-soil-test/<int:test_id>/',
    views.delete_soil_test,
    name='delete_soil_test'
),
    path(
    'download-soil-test-pdf/<int:test_id>/',
    views.download_soil_test_pdf,
    name='download_soil_test_pdf'
),
]
