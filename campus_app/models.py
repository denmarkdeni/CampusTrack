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