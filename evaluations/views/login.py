from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from evaluations.models import (EvaluationsCoordinator, EvaluationsStudent,
                                EvaluationsTeacher)


class LoginView(View):

    template_login = 'evaluations/login.html'

    def get(self, request):
        """ Check if the user ir already logged in, if it is redirect to the landing page, otherway redirect to login page"""
        try:
            # If the user is already logged in redirect them to the corresponding landing page.
            if request.session['session']:
                if request.session['type'] == 'student':
                    return redirect('home/')
                elif request.session['type'] == 'coordinator':
                    return redirect('monitoring/')
                else:
                    return redirect('teacher/home')

        except KeyError:
            pass
        # If the user didn't logged in before, redirect to de login page.
        return render(request, self.template_login)

    def post(self, request):
        """Verify if the login data is correct, and redirect to their corresponding landing page"""
        try:
            # Try to load student
            if self.load_student(request, request.POST['id_matricula'], request.POST['password']):
                return redirect('home/')
        except Exception:
            # Try to load coordinator
            try:
                if self.load_coordinator(request, request.POST['id_matricula'], request.POST['password']):
                    return redirect('monitoring/')
            except Exception:
                # Try to load teacher
                try:
                    if self.load_teacher(request, request.POST['id_matricula'], request.POST['password']):
                        return redirect('teacher/home')
                except Exception:
                    pass

        return render(request, self.template_login, {'second_time': True, 'validate': 'invalid'})

    def load_student(self, request, matricula, password):
        """load the student, create the session variables and return false if the data was incorrect"""
        student = EvaluationsStudent.objects.get(
            enrollment__exact=matricula)

        # If the matricula and password was correct, create session variables
        if student.password == password:
            request.session['id_student'] = student.id
            request.session['session'] = True
            request.session['type'] = 'student'
            return True
        else:
            return False

    def load_coordinator(self, request, matricula, password):
        """load the coordinator, create the session variables and return false if the data was incorrect"""
        coordinator = EvaluationsCoordinator.objects.get(
            enrollment__exact=matricula)

        # If the matricula and password was correct, create session variables
        if coordinator.password == password:
            request.session['id_coordinator'] = coordinator.id
            request.session['session'] = True
            request.session['type'] = 'coordinator'
            return True
        else:
            return False

    def load_teacher(self, request, matricula, password):
        """load the teacher, create the session variables and return false if the data was incorrect"""
        teacher = EvaluationsTeacher.objects.get(enrollment__exact=matricula)

        # If the matricula and password was correct, create session variables
        if teacher.password == password:
            request.session['id_teacher'] = teacher.id
            request.session['session'] = True
            request.session['type'] = 'teacher'
            return True
        else:
            return False
