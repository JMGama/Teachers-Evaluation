from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View

from .models import Alumno, Carrera, Ciclo, Docente, Materia, Pregunta
# Create your views here.


class LoginView(View):

    template_login = 'evaluations/login.html'

    def get(self, request):
        try:
            request.session.flush()
        except KeyError:
            pass
        return render(request, self.template_login)

    def post(self, request):
        try:
            student = Alumno.objects.get(
                id_matricula=request.POST['id_matricula'])
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

        return render(request, self.template_login, {'second_time': True, 'validate': 'invalid'})


class HomeView(View):

    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False):
            return render(request, self.template_login)

        signatures_list = Materia.objects.order_by('nombre_materia')[:3]

        context = {
            'signatures_list': signatures_list,
        }
        return render(request, self.template_home, context)

    def post(self, request):
        if not request.session.get('session', False):
            return render(request, self.template_login)
        try:
            signatures_list = Materia.objects.get(id_materia=request.POST['id_materia'])
        except Exception as e:
            pass
        return render(request, self.template_login, {'second_time': True, 'validate': 'invalid'})

class EvaluationView(View):

    template_evaluation = 'evaluations/evaluation_form.html'
    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request, id_materia):
        if not request.session.get('session', False):
            return render(request, self.template_login)

        signatures_list = Materia.objects.order_by('nombre_materia')[:3]
        signature = Materia.objects.get(id_materia=id_materia)
        teacher = Docente.objects.get(id_clave='1939')
        questions = Pregunta.objects.order_by('id_pregunta')

        context = {
            'signatures_list': signatures_list,
            'signature': signature,
            'teacher': teacher,
            'questions': questions,
        }

        return render(request, self.template_evaluation, context)
