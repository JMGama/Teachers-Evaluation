from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q
from django.utils.encoding import smart_str

from evaluations.models import *
from .general_functions import *

import csv
import xlsxwriter


class MonitoringView(View, GeneralFunctions):

    template_monitoring = 'evaluations/monitoring.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view
        coordinator = EvaluationsCoordinators.objects.get(
            idperson__exact=request.session['id_coordinator'])

        careers = self.get_careers_data(coordinator)

        context = {
            'coordinator': coordinator,
            'careers': careers,
        }

        return render(request, self.template_monitoring, context)

    def post(self, request):
        if request.POST['action'] == 'excel':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=mymodel.csv'
            writer = csv.writer(response, csv.excel)
            response.write(u'\ufeff'.encode('utf8'))

            career = EvaluationsCareers.objects.get(
                idcareer__exact=request.POST['career'])
            coordinator = EvaluationsCoordinators.objects.get(
                idperson__exact=request.session['id_coordinator'])
            careers = self.get_careers_data(coordinator)
            students = careers[career]['not_evaluated']

            self.write_to_excel(students, career, writer)

            return response

    def write_to_excel(self, students, career, writer):
        writer.writerow([
            smart_str(u"Matricula"),
            smart_str(u"Nombre"),
            smart_str(u"Correo"),
        ])

        for student in students:
            writer.writerow([
                smart_str(student.enrollment),
                smart_str(str(student.name) + " " +
                          str(student.lastname) + " " + str(student.lastname2)),
                smart_str(student.instemail),
            ])

    def get_careers_data(self, coordinator):
        """Return a dictionary of all the coordinator careers with their evaluations results"""
        coordinator_careers = EvaluationsDetailCoordinatorCareer.objects.filter(
            idcoordinator__exact=coordinator.idperson)
        careers = {}
        for coord_career in coordinator_careers:
            career_students = EvaluationsStudents.objects.filter(
                idcareer=coord_career.idcareer.idcareer)

            careers[coord_career.idcareer] = self.get_evaluated_students(
                career_students)
            careers[coord_career.idcareer]['average_data'] = self. get_career_average(
                careers[coord_career.idcareer]['evaluated'])
        return careers

    def get_evaluated_students(self, career_students):
        """Return all the students already evaluated and all that haven't evaluate."""
        students = {}
        eval_students = []
        not_eval_students = []

        for student in career_students:
            evaluations = self.get_evaluations(student)
            evaluated = self.get_evaluated_signatures(student)
            not_evaluated = []

            for evaluation in evaluations:
                for group in evaluation['groups']:
                    if not group.id in evaluated:
                        not_evaluated.append(group.id)
                        break

            if not not_evaluated:
                eval_students.append(student)
            else:
                not_eval_students.append(student)

        students['evaluated'] = eval_students
        students['not_evaluated'] = not_eval_students
        return students

    def get_career_average(self, evaluated_students):
        answers_yes = 0
        answers_no = 0
        data = {}
        for student in evaluated_students:
            # Only consider non optional questions for the average
            questions = EvaluationsDetailExamQuestion.objects.filter()
            for question in questions:
                if question.idquestion.optional == 'NO':
                    answers = EvaluationsAnswers.objects.filter(
                        idstudent__exact=student.idperson, iddetailquestion__exact=question.id)
                    for answer in answers:
                        if answer.answer == 'YES':
                            answers_yes = answers_yes + 1
                        else:
                            answers_no = answers_no + 1
        data['average'] = answers_yes / (answers_yes + answers_no) * 100
        data['yes'] = answers_yes
        data['no'] = answers_no
        return data
