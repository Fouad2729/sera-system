from django.contrib import admin
from django.urls import path
from main_dashboard.views import home, add_violation, edit_violation, geocode_search, api_violations, api_violation_create, api_violation_update, api_violations
from accounts.views import request_reset, confirm_reset

urlpatterns = [
    path("", home, name="home"),
    path("add/", add_violation, name="add_violation"),
    path("edit/<int:pk>/", edit_violation, name="edit_violation"),
    path("api/geocode/", geocode_search, name="geocode_search"),
    path("api/violations/", api_violations, name="api_violations"),
    path("api/violations/create/", api_violation_create, name="api_violation_create"),
    path("api/violations/<int:pk>/", api_violation_update, name="api_violation_update"),

    path("api/auth/request-reset", request_reset, name="request_reset"),
    path("api/auth/confirm-reset", confirm_reset, name="confirm_reset"),

    path("admin/", admin.site.urls),
]
