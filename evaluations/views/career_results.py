import csv

import xlsxwriter
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import smart_str
from django.views import View

from evaluations.models import (EvaluationsCareer, EvaluationsCoordinator,
                                EvaluationsDtlCoordinatorCareer,
                                EvaluationsDtlTeacherCareer, EvaluationsExam,
                                EvaluationsSignatureResult, EvaluationsStudent,
                                EvaluationsTeacher)


class CareerResultsView(View):

    template_monitoring = 'evaluations/career_monitoring.html'
    template_login = 'evaluations/login.html'

    def get(self, request, career_id):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view and the monitoring navigation bar.
        coordinator = EvaluationsCoordinator.objects.get(
            pk__exact=request.session['id_coordinator'])
        careers_id = EvaluationsDtlCoordinatorCareer.objects.filter(
            fk_coordinator__exact=coordinator.id).values('fk_career')
        careers = EvaluationsCareer.objects.filter(pk__in=careers_id)

        # Get the general data for each exam in the career.
        career = EvaluationsCareer.objects.get(
            pk__exact=career_id, status="ACTIVE")
        career_data = self.get_career_data(career)

        # Get the teachers of the career.
        teachers_detail = EvaluationsDtlTeacherCareer.objects.filter(
            fk_career__exact=career.id, status="ACTIVE").select_related('fk_teacher')
        teachers = [teahcer_dtl.fk_teacher for teahcer_dtl in teachers_detail]
        print(teachers)

        context = {
            'teachers': teachers,
            'coordinator': coordinator,
            'careers': careers,
            'career': career,
            'career_data': career_data,
        }

        return render(request, self.template_monitoring, context)

    def post(self, request, career_id):
        if request.POST['action'] == 'excel':
            career = EvaluationsCareer.objects.get(pk__exact=career_id)

            # Get all the exams for the career.
            exams = EvaluationsExam.objects.filter(
                type=career.type, status__exact='ACTIVE')

            # Get the students not evaluated for each exam.
            exam_students = self.not_evaluated_students(career, exams)

            # Generates the CSV document with the students information that didnt evaluated.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=Alumnos_No_Evaluados_' + \
                str(career).capitalize() + '.csv'
            writer = csv.writer(response, csv.excel)
            response.write(u'\ufeff'.encode('utf8'))

            self.write_to_excel(exam_students, writer)
            return response

    def get_career_data(self, career):
        """Return a dictionary with the total of students evaluated, not evaluated and the average result of the career for each exam"""
        data = []

        # Get all the exams for the career.
        exams = EvaluationsExam.objects.filter(
            type__exact=career.type, status__exact='ACTIVE')

        # For each exam in the career get the results.
        for exam in exams:
            exam_data = {'exam': exam}

            # Get the total of students and the total evaluated and not evaluated in the career.
            exam_data['students'] = self.get_total_evaluated(
                career, exam)

            # Get the average result for all the signatures in the career.
            exam_data['average'] = self.get_career_average(career, exam)

            data.append(exam_data)
        return data

    def get_total_evaluated(self, career, exam):
        """Return a dictionary with the total of students, evaluated and not evaluated for the exam in the career"""

        with connection.cursor() as cursor:
            # Raw query to count the total od students already evaluated in the career.
            cursor.execute('SELECT COUNT(DISTINCT(D.fk_student)) \
            FROM evaluations_signature_evaluated A \
            JOIN evaluations_student_signature D ON A.fk_student_signature=D.id \
            JOIN evaluations_student S ON D.fk_student=S.id \
            WHERE S.fk_career='+str(career.id)+' AND A.fk_exam = '+str(exam.id)+' AND D.status="ACTIVE"')

            evaluated = cursor.fetchone()[0]

        # Get the total of students in the career and the total of not evaluated.
        total_students = EvaluationsStudent.objects.filter(
            fk_career__exact=career.id, status="ACTIVE").count()
        not_evaluated = total_students - evaluated

        # Return the dictionary with the results.
        data = {
            'evaluated': evaluated,
            'not_evaluated': not_evaluated,
            'total': total_students
        }
        return data

    def get_career_average(self, career, exam):
        """Return the average result of all the signatures in the exam of the career."""

        # Get the average results of the signatures in the career.
        signatures_averages = list(map(float, EvaluationsSignatureResult.objects.filter(
            fk_signature__fk_career__exact=career.id, fk_exam__exact=exam.id, status="ACTIVE").values_list('average', flat=True)))

        # If there is no average results in any signature, return 0
        if len(signatures_averages) == 0:
            return 0

        # Calculate the general average for the career.
        final_average = round(sum(signatures_averages) /
                              len(signatures_averages), 2)

        return final_average

    def not_evaluated_students(self, career, exams):
        """return a list with the students not evaluated for each exam"""
        data = []

        # Returns the information for each exam in the career.
        for exam in exams:
            exam_students = {'exam': exam}

            # Raw query to get the id students already evaluated in the career.
            with connection.cursor() as cursor:
                cursor.execute('SELECT DISTINCT(S.id) \
                FROM evaluations_signature_evaluated A \
                JOIN evaluations_student_signature D ON A.fk_student_signature=D.id \
                JOIN evaluations_student S ON D.fk_student=S.id \
                WHERE S.fk_career='+str(career.id)+' AND A.fk_exam='+str(exam.id)+' AND D.status="ACTIVE"')
                evaluated_students = [i[0]for i in cursor.fetchall()]

            # Get the students that aren't in the evaluated list.
            not_eval_students = EvaluationsStudent.objects.filter(
                fk_career__exact=career.id, status="ACTIVE").exclude(pk__in=evaluated_students)

            exam_students['students'] = not_eval_students
            data.append(exam_students)
        return data

    def write_to_excel(self, exam_students, writer):
        """creates the CSV with the student data that were past"""

        # For each exam get the studetnts not evaluated.
        for exam in exam_students:

            # Write in the file the career description an the headers for the data.
            writer.writerow([smart_str(exam['exam'].description)])
            writer.writerow([
                smart_str(u"Matricula"),
                smart_str(u"Nombre"),
                smart_str(u"Correo"),
            ])

            # For each student write their information.
            for student in exam['students']:
                writer.writerow([
                    smart_str(student.enrollment),
                    smart_str(str(student.name) + " " +
                              str(student.last_name) + " " + str(student.last_name_2)),
                    smart_str(student.inst_email),
                ])
            # Write 2 white spaces at the end of each exam.
            writer.writerow([])
            writer.writerow([])
