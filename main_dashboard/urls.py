from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/violations/', views.api_violations, name='violations_api'),
    path('api/violations/create/', views.api_violation_create, name='api_violation_create'),
    path('api/violations/<int:pk>/', views.api_violation_update, name='api_violation_update'),
    path('api/violations/<int:pk>/delete/', views.api_violation_delete, name='api_violation_delete'),
    path('api/violations/export-excel/', views.api_export_excel, name='api_export_excel'),
    path('api/violations/sync-check/', views.api_sync_check, name='api_sync_check'),
]
