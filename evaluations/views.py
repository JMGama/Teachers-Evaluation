from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View

from .models import *
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
            student = InstitutionalStudents.objects.get(
                enrollment=request.POST['id_matricula'])
            if student.value == request.POST['password']:
                request.session['session'] = True
                request.session['id_matricula'] = student.enrollment
                request.session['nombre'] = student.name
                request.session['apellido_paterno'] = student.lastname
                request.session['apellido_materno'] = student.lastname2
                request.session['correo'] = student.instemail
                request.session['carrera'] = ParkingCareer.objects.get(idcareergissa__exact=student.idcareer).idcareer
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
        signatures_list = EvaluationsSignatures.objects.filter(idcareer__exact=request.session['carrera'], status="ACTIVO")

        context = {
            'signatures_list': signatures_list,
        }
        return render(request, self.template_home, context)

    def post(self, request):
        if not request.session.get('session', False):
            return render(request, self.template_login)

        try:
            signatures_list = Materia.objects.get(
                id_materia=request.POST['id_materia'])
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
