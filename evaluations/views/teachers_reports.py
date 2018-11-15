from django.shortcuts import render, redirect
from django.views import View
from easy_pdf.rendering import render_to_pdf_response
from .general_functions import *


class TeachersReportsView(View, GeneralFunctions):
    template_login = 'evaluations/login.html'

    def get(self, request, report_type):
        """Function that make the teacher/s reports"""
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        if report_type == 'all_teachers_report':
            pass
        elif report_type == 'teacher_report':
            pass
        elif report_type == 'career_teachers_report':
            pass

        return redirect('monitoring/')

    def all_teachers_report(self, request):
        pass

    def teacher_report(self, request):
        template = 'evaluations/teachers_report.html'

        career_id = request.GET.get('career_id',''),
        teacher_id = request.GET.get('teacher_id','')
        data = {}

        career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
        teacher = EvaluationsTeachers.objects.get(idperson__exact=teacher_id)
        career_data = self.get_career_data(career)

        data[teacher] = self.get_teacher_signatures_results(
            career, career_data, teacher, exam=career_data['exams'][0])

        context = {
            'data': data,
        }

        return render_to_pdf_response(request, template, context)

    def career_teachers_report(self, request):
        template = 'evaluations/teachers_report.html'

        career_id = request.GET.get('career_id','')
        data = {}

        career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
        career_teachers = self.get_career_teachers(career)
        career_data = self.get_career_data(career)

        for teacher in career_teachers:
            data[teacher] = self.get_teacher_signatures_results(
                career, career_data, teacher, exam=career_data['exams'][0])

        context = {
            'data': data,
        }

        return render_to_pdf_response(request, template, context)
