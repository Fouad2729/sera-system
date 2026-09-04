from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/violations/', views.api_violations, name='violations_api'),
    path('api/violations/create/', views.api_violation_create, name='api_violation_create'),
    path('api/violations/<int:pk>/', views.api_violation_update, name='api_violation_update'),
]
