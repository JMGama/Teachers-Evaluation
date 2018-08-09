from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import *


class LoginView(View):

    template_login = 'evaluations/login.html'

    def get(self, request):
        try:
            if request.session['session']:
                if request.session['type'] == 'student':
                    return redirect('home/')
                else:
                    return redirect('monitoring/')

        except KeyError:
            pass
        return render(request, self.template_login)

    def post(self, request):
        # Try to load student
        try:
            if self.load_student(request, request.POST['id_matricula'], request.POST['password']):
                return redirect('home/')
        except Exception as e:
            print(e)
            # Try to load coordinator
            try:
                if self.load_coordinator(request, request.POST['id_matricula'], request.POST['password']):
                    return redirect('monitoring/')
            except Exception:
                pass

        return render(request, self.template_login, {'second_time': True, 'validate': 'invalid'})

    def load_student(self, request, matricula, password):
        student = EvaluationsStudents.objects.get(
            enrollment__exact=matricula)
        if student.value == password:
            request.session['id_student'] = student.idperson
            request.session['session'] = True
            request.session['type'] = 'student'
            return True
        else:
             return False

    def load_coordinator(self, request, matricula, password):
        coordinator = EvaluationsCoordinators.objects.get(
            enrollment__exact=matricula)
        if coordinator.value == password:
            request.session['id_coordinator'] = coordinator.idperson
            request.session['session'] = True
            request.session['type'] = 'coordinator'
            return True
        else:
             return False
