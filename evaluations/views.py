from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from .models import *
# Create your views here.


class LoginView(View):

    template_login = 'evaluations/login.html'

    def get(self, request):
        try:
            if request.session['session']:
                return redirect('home/')
        except KeyError:
            pass
        return render(request, self.template_login)

    def post(self, request):
        try:
            student = InstitutionalStudents.objects.get(
                enrollment=request.POST['id_matricula'])
            if student.value == request.POST['password']:
                request.session['session'] = True
                request.session['matricula'] = student.enrollment
                request.session['nombre'] = student.name
                request.session['apellido_paterno'] = student.lastname
                request.session['apellido_materno'] = student.lastname2
                request.session['correo'] = student.instemail
                request.session['carrera'] = ParkingCareer.objects.get(
                    idcareergissa__exact=student.idcareer).idcareer
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

        # Values for the navigation bar
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=request.session['carrera']) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__enrollment__exact=request.session['matricula'], status="ACTIVO")

        context = {
            'user_exams': user_exams,
            'user_groups': user_groups,
        }
        return render(request, self.template_home, context)


class EvaluationView(View):

    template_evaluation = 'evaluations/evaluation_form.html'
    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'
    test = 'evaluations/detail.html'

    def get(self, request, exam_id, group_id):
        if not request.session.get('session', False):
            return render(request, self.template_login)

        # Values for the navigation bar
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=request.session['carrera']) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__enrollment__exact=request.session['matricula'], status="ACTIVO")

        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)

        group = EvaluationsDetailStudentGroup.objects.get(id__exact=group_id)
        career = ParkingCareer.objects.get(
            idcareer__exact=request.session['carrera'])

        context = {
            'user_exams': user_exams,
            'user_groups': user_groups,
            'exam_questions': exam_questions,
            'group': group,
            'career': career,
        }

        return render(request, self.template_evaluation, context)


class LogoutView(View):
    def get(self, request):
        try:
            request.session.flush()
        except KeyError:
            pass
        return redirect('/evaluations')
