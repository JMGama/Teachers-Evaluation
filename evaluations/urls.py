from . import views
from django.urls import path

app_name = 'evaluations'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    path('evaluation/<slug:exam_id>/<slug:signature>/',
         views.EvaluationView.as_view(), name='evaluation'),

    path('career_results/<slug:career_id>/', views.CareerResultsView.as_view(), name='career_results'),
    path('career_results/<slug:career_id>/<slug:teacher_id>/', views.TeacherResultsView.as_view(), name='teacher_results'),

    path('monitoring/', views.MonitoringView.as_view(), name='monitoring'),
    path('monitoring/admin_reports', views.AdminReports.as_view(), name='admin_reports'),
    path('monitoring/tech_report', views.tech_report.as_view(), name='tech_report'),
    
]
