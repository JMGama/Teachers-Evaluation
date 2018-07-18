from django.urls import path

from . import views

app_name = 'evaluations'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('evaluation/<slug:exam_id>/<slug:detail_group_id>/',
         views.EvaluationView.as_view(), name='evaluation')
]
