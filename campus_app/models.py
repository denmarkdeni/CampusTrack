from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/user.png')

    def __str__(self):
        return f"{self.user.username} ({self.role})" 
    
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.TextField()

    # Academic
    course = models.CharField(max_length=100)
    year = models.CharField(max_length=20)
    roll_number = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    batch = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    address = models.TextField(blank=True)

    qualification = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(null=True, blank=True)  
    department = models.CharField(max_length=100)
    subjects = models.TextField()
    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
    
class Degree(models.Model):
    name = models.CharField(max_length=100)  # e.g. BSc, B.Tech
    duration_years = models.IntegerField()
    total_semesters = models.IntegerField()

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)  # e.g. Computer Science
    def __str__(self):
        return self.name


class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=100)

    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    semester = models.IntegerField()
    year = models.IntegerField()

    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'account__role': 'teacher'}
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=9)  # Example: '2024-2025'
    status = models.CharField(max_length=20, choices=[('enrolled', 'Enrolled'), ('completed', 'Completed'), ('dropped', 'Dropped')], default='enrolled')
    date_enrolled = models.DateField(auto_now_add=True)
    date_completed = models.DateField(null=True, blank=True)
    date_dropped = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.course_name}"

class Mark(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.IntegerField()
    internal_marks = models.FloatField()
    external_marks = models.FloatField()
    grade = models.CharField(max_length=2)  # A, B, C etc.

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.grade}"
