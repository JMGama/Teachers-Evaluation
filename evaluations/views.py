from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View

from .models import Alumno
# Create your views here.


class LoginView(View):

    template_name = 'evaluations/login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            student =  Alumno.objects.get(id_matricula=request.POST['id_matricula'])
            if student.password == request.POST['password']:
                request.session['session'] = True
                request.session['id_matricula'] = student.id_matricula
                request.session['nombre'] = student.nombre
                request.session['apellido_paterno'] = student.apellido_paterno
                request.session['apellido_materno'] = student.apellido_materno
                request.session['correo'] = student.correo

                return redirect('home/')
        except Exception as e:
            pass

        return render(request, self.template_name, {'second_time': True, 'validate': 'invalid'})


def home(request):
    if not request.session.get('session', False):
        return render(request, 'evaluations/login.html')

    students_list = Alumno.objects.order_by('nombre')[:]
    context = {
        'students_list': students_list,
    }
    return render(request, 'evaluations/home.html', context)


def user_detail(request, id_matricula):
    student = get_object_or_404(Alumno, id_matricula=id_matricula)
    return render(request, 'evaluations/user_detail.html', {'student': student})
