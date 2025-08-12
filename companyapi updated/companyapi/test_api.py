#!/usr/bin/env python3
"""
Test script for the Company API with JWT authentication
Run this script to test all the new CRUD operations and endpoints
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(endpoint, method, status, data=None):
    """Print API call result"""
    status_icon = "✅" if status < 400 else "❌"
    print(f"{status_icon} {method} {endpoint} - Status: {status}")
    if data and status < 400:
        print(f"   Response: {json.dumps(data, indent=2)}")
    elif data and status >= 400:
        print(f"   Error: {json.dumps(data, indent=2)}")

def test_authentication():
    """Test authentication endpoints"""
    print_section("Testing Authentication Endpoints")
    
    # Test registration
    print("\n1. Testing User Registration...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register/", json=register_data)
        data = response.json()
        print_result("/api/auth/register/", "POST", response.status_code, data)
        
        if response.status_code == 201:
            print("   ✅ Registration successful! You can now use this account.")
        elif response.status_code == 400 and "already exists" in str(data):
            print("   ℹ️  User already exists, continuing with login...")
        else:
            print("   ❌ Registration failed")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return None
    
    # Test login
    print("\n2. Testing User Login...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
        data = response.json()
        print_result("/api/auth/login/", "POST", response.status_code, data)
        
        if response.status_code == 200:
            access_token = data['tokens']['access']
            print(f"   ✅ Login successful! Access token: {access_token[:20]}...")
            return access_token
        else:
            print("   ❌ Login failed")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        return None

def test_protected_endpoints(token):
    """Test protected endpoints with JWT token"""
    print_section("Testing Protected Endpoints")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test profile endpoint
    print("\n1. Testing Profile Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/auth/profile/", headers=headers)
        data = response.json()
        print_result("/api/auth/profile/", "GET", response.status_code, data)
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test statistics endpoint
    print("\n2. Testing Statistics Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/stats/", headers=headers)
        data = response.json()
        print_result("/api/stats/", "GET", response.status_code, data)
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")

def test_crud_operations(token):
    """Test CRUD operations for all entities"""
    print_section("Testing CRUD Operations")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test Organization CRUD
    print("\n1. Testing Organization CRUD...")
    
    # Create organization
    org_data = {"name": "Test Organization"}
    try:
        response = requests.post(f"{API_BASE}/organizations/", json=org_data, headers=headers)
        data = response.json()
        print_result("/api/organizations/", "POST", response.status_code, data)
        
        if response.status_code == 201:
            org_id = data['id']
            print(f"   ✅ Organization created with ID: {org_id}")
            
            # Read organization
            response = requests.get(f"{API_BASE}/organizations/{org_id}/", headers=headers)
            data = response.json()
            print_result(f"/api/organizations/{org_id}/", "GET", response.status_code, data)
            
            # Update organization
            update_data = {"name": "Updated Test Organization"}
            response = requests.put(f"{API_BASE}/organizations/{org_id}/", json=update_data, headers=headers)
            data = response.json()
            print_result(f"/api/organizations/{org_id}/", "PUT", response.status_code, data)
            
        else:
            org_id = None
            print("   ❌ Failed to create organization")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        org_id = None
    
    # Test Company CRUD
    print("\n2. Testing Company CRUD...")
    
    if org_id:
        company_data = {"name": "Test Company", "organization": org_id}
        try:
            response = requests.post(f"{API_BASE}/companies/", json=company_data, headers=headers)
            data = response.json()
            print_result("/api/companies/", "POST", response.status_code, data)
            
            if response.status_code == 201:
                company_id = data['id']
                print(f"   ✅ Company created with ID: {company_id}")
                
                # Read company
                response = requests.get(f"{API_BASE}/companies/{company_id}/", headers=headers)
                data = response.json()
                print_result(f"/api/companies/{company_id}/", "GET", response.status_code, data)
                
                # Update company
                update_data = {"name": "Updated Test Company", "organization": org_id}
                response = requests.put(f"{API_BASE}/companies/{company_id}/", json=update_data, headers=headers)
                data = response.json()
                print_result(f"/api/companies/{company_id}/", "PUT", response.status_code, data)
                
            else:
                company_id = None
                print("   ❌ Failed to create company")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
            company_id = None
    else:
        company_id = None
        print("   ⏭️  Skipping company tests (no organization created)")
    
    # Test Employee CRUD
    print("\n3. Testing Employee CRUD...")
    
    if company_id:
        employee_data = {"name": "Test Employee", "position": "Developer", "company": company_id}
        try:
            response = requests.post(f"{API_BASE}/employees/", json=employee_data, headers=headers)
            data = response.json()
            print_result("/api/employees/", "POST", response.status_code, data)
            
            if response.status_code == 201:
                employee_id = data['id']
                print(f"   ✅ Employee created with ID: {employee_id}")
                
                # Read employee
                response = requests.get(f"{API_BASE}/employees/{employee_id}/", headers=headers)
                data = response.json()
                print_result(f"/api/employees/{employee_id}/", "GET", response.status_code, data)
                
                # Update employee
                update_data = {"name": "Updated Test Employee", "position": "Senior Developer", "company": company_id}
                response = requests.put(f"{API_BASE}/employees/{employee_id}/", json=update_data, headers=headers)
                data = response.json()
                print_result(f"/api/employees/{employee_id}/", "PUT", response.status_code, data)
                
            else:
                employee_id = None
                print("   ❌ Failed to create employee")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
            employee_id = None
    else:
        print("   ⏭️  Skipping employee tests (no company created)")

def test_utility_endpoints(token):
    """Test utility endpoints"""
    print_section("Testing Utility Endpoints")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test search endpoint
    print("\n1. Testing Search Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/search/?q=Test", headers=headers)
        data = response.json()
        print_result("/api/search/?q=Test", "GET", response.status_code, data)
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test list endpoints
    print("\n2. Testing List Endpoints...")
    
    endpoints = [
        "/api/organizations/",
        "/api/companies/",
        "/api/employees/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
            data = response.json()
            print_result(endpoint, "GET", response.status_code, data)
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error for {endpoint}: {e}")

def main():
    """Main test function"""
    print("🚀 Company API Test Suite")
    print("This script will test all the new CRUD operations and endpoints")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server responded with unexpected status")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure Django is running on http://127.0.0.1:8000")
        print("   Run: python manage.py runserver")
        return
    
    # Run tests
    token = test_authentication()
    if not token:
        print("\n❌ Authentication failed. Cannot continue with protected endpoint tests.")
        return
    
    test_protected_endpoints(token)
    test_crud_operations(token)
    test_utility_endpoints(token)
    
    print_section("Test Summary")
    print("✅ All tests completed!")
    print("\n🎯 Next steps:")
    print("1. Visit http://127.0.0.1:8000/dashboard/ for the enhanced dashboard")
    print("2. Use the dashboard to create, read, update, and delete data")
    print("3. Test the search functionality")
    print("4. Explore the API documentation at http://127.0.0.1:8000/api/")

if __name__ == "__main__":
    main()
