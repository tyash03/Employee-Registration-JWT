from django.db import models

# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, related_name='companies', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    company = models.ForeignKey(Company, related_name='employees', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.position})"
