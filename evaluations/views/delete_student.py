from django.views import View
from django.shortcuts import render

from .general_functions import *

class DeleteStudentView(View, GeneralFunctions):

    template_delete_student = 'evaluations/delete_student.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view
        coordinator = EvaluationsCoordinators.objects.get(
            idperson__exact=request.session['id_coordinator'])
        careers_id = EvaluationsDetailCoordinatorCareer.objects.filter(
            idcoordinator__exact=coordinator.idperson).values('idcareer')
        careers = EvaluationsCareers.objects.filter(idcareer__in=careers_id)
        
        #Validates if the user is admin
        if coordinator.enrollment != '503':
            return render(request, self.template_login)

        students = EvaluationsStudents.objects.all()
        print(students)
        context = {
            'students': students,
            'coordinator': coordinator,
            'careers': careers,
        }

        return render(request, self.template_delete_student, context)
