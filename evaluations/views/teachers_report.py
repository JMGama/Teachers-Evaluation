from django.shortcuts import render
from django.views import View
from easy_pdf.rendering import render_to_pdf_response
from .general_functions import *


class TeachersReport(View, GeneralFunctions):
    template_name = 'evaluations/teachers_report.html'
    template_login = 'evaluations/login.html'

    def get(self, request, career_id):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)
        template = self.template_name

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
