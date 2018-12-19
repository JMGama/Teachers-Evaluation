from . import views
from django.urls import path

app_name = 'evaluations'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
#     path('teacher/home', views.TeacherHomeView.as_view(), name='teacher_home'),

    path('evaluation/<slug:exam_id>/<slug:signature>/',
         views.EvaluationView.as_view(), name='evaluation'),
#     path('teacher/evaluation/<slug:exam_id>/<slug:signature_dtl_id>/',
#          views.TeacherEvaluationView.as_view(), name='teacher_evaluation'),
#     path('reports/teacher/<slug:report_type>/',
#          views.TeachersReportsView.as_view(), name='teachers_reports'),

    path('career_results/<slug:career_id>/',
         views.CareerResultsView.as_view(), name='career_results'),
    path('career_results/<slug:career_id>/<slug:teacher_id>/',
         views.TeacherResultsView.as_view(), name='teacher_results'),

    path('monitoring/', views.MonitoringView.as_view(), name='monitoring'),
#     path('monitoring/admin_reports/<slug:career_type>',
#          views.AdminReportsView.as_view(), name='admin_reports'),
#     path('monitoring/delete_student',
#          views.DeleteStudentView.as_view(), name='delete_student'),

]
