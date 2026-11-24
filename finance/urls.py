
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.finance_dashboard, name='finance_dashboard'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('edit-transaction/<int:id>/', views.edit_transaction, name='edit_transaction'),
    path('delete-transaction/<int:id>/', views.delete_transaction, name='delete_transaction'),
]
