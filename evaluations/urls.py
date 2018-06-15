from django.urls import path

from . import views

app_name = 'evaluations'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('evaluation/<slug:id_materia>/', views.EvaluationView.as_view(), name='evaluation')
]
