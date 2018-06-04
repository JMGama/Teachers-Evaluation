from django.urls import path

from . import views

app_name = 'evaluations'
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('home/', views.home, name='home'),
    path('<slug:matricula>/', views.user_detail, name='user_detail')
]
