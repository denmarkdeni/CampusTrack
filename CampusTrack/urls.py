"""
URL configuration for CampusTrack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from campus_app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),

    path('user-management/', views.user_management, name='user_management'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('remove-user/<int:user_id>/', views.remove_user, name='remove_user'),

    path('course-management/', views.course_management, name='course_management'),
    path('remove-course/<int:course_id>/', views.remove_course, name='remove_course'),
    path('cultural-event-management/', views.cultural_event_management, name='cultural_event_management'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('project-management/', views.project_management, name='project_management'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),

    path('enrollment-management/', views.enrollment_management, name='enrollment_management'),
    path('remove-enrollment/<int:enrollment_id>/', views.remove_enrollment, name='remove_enrollment'),
    path('update-enrollment-status/<int:enrollment_id>/', views.update_enrollment_status, name='update_enrollment_status'),

    path('dashboard/profile/', views.profile, name='profile'),
    path('dashboard/student/profile/', views.student_profile, name='student_profile'),
    path('dashboard/teacher/profile/', views.teacher_profile, name='teacher_profile'),

    path('course/add/', views.add_course, name='add_course'),
    path('course/list/', views.course_list, name='course_list'),
    path('course/all/', views.all_courses, name='all_courses'),
    path('course/Student/list', views.student_course_list, name='student_course_list'),
    path('course/details/<int:dep_id>', views.course_details, name='course_details'),
    path('course/enroll/<int:dep_id>/', views.course_enrollment, name='course_enrollment'),

    path('teacher/marks-upload/', views.marks_upload, name='marks_upload'),
    path('teacher/upload-marks/<int:enrollment_id>/', views.upload_marks, name='upload_marks'),
    path('teacher/all-marks/', views.all_marks, name='all_marks'),
    path('student/my-marks/', views.my_marks, name='my_marks'),

    path('project-upload/', views.project_upload, name='project_upload'),
    path('projects/', views.project_list, name='project_list'),
    path('submit-project/<int:project_id>/', views.submit_project, name='submit_project'),
    path('submission-list/', views.submission_list, name='submission_list'),
    path('add-remarks/<int:submission_id>/', views.add_remarks, name='add_remarks'),

    path('event-upload/', views.event_upload, name='event_upload'),
    path('events/', views.event_list, name='event_list'),
    path('participate-event/<int:event_id>/', views.participate_event, name='participate_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('participant-list/', views.participant_list, name='participant_list'),
    path('update-participant/<int:participation_id>/', views.update_participant_status, name='update_participant_status'),

    path('department/<int:department_id>/', views.department_detail, name='department_detail'),

    path('feedback/', views.feedback_form, name='feedback_form'),
    path('my-feedback/', views.my_feedback, name='my_feedback'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)