from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Organization, Company, Employee
from .serializers import OrganizationSerializer, CompanySerializer, EmployeeSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({
            'error': 'Username already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'User registered successfully',
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    """Refresh access token using refresh token"""
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'error': 'Refresh token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        
        return Response({
            'access': access_token
        })
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get user profile (protected endpoint)"""
    return Response({
        'username': request.user.username,
        'email': request.user.email,
        'id': request.user.id
    })


# Organization CRUD operations
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def organization_list_create(request):
    """List all organizations or create a new one"""
    if request.method == 'GET':
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def organization_detail(request, pk):
    """Retrieve, update or delete an organization"""
    try:
        organization = get_object_or_404(Organization, pk=pk)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = OrganizationSerializer(organization)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = OrganizationSerializer(organization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        organization.delete()
        return Response({'message': 'Organization deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# Company CRUD operations
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def company_list_create(request):
    """List all companies or create a new one"""
    if request.method == 'GET':
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def company_detail(request, pk):
    """Retrieve, update or delete a company"""
    try:
        company = get_object_or_404(Company, pk=pk)
    except Company.DoesNotExist:
        return Response({'error': 'Company not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = CompanySerializer(company)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CompanySerializer(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        company.delete()
        return Response({'message': 'Company deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# Employee CRUD operations
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def employee_list_create(request):
    """List all employees or create a new one"""
    if request.method == 'GET':
        name = request.GET.get('name')
        company = request.GET.get('company')
        organization = request.GET.get('organization')

        filters = {}
        if name:
            filters['name__icontains'] = name
        if company:
            filters['company_id'] = company
        if organization:
            filters['company__organization_id'] = organization

        if filters:
            employees = Employee.objects.filter(**filters)
        else:
            employees = Employee.objects.all()
        
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def employee_detail(request, pk):
    """Retrieve, update or delete an employee"""
    try:
        employee = get_object_or_404(Employee, pk=pk)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = EmployeeSerializer(employee, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        employee.delete()
        return Response({'message': 'Employee deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# Legacy endpoints for backward compatibility
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organizations(request):
    organizations = Organization.objects.all()
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_companies(request):
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employees(request):
    name = request.GET.get('name')
    company = request.GET.get('company')
    organization = request.GET.get('organization')

    filters = {}
    if name:
        filters['name__icontains'] = name
    if company:
        filters['company_id'] = company
    if organization:
        filters['company__organization_id'] = organization

    if filters:
        employees = Employee.objects.filter(**filters)
    else:
        employees = Employee.objects.all()
    
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_employees(request):
    name = request.GET.get('name')
    company = request.GET.get('company')
    organization = request.GET.get('organization')

    filters = {}
    if name:
        filters['name__icontains'] = name
    if company:
        filters['company_id'] = company
    if organization:
        filters['company__organization_id'] = organization

    employees = Employee.objects.all()  # Start with all employees
    if filters:
        employees = employees.filter(**filters)  # Apply filters only if they exist

    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)


# New utility endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_stats(request):
    """Get statistics about organizations"""
    total_organizations = Organization.objects.count()
    total_companies = Company.objects.count()
    total_employees = Employee.objects.count()
    
    # Get organizations with company and employee counts
    org_stats = []
    for org in Organization.objects.all():
        company_count = org.companies.count()
        employee_count = sum(company.employees.count() for company in org.companies.all())
        org_stats.append({
            'id': org.id,
            'name': org.name,
            'company_count': company_count,
            'employee_count': employee_count
        })
    
    return Response({
        'total_organizations': total_organizations,
        'total_companies': total_companies,
        'total_employees': total_employees,
        'organization_details': org_stats
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_all(request):
    """Search across all entities"""
    query = request.GET.get('q', '')
    if not query:
        return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    results = {
        'organizations': [],
        'companies': [],
        'employees': []
    }
    
    # Search organizations
    orgs = Organization.objects.filter(name__icontains=query)
    results['organizations'] = OrganizationSerializer(orgs, many=True).data
    
    # Search companies
    companies = Company.objects.filter(name__icontains=query)
    results['companies'] = CompanySerializer(companies, many=True).data
    
    # Search employees
    employees = Employee.objects.filter(name__icontains=query)
    results['employees'] = EmployeeSerializer(employees, many=True).data
    
    return Response(results)


def home(request):
    return HttpResponse("""
        <h1>Welcome to the Company API!</h1>
        <p>This is a Django REST API with JWT authentication.</p>
        
        <h2>Available Endpoints:</h2>
        
        <h3>Authentication (No token required):</h3>
        <ul>
            <li><strong>POST /api/auth/register/</strong> - User registration</li>
            <li><strong>POST /api/auth/login/</strong> - User login</li>
            <li><strong>POST /api/auth/refresh/</strong> - Refresh access token</li>
        </ul>
        
        <h3>Protected API Endpoints (Token required):</h3>
        
        <h4>Organizations:</h4>
        <ul>
            <li><strong>GET /api/organizations/</strong> - List all organizations</li>
            <li><strong>POST /api/organizations/</strong> - Create new organization</li>
            <li><strong>GET /api/organizations/{id}/</strong> - Get organization details</li>
            <li><strong>PUT /api/organizations/{id}/</strong> - Update organization</li>
            <li><strong>DELETE /api/organizations/{id}/</strong> - Delete organization</li>
        </ul>
        
        <h4>Companies:</h4>
        <ul>
            <li><strong>GET /api/companies/</strong> - List all companies</li>
            <li><strong>POST /api/companies/</strong> - Create new company</li>
            <li><strong>GET /api/companies/{id}/</strong> - Get company details</li>
            <li><strong>PUT /api/companies/{id}/</strong> - Update company</li>
            <li><strong>DELETE /api/companies/{id}/</strong> - Delete company</li>
        </ul>
        
        <h4>Employees:</h4>
        <ul>
            <li><strong>GET /api/employees/</strong> - List all employees</li>
            <li><strong>POST /api/employees/</strong> - Create new employee</li>
            <li><strong>GET /api/employees/{id}/</strong> - Get employee details</li>
            <li><strong>PUT /api/employees/{id}/</strong> - Update employee</li>
            <li><strong>DELETE /api/employees/{id}/</strong> - Delete employee</li>
        </ul>
        
        <h4>Utility Endpoints:</h4>
        <ul>
            <li><strong>GET /api/stats/</strong> - Get organization statistics</li>
            <li><strong>GET /api/search/?q={query}</strong> - Search across all entities</li>
        </ul>
        
        <h3>How to Use:</h3>
        <ol>
            <li>Register or login to get a JWT token</li>
            <li>Include the token in Authorization header: <code>Bearer &lt;your_token&gt;</code></li>
            <li>Access protected endpoints</li>
        </ol>
        
        <p><em>Note: All API endpoints except authentication require a valid JWT token.</em></p>
        
        <h2>Quick Access:</h2>
        <p><a href="/auth/register-form/">📝 Register New User</a></p>
        <p><a href="/auth/login-form/">🔐 Login</a></p>
        <p><a href="/test-token/">🧪 Test Your Token</a></p>
        <p><a href="/dashboard/">📊 View Data Dashboard</a></p>
    """)


@csrf_exempt
def register_form(request):
    """Simple HTML form for user registration"""
    if request.method == 'POST':
        # Handle form submission
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if username and password:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                refresh = RefreshToken.for_user(user)
                
                return HttpResponse(f"""
                    <h1>✅ Registration Successful!</h1>
                    <p>User <strong>{username}</strong> has been created successfully.</p>
                    
                    <h3>Your JWT Tokens:</h3>
                    <p><strong>Access Token:</strong> <code>{refresh.access_token}</code></p>
                    <p><strong>Refresh Token:</strong> <code>{refresh}</code></p>
                    
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Copy your access token</li>
                        <li>Use it in the Authorization header: <code>Bearer {refresh.access_token}</code></li>
                        <li>Test protected endpoints</li>
                    </ol>
                    
                    <p><a href="/api/">← Back to API Documentation</a></p>
                    <p><a href="/auth/login-form/">🔐 Login</a></p>
                """)
            except Exception as e:
                return HttpResponse(f"""
                    <h1>❌ Registration Failed</h1>
                    <p>Error: {str(e)}</p>
                    <p><a href="/auth/register-form/">← Try Again</a></p>
                """)
    
    return HttpResponse(f"""
        <h1>📝 User Registration</h1>
        <form method="POST">
            <p><label>Username: <input type="text" name="username" required></label></p>
            <p><label>Email: <input type="email" name="email"></label></p>
            <p><label>Password: <input type="password" name="password" required></label></p>
            <p><button type="submit">Register</button></p>
        </form>
        <p><a href="/api/">← Back to API Documentation</a></p>
    """)


@csrf_exempt
def login_form(request):
    """Simple HTML form for user login"""
    if request.method == 'POST':
        # Handle form submission
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                
                return HttpResponse(f"""
                    <h1>✅ Login Successful!</h1>
                    <p>Welcome back, <strong>{username}</strong>!</p>
                    
                    <h3>Your JWT Tokens:</h3>
                    <p><strong>Access Token:</strong> <code>{refresh.access_token}</code></p>
                    <p><strong>Refresh Token:</strong> <code>{refresh}</code></p>
                    
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Copy your access token</li>
                        <li>Use it in the Authorization header: <code>Bearer {refresh.access_token}</code></li>
                        <li>Test protected endpoints</li>
                    </ol>
                    
                    <p><a href="/api/">← Back to API Documentation</a></p>
                    <p><a href="/auth/register-form/">📝 Register New User</a></p>
                    <p><a href="/test-token/">🧪 Test Your Token</a></p>
                """)
            else:
                return HttpResponse(f"""
                    <h1>❌ Login Failed</h1>
                    <p>Invalid username or password.</p>
                    <p><a href="/auth/login-form/">← Try Again</a></p>
                """)
    
    return HttpResponse(f"""
        <h1>🔐 User Login</h1>
        <form method="POST">
            <p><label>Username: <input type="text" name="username" required></label></p>
            <p><label>Password: <input type="password" name="password" required></label></p>
            <p><button type="submit">Login</button></p>
        </form>
        <p><a href="/api/">← Back to API Documentation</a></p>
        <p><a href="/auth/register-form/">📝 Register New User</a></p>
    """)


@csrf_exempt
def test_token(request):
    """Test page for JWT token"""
    return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>JWT Token Tester</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                input[type="text"] {{ width: 100%; padding: 10px; margin: 10px 0; }}
                button {{ padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }}
                button:hover {{ background: #0056b3; }}
                .result {{ margin: 20px 0; padding: 15px; border-radius: 5px; }}
                .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
                .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
                .endpoint {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧪 JWT Token Tester</h1>
                <p>Paste your JWT access token below and test protected endpoints:</p>
                
                <input type="text" id="token" placeholder="Paste your JWT access token here..." style="font-family: monospace;">
                
                <h3>Test Endpoints:</h3>
                
                <div class="endpoint">
                    <button onclick="testEndpoint('/api/auth/profile/')">👤 Test Profile</button>
                    <span>Get your user profile information</span>
                </div>
                
                <div class="endpoint">
                    <button onclick="testEndpoint('/api/organizations/')">🏢 Test Organizations</button>
                    <span>Get list of organizations</span>
                </div>
                
                <div class="endpoint">
                    <button onclick="testEndpoint('/api/companies/')">🏭 Test Companies</button>
                    <span>Get list of companies</span>
                </div>
                
                <div class="endpoint">
                    <button onclick="testEndpoint('/api/employees/')">👥 Test Employees</button>
                    <span>Get list of employees</span>
                </div>
                
                <div id="result"></div>
                
                <p><a href="/api/">← Back to API Documentation</a></p>
                <p><a href="/auth/login-form/">🔐 Login</a></p>
                <p><a href="/dashboard/">📊 View Data Dashboard</a></p>
            </div>
            
            <script>
                function testEndpoint(endpoint) {{
                    const token = document.getElementById('token').value;
                    const resultDiv = document.getElementById('result');
                    
                    if (!token) {{
                        resultDiv.innerHTML = '<div class="error">❌ Please enter your JWT token first!</div>';
                        return;
                    }}
                    
                    resultDiv.innerHTML = '<div class="result">🔄 Testing...</div>';
                    
                    fetch(endpoint, {{
                        method: 'GET',
                        headers: {{
                            'Authorization': 'Bearer ' + token
                        }}
                    }})
                    .then(response => {{
                        if (response.ok) {{
                            return response.json();
                        }} else {{
                            throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                        }}
                    }})
                    .then(data => {{
                        resultDiv.innerHTML = '<div class="success">✅ Success! Response: <pre>' + JSON.stringify(data, null, 2) + '</pre></div>';
                    }})
                    .catch(error => {{
                        resultDiv.innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
                    }});
                }}
            </script>
        </body>
        </html>
    """)


@csrf_exempt
def dashboard(request):
    """Enhanced data dashboard with CRUD operations and better UI"""
    return HttpResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced Company Data Dashboard</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                .container {{ max-width: 1400px; margin: 0 auto; }}
                .header {{ background: white; padding: 30px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); text-align: center; }}
                .header h1 {{ margin: 0; color: #333; font-size: 2.5em; }}
                .header p {{ color: #666; font-size: 1.1em; margin: 10px 0 0 0; }}
                
                .token-section {{ background: white; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
                .token-section h2 {{ margin-top: 0; color: #333; }}
                input[type="text"] {{ width: 100%; padding: 15px; margin: 10px 0; border: 2px solid #e1e5e9; border-radius: 8px; font-family: monospace; font-size: 14px; box-sizing: border-box; }}
                input[type="text"]:focus {{ outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }}
                
                .button-group {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 15px 0; }}
                button {{ padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s ease; }}
                .primary {{ background: #667eea; color: white; }}
                .primary:hover {{ background: #5a6fd8; transform: translateY(-2px); }}
                .success {{ background: #28a745; color: white; }}
                .success:hover {{ background: #218838; transform: translateY(-2px); }}
                .warning {{ background: #ffc107; color: #212529; }}
                .warning:hover {{ background: #e0a800; transform: translateY(-2px); }}
                .danger {{ background: #dc3545; color: white; }}
                .danger:hover {{ background: #c82333; transform: translateY(-2px); }}
                .info {{ background: #17a2b8; color: white; }}
                .info:hover {{ background: #138496; transform: translateY(-2px); }}
                
                .data-section {{ background: white; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
                .data-section h2 {{ margin-top: 0; color: #333; }}
                
                .data-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; }}
                .data-card {{ background: #f8f9fa; padding: 20px; border-radius: 12px; border-left: 5px solid #667eea; transition: transform 0.3s ease; }}
                .data-card:hover {{ transform: translateY(-5px); }}
                .data-card h3 {{ margin-top: 0; color: #667eea; font-size: 1.3em; }}
                
                .crud-section {{ background: white; padding: 25px; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
                .crud-section h2 {{ margin-top: 0; color: #333; }}
                .crud-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
                .crud-card {{ background: #f8f9fa; padding: 20px; border-radius: 12px; border: 1px solid #e9ecef; }}
                .crud-card h4 {{ margin-top: 0; color: #495057; }}
                .form-group {{ margin-bottom: 15px; }}
                .form-group label {{ display: block; margin-bottom: 5px; font-weight: 600; color: #495057; }}
                .form-group input, .form-group select {{ width: 100%; padding: 10px; border: 1px solid #ced4da; border-radius: 5px; box-sizing: border-box; }}
                
                .loading {{ text-align: center; padding: 20px; color: #666; }}
                .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .info-box {{ background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                
                .nav-links {{ margin: 20px 0; text-align: center; }}
                .nav-links a {{ color: #667eea; text-decoration: none; margin: 0 15px; padding: 10px 20px; border-radius: 25px; background: #f8f9fa; transition: all 0.3s ease; }}
                .nav-links a:hover {{ background: #667eea; color: white; text-decoration: none; }}
                
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; }}
                .stat-number {{ font-size: 2em; font-weight: bold; margin: 10px 0; }}
                .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Enhanced Company Data Dashboard</h1>
                    <p>Complete CRUD operations with JWT authentication and advanced features</p>
                    <div class="nav-links">
                        <a href="/api/">📚 API Documentation</a>
                        <a href="/test-token/">🧪 Token Tester</a>
                        <a href="/auth/login-form/">🔐 Login</a>
                        <a href="/auth/register-form/">📝 Register</a>
                    </div>
                </div>
                
                <div class="token-section">
                    <h2>🔑 JWT Token Authentication</h2>
                    <p>Enter your JWT access token to access all features:</p>
                    <input type="text" id="token" placeholder="Paste your JWT access token here...">
                    <div class="button-group">
                        <button class="success" onclick="loadAllData()">📊 Load All Data</button>
                        <button class="info" onclick="loadStats()">📈 Load Statistics</button>
                        <button class="warning" onclick="testAllEndpoints()">🧪 Test All Endpoints</button>
                    </div>
                </div>
                
                <div class="data-section">
                    <h2>📊 Data Overview</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-label">Organizations</div>
                            <div class="stat-number" id="org-count">-</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Companies</div>
                            <div class="stat-number" id="company-count">-</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Employees</div>
                            <div class="stat-number" id="employee-count">-</div>
                        </div>
                    </div>
                    
                    <div class="data-grid">
                        <div class="data-card">
                            <h3>🏢 Organizations</h3>
                            <div id="organizations">Click "Load All Data" to see organizations</div>
                        </div>
                        
                        <div class="data-card">
                            <h3>🏭 Companies</h3>
                            <div id="companies">Click "Load All Data" to see companies</div>
                        </div>
                        
                        <div class="data-card">
                            <h3>👥 Employees</h3>
                            <div id="employees">Click "Load All Data" to see employees</div>
                        </div>
                        
                        <div class="data-card">
                            <h3>👤 Your Profile</h3>
                            <div id="profile">Click "Load All Data" to see your profile</div>
                        </div>
                    </div>
                </div>
                
                <div class="crud-section">
                    <h2>🛠️ CRUD Operations</h2>
                    <div class="crud-grid">
                        <div class="crud-card">
                            <h4>🏢 Create Organization</h4>
                            <div class="form-group">
                                <label>Organization Name:</label>
                                <input type="text" id="new-org-name" placeholder="Enter organization name">
                            </div>
                            <button class="success" onclick="createOrganization()">Create Organization</button>
                        </div>
                        
                        <div class="crud-card">
                            <h4>🏭 Create Company</h4>
                            <div class="form-group">
                                <label>Company Name:</label>
                                <input type="text" id="new-company-name" placeholder="Enter company name">
                            </div>
                            <div class="form-group">
                                <label>Organization ID:</label>
                                <input type="number" id="new-company-org" placeholder="Enter organization ID">
                            </div>
                            <button class="success" onclick="createCompany()">Create Company</button>
                        </div>
                        
                        <div class="crud-card">
                            <h4>👥 Create Employee</h4>
                            <div class="form-group">
                                <label>Employee Name:</label>
                                <input type="text" id="new-employee-name" placeholder="Enter employee name">
                            </div>
                            <div class="form-group">
                                <label>Position:</label>
                                <input type="text" id="new-employee-position" placeholder="Enter position">
                            </div>
                            <div class="form-group">
                                <label>Company ID:</label>
                                <input type="number" id="new-employee-company" placeholder="Enter company ID">
                            </div>
                            <button class="success" onclick="createEmployee()">Create Employee</button>
                        </div>
                        
                        <div class="crud-card">
                            <h4>🔍 Search All Entities</h4>
                            <div class="form-group">
                                <label>Search Query:</label>
                                <input type="text" id="search-query" placeholder="Enter search term">
                            </div>
                            <button class="info" onclick="searchAll()">Search</button>
                            <div id="search-results"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                function getToken() {{
                    return document.getElementById('token').value;
                }}
                
                function showMessage(elementId, message, type = 'info') {{
                    const element = document.getElementById(elementId);
                    element.innerHTML = `<div class="${{type}}">${{message}}</div>`;
                }}
                
                function loadAllData() {{
                    const token = getToken();
                    if (!token) {{
                        alert('Please enter your JWT token first!');
                        return;
                    }}
                    
                    loadData('/api/organizations/', 'organizations', '🏢 Organizations');
                    loadData('/api/companies/', 'companies', '🏭 Companies');
                    loadData('/api/employees/', 'employees', '👥 Employees');
                    loadData('/api/auth/profile/', 'profile', '👤 Profile');
                    loadStats();
                }}
                
                function loadStats() {{
                    const token = getToken();
                    if (!token) return;
                    
                    fetch('/api/stats/', {{
                        method: 'GET',
                        headers: {{ 'Authorization': 'Bearer ' + token }}
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById('org-count').textContent = data.total_organizations;
                        document.getElementById('company-count').textContent = data.total_companies;
                        document.getElementById('employee-count').textContent = data.total_employees;
                    }})
                    .catch(error => console.error('Error loading stats:', error));
                }}
                
                function loadData(endpoint, elementId, title) {{
                    const token = getToken();
                    const element = document.getElementById(elementId);
                    
                    element.innerHTML = '<div class="loading">🔄 Loading...</div>';
                    
                    fetch(endpoint, {{
                        method: 'GET',
                        headers: {{ 'Authorization': 'Bearer ' + token }}
                    }})
                    .then(response => {{
                        if (response.ok) return response.json();
                            throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }})
                    .then(data => {{
                        if (Array.isArray(data)) {{
                            if (data.length === 0) {{
                                element.innerHTML = '<div class="success">✅ No ' + title + ' found</div>';
                            }} else {{
                                let html = '<div class="success">✅ Found ' + data.length + ' ' + title + ':</div><ul>';
                                data.forEach(item => {{
                                    html += '<li><strong>' + (item.name || 'N/A') + '</strong>';
                                        if (item.position) html += ' - ' + item.position;
                                    if (item.organization_name) html += ' (Org: ' + item.organization_name + ')';
                                    if (item.company_name) html += ' (Company: ' + item.company_name + ')';
                                        html += '</li>';
                                }});
                                html += '</ul>';
                                element.innerHTML = html;
                            }}
                        }} else {{
                            element.innerHTML = '<div class="success">✅ ' + title + ': <pre>' + JSON.stringify(data, null, 2) + '</pre></div>';
                        }}
                    }})
                    .catch(error => {{
                        element.innerHTML = '<div class="error">❌ Error loading ' + title + ': ' + error.message + '</div>';
                    }});
                }}
                
                function createOrganization() {{
                    const token = getToken();
                    const name = document.getElementById('new-org-name').value;
                    
                    if (!token || !name) {{
                        alert('Please enter both token and organization name!');
                        return;
                    }}
                    
                    fetch('/api/organizations/', {{
                        method: 'POST',
                        headers: {{ 
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{ name: name }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.id) {{
                            alert('Organization created successfully! ID: ' + data.id);
                            document.getElementById('new-org-name').value = '';
                            loadAllData();
                        }} else {{
                            alert('Error creating organization: ' + JSON.stringify(data));
                        }}
                    }})
                    .catch(error => alert('Error: ' + error.message));
                }}
                
                function createCompany() {{
                    const token = getToken();
                    const name = document.getElementById('new-company-name').value;
                    const orgId = document.getElementById('new-company-org').value;
                    
                    if (!token || !name || !orgId) {{
                        alert('Please enter token, company name, and organization ID!');
                        return;
                    }}
                    
                    fetch('/api/companies/', {{
                        method: 'POST',
                        headers: {{ 
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{ name: name, organization: orgId }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.id) {{
                            alert('Company created successfully! ID: ' + data.id);
                            document.getElementById('new-company-name').value = '';
                            document.getElementById('new-company-org').value = '';
                            loadAllData();
                        }} else {{
                            alert('Error creating company: ' + JSON.stringify(data));
                        }}
                    }})
                    .catch(error => alert('Error: ' + error.message));
                }}
                
                function createEmployee() {{
                    const token = getToken();
                    const name = document.getElementById('new-employee-name').value;
                    const position = document.getElementById('new-employee-position').value;
                    const companyId = document.getElementById('new-employee-company').value;
                    
                    if (!token || !name || !companyId) {{
                        alert('Please enter token, employee name, and company ID!');
                        return;
                    }}
                    
                    const data = {{ name: name, company: companyId }};
                    if (position) data.position = position;
                    
                    fetch('/api/employees/', {{
                        method: 'POST',
                        headers: {{ 
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify(data)
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.id) {{
                            alert('Employee created successfully! ID: ' + data.id);
                            document.getElementById('new-employee-name').value = '';
                            document.getElementById('new-employee-position').value = '';
                            document.getElementById('new-employee-company').value = '';
                            loadAllData();
                        }} else {{
                            alert('Error creating employee: ' + JSON.stringify(data));
                        }}
                    }})
                    .catch(error => alert('Error: ' + error.message));
                }}
                
                function searchAll() {{
                    const token = getToken();
                    const query = document.getElementById('search-query').value;
                    
                    if (!token || !query) {{
                        alert('Please enter both token and search query!');
                        return;
                    }}
                    
                    fetch('/api/search/?q=' + encodeURIComponent(query), {{
                        method: 'GET',
                        headers: {{ 'Authorization': 'Bearer ' + token }}
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        let html = '<div class="success">🔍 Search Results:</div>';
                        if (data.organizations.length > 0) {{
                            html += '<h5>Organizations:</h5><ul>';
                            data.organizations.forEach(org => html += '<li>' + org.name + '</li>');
                            html += '</ul>';
                        }}
                        if (data.companies.length > 0) {{
                            html += '<h5>Companies:</h5><ul>';
                            data.companies.forEach(company => html += '<li>' + company.name + '</li>');
                            html += '</ul>';
                        }}
                        if (data.employees.length > 0) {{
                            html += '<h5>Employees:</h5><ul>';
                            data.employees.forEach(emp => html += '<li>' + emp.name + ' - ' + (emp.position || 'N/A') + '</li>');
                            html += '</ul>';
                        }}
                        if (data.organizations.length === 0 && data.companies.length === 0 && data.employees.length === 0) {{
                            html += '<p>No results found.</p>';
                        }}
                        document.getElementById('search-results').innerHTML = html;
                    }})
                    .catch(error => {{
                        document.getElementById('search-results').innerHTML = '<div class="error">❌ Error: ' + error.message + '</div>';
                    }});
                }}
                
                function testAllEndpoints() {{
                    const token = getToken();
                    if (!token) {{
                        alert('Please enter your JWT token first!');
                        return;
                    }}
                    
                    alert('Testing all endpoints... Check the console for results.');
                    
                    // Test all major endpoints
                    const endpoints = [
                        '/api/organizations/',
                        '/api/companies/',
                        '/api/employees/',
                        '/api/stats/',
                        '/api/auth/profile/'
                    ];
                    
                    endpoints.forEach(endpoint => {{
                        fetch(endpoint, {{
                            method: 'GET',
                            headers: {{ 'Authorization': 'Bearer ' + token }}
                        }})
                        .then(response => {{
                            console.log(endpoint + ': ' + response.status);
                        }})
                        .catch(error => {{
                            console.error(endpoint + ' error:', error);
                        }});
                    }});
                }}
            </script>
        </body>
        </html>
    """)

