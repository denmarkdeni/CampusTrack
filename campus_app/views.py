from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account, StudentProfile, TeacherProfile, Degree, Department, Course , Enrollment
from datetime import datetime

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

    context = {
        "total_students":Account.objects.filter(role="student").count(),
        "total_teachers":Account.objects.filter(role="teacher").count(),
        "total_courses":Course.objects.all().count(),
        "cultural_events":100,
        "enrollments":Enrollment.objects.all().order_by('-date_enrolled')[:5],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
    
def teacher_dashboard(request):
    return render(request, 'dashboard/teacher_dashboard.html')
    
def student_dashboard(request):
    return render(request, 'dashboard/student_dashboard.html')

def profile(request):
    if request.user.is_authenticated:
        if request.user.account.role == 'student':
            return redirect('student_profile')
        elif request.user.account.role == 'teacher':
            return redirect('teacher_profile')
    else:
        return redirect('login')
    
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

@login_required
def add_course(request):
    if request.method == 'POST':
        course_code = request.POST['course_code']
        course_name = request.POST['course_name']
        degree_id = request.POST['degree_id']
        department_id = request.POST['department_id']
        semester = request.POST['semester']
        year = request.POST['year']
        teacher_id = request.POST.get('teacher_id')

        degree = Degree.objects.get(id=degree_id)
        department = Department.objects.get(id=department_id)
        teacher = User.objects.get(id=teacher_id) if teacher_id else None

        Course.objects.create(
            course_code=course_code,
            course_name=course_name,
            degree=degree,
            department=department,
            semester=semester,
            year=year,
            teacher=teacher
        )

        messages.success(request, 'Course added successfully!')
        return redirect('add_course')

    degrees = Degree.objects.all()
    departments = Department.objects.all()
    teachers = User.objects.filter(account__role='teacher')

    return render(request, 'course/course_add.html', {
        'degrees': degrees,
        'departments': departments,
        'teachers': teachers
    })

def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course/course_list.html', {'courses': courses})

def all_courses(request):
    departments = Department.objects.all().order_by('name')
    return render(request, 'course/all_courses.html', {'departments': departments})

def student_course_list(request):
    enrollments = Enrollment.objects.filter(student=request.user)
    return render(request, 'course/student_course_list.html', {'enrollments': enrollments})

def course_details(request, dep_id):
    department = Department.objects.get(id=dep_id)
    courses = Course.objects.filter(department=department).order_by('course_code')
    IsEnrolled = Enrollment.objects.filter(student=request.user, department=department).exists()

    if not IsEnrolled:
        return redirect('course_enrollment', dep_id=dep_id)
    
    if not courses:
        messages.warning(request, 'No courses found for this department.')
    
    return render(request, 'course/course_details.html', {
        'department': department,
        'courses': courses
    })

def course_enrollment(request, dep_id):
    department = Department.objects.get(id=dep_id)
    courses = Course.objects.filter(department=department).order_by('course_code')
    current = datetime.now()
    academic_year = f"{current.year}-{current.year + department.degree.duration_years }" 
    total_subjects = Course.objects.filter(department=department).count()
    
    if request.method == 'POST':

        Enrollment.objects.create(
            student=request.user,
            department=department,
            academic_year=academic_year
        )
        
        messages.success(request, 'Courses enrolled successfully!')
        return redirect('student_dashboard')

    return render(request, 'course/course_enrollment.html', {
        'department': department,
        'courses': courses,
        'academic_year': academic_year,
        'total_subjects': total_subjects
    })

@login_required
def user_management(request):
    accounts = Account.objects.all()
    return render(request, 'admin/user_management.html', {'accounts': accounts})

@login_required
def approve_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('user_management')

@login_required
def remove_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('user_management')

@login_required
def course_management(request):
    courses = Course.objects.all()
    return render(request, 'admin/course_management.html', {'courses': courses})

@login_required
def remove_course(request, course_id):
    course = Course.objects.get(id=course_id)
    course.delete()
    return redirect('course_management')

@login_required
def enrollment_management(request):
    enrollments = Enrollment.objects.all()
    return render(request, 'admin/enrollment_management.html', {'enrollments': enrollments})

@login_required
def remove_enrollment(request, enrollment_id):
    enrollment = Enrollment.objects.get(id=enrollment_id)
    enrollment.delete()
    return redirect('enrollment_management')