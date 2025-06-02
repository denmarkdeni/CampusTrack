from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account

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

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome 😊, {user.username} , you are logged in successfully!...🤝")
            return redirect('admin_dashboard')
           
        else:
            messages.error(request, 'Invalid username or password')
            redirect('login')
    return render(request,'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
