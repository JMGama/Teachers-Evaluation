from django.db import transaction
from django.shortcuts import render
from django.views import View

from evaluations.models import (EvaluationsCareer, EvaluationsCoordinator,
                                EvaluationsDtlCoordinatorCareer,
                                EvaluationsStudent)


class DeleteStudentView(View):

    template_delete_student = 'evaluations/delete_student.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        # Verify if the coordinator is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view and the monitoring navigation bar.
        coordinator = EvaluationsCoordinator.objects.get(
            pk__exact=request.session['id_coordinator'])
        careers_id = EvaluationsDtlCoordinatorCareer.objects.filter(
            fk_coordinator__exact=coordinator.id).values('fk_career')
        careers = EvaluationsCareer.objects.filter(pk__in=careers_id)

        # Validates if the user is admin.
        if coordinator.type != 'ADMIN':
            return render(request, self.template_login)

        # Get all the students
        students = EvaluationsStudent.objects.filter(status="ACTIVE")

        # Render the students view with the list of all the students.
        context = {
            'students': students,
            'coordinator': coordinator,
            'careers': careers,
        }

        return render(request, self.template_delete_student, context)

    def post(self, request):
        # Verify if the coordinator is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view and the monitoring navigation bar.
        coordinator = EvaluationsCoordinator.objects.get(
            pk__exact=request.session['id_coordinator'])
        careers_id = EvaluationsDtlCoordinatorCareer.objects.filter(
            fk_coordinator__exact=coordinator.id).values('fk_career')
        careers = EvaluationsCareer.objects.filter(pk__in=careers_id)

        # Validates if the user is admin.
        if coordinator.type != 'ADMIN':
            return render(request, self.template_login)

        # Check for the selected students.
        students_to_delete = request.POST.getlist('students')

        # If they didnt selected any student, return an error message.
        dialogue = []
        if not students_to_delete:
            dialogue = [
                "clear", "red", "<b>Debes seleccionar al menos un alumno para ser eliminado.</b>"]

        else:
            try:

                # Begin a transaction.
                with transaction.atomic():
                    students = EvaluationsStudent.objects.filter(
                        pk__in=students_to_delete)

                    # Set the students as inactive and their asignation signatures in the Student-Signature table.
                    EvaluationsStudent.objects.filter(
                        pk__in=students_to_delete).update(status="INACTIVE")

                # Return a dialog with the students that where eliminated.
                dialogue.append("check")
                dialogue.append("green")
                dialogue.append(
                    "<b>Los siguientes alumnos fueron eliminados correctamente:</b> <br><br>")
                for student in students:
                    dialogue[2] = dialogue[2] + student.enrollment + " - " + student.name + \
                        " " + student.last_name + " " + student.last_name_2 + \
                        " - " + student.fk_career.description + "<br>"

            except Exception as e:

                # Return a message with the error in case something whent wrong.
                dialogue = ["warning", "red",
                            "Ocurrió un error al procesar la petición. Error: " + str(e)]

        students = EvaluationsStudent.objects.filter(status="ACTIVE")
        context = {
            'dialogue': dialogue,
            'students': students,
            'coordinator': coordinator,
            'careers': careers,
        }

        return render(request, self.template_delete_student, context)
