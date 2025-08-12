from django.contrib import admin
from .models import Organization, Company, Employee

# Register your models here.
admin.site.register(Organization)
admin.site.register(Company)
admin.site.register(Employee)
