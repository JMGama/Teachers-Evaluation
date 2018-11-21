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

        # Validates if the user is admin
        if coordinator.type != 'ADMINISTRATIVO':
            return render(request, self.template_login)

        students = EvaluationsStudents.objects.all()
        context = {
            'students': students,
            'coordinator': coordinator,
            'careers': careers,
        }

        return render(request, self.template_delete_student, context)

    def post(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view
        coordinator = EvaluationsCoordinators.objects.get(
            idperson__exact=request.session['id_coordinator'])
        careers_id = EvaluationsDetailCoordinatorCareer.objects.filter(
            idcoordinator__exact=coordinator.idperson).values('idcareer')
        careers = EvaluationsCareers.objects.filter(idcareer__in=careers_id)

        # Validates if the user is admin
        if coordinator.enrollment != '503':
            return render(request, self.template_login)

        # Check for the selected students
        students_to_delete = request.POST.getlist('students')

        # Deleted students dialogue information
        dialogue = ["warning","red","Ocurrió un error al procesar la petición."]
        students_deleted = EvaluationsStudents.objects.filter(
            idperson__in=students_to_delete)
        if not students_deleted:
            dialogue = ["clear","red","<b>Debes seleccionar al menos un alumno para ser eliminado.</b>"]
        else:
            dialogue[0] = "check"
            dialogue[1] = "green"
            dialogue[2] = "<b>Los siguientes alumnos fueron eliminados correctamente:</b> <br><br>"
            for student in students_deleted:
                dialogue[2] = dialogue[2] + student.enrollment + " - " + student.name + \
                    " " + student.lastname + " " + student.lastname2 + " - " + student.idcareer.description + "<br>"

        # Delete all the information about the student(s)
        EvaluationsAnswers.objects.filter(
            idstudent__in=students_to_delete).delete()
        EvaluationsDetailStudentSignatureExam.objects.filter(
            idstudent__in=students_to_delete).delete()
        EvaluationsDetailStudentGroup.objects.filter(
            idstudent__in=students_to_delete).delete()
        EvaluationsStudents.objects.filter(
            idperson__in=students_to_delete).delete()

        students = EvaluationsStudents.objects.all()
        context = {
            'dialogue': dialogue,
            'students': students,
            'coordinator': coordinator,
            'careers': careers,
        }

        return render(request, self.template_delete_student, context)
