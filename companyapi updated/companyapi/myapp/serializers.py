from rest_framework import serializers
from .models import Organization, Company, Employee


class EmployeeSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    organization_name = serializers.CharField(source='company.organization.name', read_only=True)
    company_id = serializers.IntegerField(source='company.id', read_only=True)
    organization_id = serializers.IntegerField(source='company.organization.id', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'position', 'company', 'company_name', 'organization_name', 'company_id', 'organization_id']
        extra_kwargs = {
            'name': {'required': True, 'max_length': 100},
            'position': {'required': False, 'max_length': 100},
            'company': {'required': True}
        }

    def validate_name(self, value):
        """Validate employee name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Employee name must be at least 2 characters long")
        return value.strip()

    def validate_position(self, value):
        """Validate employee position"""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError("Position must be at least 2 characters long")
        return value.strip() if value else value


class CompanySerializer(serializers.ModelSerializer):
    employees = EmployeeSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'organization', 'organization_name', 'employees', 'employee_count']
        extra_kwargs = {
            'name': {'required': True, 'max_length': 100},
            'organization': {'required': True}
        }

    def get_employee_count(self, obj):
        """Get the count of employees for this company"""
        return obj.employees.count()

    def validate_name(self, value):
        """Validate company name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Company name must be at least 2 characters long")
        return value.strip()


class OrganizationSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True, read_only=True)
    company_count = serializers.SerializerMethodField()
    total_employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['id', 'name', 'companies', 'company_count', 'total_employee_count']
        extra_kwargs = {
            'name': {'required': True, 'max_length': 100}
        }

    def get_company_count(self, obj):
        """Get the count of companies for this organization"""
        return obj.companies.count()

    def get_total_employee_count(self, obj):
        """Get the total count of employees across all companies in this organization"""
        return sum(company.employees.count() for company in obj.companies.all())

    def validate_name(self, value):
        """Validate organization name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Organization name must be at least 2 characters long")
        return value.strip()


# Additional serializers for specific use cases
class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating employees with minimal required fields"""
    class Meta:
        model = Employee
        fields = ['name', 'position', 'company']
        extra_kwargs = {
            'name': {'required': True},
            'company': {'required': True}
        }


class CompanyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating companies with minimal required fields"""
    class Meta:
        model = Company
        fields = ['name', 'organization']
        extra_kwargs = {
            'name': {'required': True},
            'organization': {'required': True}
        }


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating organizations with minimal required fields"""
    class Meta:
        model = Organization
        fields = ['name']
        extra_kwargs = {
            'name': {'required': True}
        }
