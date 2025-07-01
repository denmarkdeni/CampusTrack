from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Account, StudentProfile, TeacherProfile, Degree, Department, Feedback
from .models import Course , Enrollment, Mark, Project, Submission, CulturalEvent, EventParticipation
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def home(request):
    context = {
        "students":Account.objects.filter(role="student").count(),
        "teachers":Account.objects.filter(role="teacher").count(),
        "courses":Course.objects.all().count(),
        "culturals": CulturalEvent.objects.all().count(),
        "departments": Department.objects.all()[:6],
        "teachers_list": TeacherProfile.objects.all(),
        "feedback":Feedback.objects.all().order_by('-created_at')[:5],
    }
    return render(request, 'home.html', context)

def department_detail(request, department_id):
    department = Department.objects.get(id=department_id)
    return render(request, 'course/department_detail.html', {'department': department})

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
        "cultural_events": CulturalEvent.objects.all().count(),
        "enrollments":Enrollment.objects.all().order_by('-date_enrolled')[:5],
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
    
def teacher_dashboard(request):
    context = {
        "total_students":Account.objects.filter(role="student").count(),
        "marks_reviewed": Mark.objects.all().count(),
        "total_courses":Course.objects.all().count(),
        "cultural_events": CulturalEvent.objects.all().count(),
        "enrollments":Enrollment.objects.all().order_by('-date_enrolled')[:5],
    }
    return render(request, 'dashboard/teacher_dashboard.html', context)
    
@login_required
def student_dashboard(request):
    project_count = Project.objects.filter(course__department__in=Enrollment.objects.filter(student=request.user).values_list('department', flat=True)).count()
    submission_count = Submission.objects.filter(student=request.user).count()
    event_count = EventParticipation.objects.filter(participant=request.user).count()
    courses_count = Course.objects.filter(department__in=Enrollment.objects.filter(student=request.user).values_list('department', flat=True)).count()
    
    recent_enrollments = Enrollment.objects.filter(student=request.user).order_by('-date_enrolled')[:2]
    recent_submissions = Submission.objects.filter(student=request.user).order_by('-submitted_at')[:2]
    recent_events = EventParticipation.objects.filter(participant=request.user).order_by('-event__start_date')[:2]
    
    context = {
        "project_count": project_count,
        "submission_count": submission_count,
        "event_count": event_count,
        "courses_count": courses_count,
        "recent_enrollments": recent_enrollments,
        "recent_submissions": recent_submissions,
        "recent_events": recent_events,
    }
    return render(request, 'dashboard/student_dashboard.html', context)

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
    enrollment = Enrollment.objects.filter(student=request.user, department=department)
    IsEnrolled = enrollment.exists()

    if not IsEnrolled:
        return redirect('course_enrollment', dep_id=dep_id)
    
    if not courses:
        messages.warning(request, 'No courses found for this department.')
    
    return render(request, 'course/course_details.html', {
        'department': department,
        'courses': courses,
        'enrollment': enrollment.first() if enrollment else None,
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

@login_required
def update_enrollment_status(request, enrollment_id):
    if request.method == 'POST':
        enrollment = Enrollment.objects.get(id=enrollment_id)
        enrollment.status = request.POST['status']
        if enrollment.status == 'completed':
            enrollment.date_completed = timezone.now().date()
            enrollment.date_dropped = None
        elif enrollment.status == 'dropped':
            enrollment.date_dropped = timezone.now().date()
            enrollment.date_completed = None
        else:
            enrollment.date_completed = None
            enrollment.date_dropped = None
        enrollment.save()
        return redirect('enrollment_management')
    return redirect('enrollment_management')

@login_required
def cultural_event_management(request):
    events = CulturalEvent.objects.all()
    return render(request, 'admin/cultural_event_management.html', {'events': events})

@login_required
def delete_event(request, event_id):
    event = CulturalEvent.objects.get(id=event_id)
    event.delete()
    return redirect('cultural_event_management')

@login_required
def project_management(request):
    projects = Project.objects.all()
    return render(request, 'admin/project_management.html', {'projects': projects})

@login_required
def delete_project(request, project_id):
    project = Project.objects.get(id=project_id)
    project.delete()
    return redirect('project_management')

@login_required
def marks_upload(request):
    enrollments = Enrollment.objects.filter(status='enrolled')
    return render(request, 'marks/marks_upload.html', {'enrollments': enrollments})

@login_required
def upload_marks(request, enrollment_id):
    if request.method == 'POST':
        enrollment = Enrollment.objects.get(id=enrollment_id)
        Mark.objects.create(
            enrollment=enrollment,
            year=request.POST['year'],
            semester=request.POST['semester'],
            internal_marks=request.POST['internal_marks'],
            external_marks=request.POST['external_marks'],
            grade=request.POST['grade']
        )
        messages.success(request, 'Marks uploaded successfully!')
        return redirect('marks_upload')
    return redirect('marks_upload')

@login_required
def all_marks(request):
    marks = Mark.objects.all()
    return render(request, 'marks/all_marks.html', {'marks': marks})

@login_required
def my_marks(request):
    marks = Mark.objects.filter(enrollment__student=request.user).order_by('semester')
    return render(request, 'marks/my_marks.html', {'marks': marks})

@login_required
def project_upload(request):
    if request.method == 'POST':
        Project.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            course_id=request.POST['course'],
            assigned_date=request.POST['assigned_date'],
            due_date=request.POST['due_date']
        )
        messages.success(request, 'Project uploaded successfully!')
        return redirect('project_upload')
    courses = Course.objects.all()
    return render(request, 'projects/project_upload.html', {'courses': courses})

@login_required
def project_list(request):
    if request.user.account.role == 'student':
        departments = Enrollment.objects.filter(student=request.user).values_list('department', flat=True)
        projects = Project.objects.filter(course__department__in=departments)
    else:
        projects = Project.objects.all()
    return render(request, 'projects/project_list.html', {'projects': projects})

@login_required
def submit_project(request, project_id):
    project = Project.objects.get(id=project_id)
    if request.method == 'POST':
        Submission.objects.create(
            student=request.user,
            project=project,
            file=request.FILES['file']
        )
        messages.success(request, 'Project submitted successfully!')
        return redirect('project_list')
    return render(request, 'projects/submit_project.html', {'project': project})

@login_required
def submission_list(request):
    submissions = Submission.objects.all().order_by('-submitted_at')
    return render(request, 'projects/submission_list.html', {'submissions': submissions})

@login_required
def add_remarks(request, submission_id):
    if request.method == 'POST':
        submission = Submission.objects.get(id=submission_id)
        submission.remarks = request.POST['remarks']
        submission.save()
        messages.success(request, 'Remarks added successfully!')
        return redirect('submission_list')
    return redirect('submission_list')

@login_required
def event_upload(request):
    if request.method == 'POST':
        CulturalEvent.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            department_id=request.POST['department'],
            created_by=request.user
        )
        messages.success(request, 'Cultural Event added successfully!')
        return redirect('event_upload')
    departments = Department.objects.all()
    return render(request, 'culturals/event_upload.html', {'departments': departments})

@login_required
def event_list(request):
    today = timezone.now().date()
    if request.user.account.role == 'student':
        events = CulturalEvent.objects.filter(start_date__lte=today, end_date__gte=today)
    else:
        events = CulturalEvent.objects.all().order_by('-start_date')
    return render(request, 'culturals/event_list.html', {'events': events})

@login_required
def participate_event(request, event_id):
    event = CulturalEvent.objects.get(id=event_id)
    if request.method == 'POST':
        EventParticipation.objects.create(
            event=event,
            participant=request.user,
            role=request.POST['role']
        )
        messages.success(request, 'Participated successfully!')
        return redirect('event_list')
    return render(request, 'culturals/participate_event.html', {'event': event})

@login_required
def my_events(request):
    participations = EventParticipation.objects.filter(participant=request.user)
    return render(request, 'culturals/my_events.html', {'participations': participations})

@login_required
def participant_list(request):
    participations = EventParticipation.objects.filter(event__created_by=request.user)
    return render(request, 'culturals/participant_list.html', {'participations': participations})

@login_required
def update_participant_status(request, participation_id):
    if request.method == 'POST':
        participation = EventParticipation.objects.get(id=participation_id)
        participation.status = request.POST['status']
        participation.feedback = request.POST['feedback']
        
        if 'certificate' in request.FILES:
            participation.certificate = request.FILES['certificate']
        elif participation.status in ['Participated', 'Won']:
            # Generate certificate
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(100, 750, f"Certificate of {participation.status}")
            p.drawString(100, 730, f"Presented to {participation.participant.username}")
            p.drawString(100, 710, f"For {participation.role} in {participation.event.name}")
            p.showPage()
            p.save()
            buffer.seek(0)
            participation.certificate.save(
                f"{participation.event.name}_{participation.participant.username}.pdf",
                ContentFile(buffer.getvalue())
            )
            buffer.close()
        
        participation.save()
        messages.success(request, 'Updated!')
        return redirect('participant_list')
    return redirect('participant_list')

@login_required
def feedback_form(request):
    if request.method == 'POST':
        Feedback.objects.create(
            student=request.user,
            department_id=request.POST['course'],
            comments=request.POST['comments'],
            rating=request.POST['rating']
        )
        messages.success(request, 'Feedback submitted successfully!')
        return redirect('my_feedback')
    departments = Department.objects.all()
    return render(request, 'feedback/feedback_form.html', {'courses': departments})

@login_required
def my_feedback(request):
    feedback_list = Feedback.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'feedback/my_feedback.html', {'feedback_list': feedback_list})