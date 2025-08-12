"""
URL configuration for companyapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home, name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import (
    home, get_organizations, get_companies, get_employees, filter_employees,
    register, login, token_refresh, profile, register_form, login_form, test_token, dashboard,
    # New CRUD endpoints
    organization_list_create, organization_detail,
    company_list_create, company_detail,
    employee_list_create, employee_detail,
    # New utility endpoints
    organization_stats, search_all
)

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    
    # General API overview
    path('api/', home, name='api_overview'),
    
    # Web forms for easy access
    path('auth/register-form/', register_form, name='register_form'),
    path('auth/login-form/', login_form, name='login_form'),
    path('test-token/', test_token, name='test_token'),
    path('dashboard/', dashboard, name='dashboard'),
    
    # Authentication endpoints
    path('api/auth/register/', register, name='register'),
    path('api/auth/login/', login, name='login'),
    path('api/auth/refresh/', token_refresh, name='token_refresh'),
    path('api/auth/profile/', profile, name='profile'),
    
    # Enhanced CRUD endpoints for Organizations
    path('api/organizations/', organization_list_create, name='organization_list_create'),
    path('api/organizations/<int:pk>/', organization_detail, name='organization_detail'),
    
    # Enhanced CRUD endpoints for Companies
    path('api/companies/', company_list_create, name='company_list_create'),
    path('api/companies/<int:pk>/', company_detail, name='company_detail'),
    
    # Enhanced CRUD endpoints for Employees
    path('api/employees/', employee_list_create, name='employee_list_create'),
    path('api/employees/<int:pk>/', employee_detail, name='employee_detail'),
    
    # Utility endpoints
    path('api/stats/', organization_stats, name='organization_stats'),
    path('api/search/', search_all, name='search_all'),
    
    # Legacy endpoints for backward compatibility
    path('api/organizations/legacy/', get_organizations, name='get_organizations'),
    path('api/companies/legacy/', get_companies, name='get_companies'),
    path('api/employees/legacy/', get_employees, name='get_employees'),
    path('api/employees/filter/', filter_employees, name='filter_employees'),
]
