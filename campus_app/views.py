from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account, StudentProfile, TeacherProfile

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        user_role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')
        
        user = User.objects.create_user(username=username, email=email, password=password)

        Account.objects.create(user=user, role=user_role)

        messages.success(request, 'Your account has been created successfully!')
        return redirect('login')
    return render(request,'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome 😊, {user.username} , you are logged in successfully!...🤝")
            return redirect('dashboard')
           
        else:
            messages.error(request, 'Invalid username or password')
            redirect('login')
    return render(request,'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.account.role == 'teacher':
            return redirect('teacher_dashboard')
        elif request.user.account.role == 'student':
            return redirect('student_dashboard')
    else:
        return redirect('register')  
    
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')
    
def teacher_dashboard(request):
    return render(request, 'dashboard/teacher_dashboard.html')
    
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')
    
@login_required
def student_profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name')
        profile.phone = request.POST.get('phone')
        profile.dob = request.POST.get('dob')
        profile.gender = request.POST.get('gender')
        profile.address = request.POST.get('address')
        profile.course = request.POST.get('course')
        profile.year = request.POST.get('year')
        profile.roll_number = request.POST.get('roll_number')
        profile.department = request.POST.get('department')
        profile.batch = request.POST.get('batch')
        
        if request.FILES.get('profile_pic'):
            account = Account.objects.get(user=request.user)
            account.profile_pic = request.FILES.get('profile_pic')
            account.save()

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('student_profile') 

    return render(request, 'profile/student_profile.html', {'profile': profile})

@login_required
def teacher_profile(request):
    profile, created = TeacherProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name')
        profile.phone = request.POST.get('phone')
        profile.dob = request.POST.get('dob')
        profile.gender = request.POST.get('gender')
        profile.address = request.POST.get('address')
        profile.qualification = request.POST.get('qualification')
        profile.experience = request.POST.get('experience')
        profile.department = request.POST.get('department')
        profile.subjects = request.POST.get('subjects')
        profile.designation = request.POST.get('designation')

        if 'profile_pic' in request.FILES:
            account = Account.objects.get(user=request.user)
            account.profile_pic = request.FILES.get('profile_pic')
            account.save()

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('teacher_profile')  

    return render(request, 'profile/teacher_profile.html', {'profile': profile})
