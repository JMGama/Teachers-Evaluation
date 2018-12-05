from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from easy_pdf.rendering import render_to_pdf_response
from .general_functions import *

import csv


class TeachersReportsView(View, GeneralFunctions):
    template_login = 'evaluations/login.html'

    def get(self, request, report_type):
        """Function that make the teacher/s reports"""
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        template = ''
        context = {}

        if report_type == 'all_teachers_report':
            template, context = self.all_teachers_report(request)
        elif report_type == 'teacher_report':
            template, context = self.teacher_report(request)
        elif report_type == 'career_teachers_report':
            template, context = self.career_teachers_report(request)
        elif report_type == 'career_teachers_excel':
            return self.career_teachers_excel(request)
        
        if template and context:
            return render_to_pdf_response(request, template, context)

        return redirect('/evaluations/career_results/32/47740/#reportes')

    def all_teachers_report(self, request):
        template = 'evaluations/teach_report.html'

        coordinator = EvaluationsCoordinators.objects.get(
            idperson__exact=request.session['id_coordinator'])
        coordinator_careers = EvaluationsDetailCoordinatorCareer.objects.select_related(
            'idcareer').filter(idcoordinator__exact=coordinator.idperson)

        data = {}
        for career_detail in coordinator_careers:
            career = career_detail.idcareer
            career_data = self.get_career_data(career)

            teachers_signatures_results = self.get_teachers_signatures_results(
                career, career_data)
            data[career] = teachers_signatures_results

        context = {
            'all': data,
        }
        return template, context

    def teacher_report(self, request):
        template = 'evaluations/teachers_report.html'

        career_id = request.GET.get('career_id', '')
        teacher_id = request.GET.get('teacher_id', '')

        data = {}

        career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
        teacher = EvaluationsTeachers.objects.get(idperson__exact=teacher_id)
        career_data = self.get_career_data(career)

        data[teacher] = self.get_teacher_signatures_results(
            career, career_data, teacher, exam=career_data['exams'][0])

        context = {
            'data': data,
            'exam': career_data['exams'][0],
        }
        return template, context

    def career_teachers_report(self, request):
        template = 'evaluations/teachers_report.html'

        career_id = request.GET.get('career_id', '')
        data = {}

        career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
        career_teachers = self.get_career_teachers(career)
        career_data = self.get_career_data(career)

        for teacher in career_teachers:
            data[teacher] = self.get_teacher_signatures_results(
                career, career_data, teacher, exam=career_data['exams'][0])

        context = {
            'data': data,
            'exam': career_data['exams'][0],
        }

        return template, context

    def career_teachers_excel(self, request):
        career_id = request.GET.get('career_id', '')
        career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
        results = self.get_teachers_results(career)
        response = self.teacher_results_excel(request, results)
        return response

    def get_teachers_results(self, career):
        results = {}

        data = {}
        career_teachers = self.get_career_teachers(career)
        career_data = self.get_career_data(career)

        for teacher in career_teachers:
            data[teacher] = self.get_teacher_signatures_results(
                career, career_data, teacher, exam=career_data['exams'][0])
        results[career] = data

        return results

    def teacher_results_excel(self, request, results):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Resultados_Docentes.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        titles = ['CARRERA', 'MATERIA', 'DOCENTE', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6',
                  'P7', 'P8', 'P9', 'P10', 'P11', 'P12', 'TOTAL ALUMNOS EVALUADOS']

        writer.writerow([smart_str(u""+title) for title in titles])
        for career, teachers in results.items():
            for teacher, signatures in teachers.items():
                for singature, items in signatures.items():
                    teacher_data = [career.description, singature.name,
                                    teacher.name+" "+teacher.lastname+" "+teacher.lastname2]
                    for question, data in items['questions'].items():
                        if 'average'in data:
                            teacher_data.append(str(data['average']) + "%")
                        else:
                            comments = ''
                            for answer in data['answers']:
                                if len(answer.answer) > 2:
                                    comments += answer.answer + " | "
                            comments.replace('\n', '').replace('\r', '')
                            teacher_data.append(comments)
                    teacher_data.append(items['evaluated'])
                    writer.writerow(teacher_data)
            writer.writerow([])
        return response
