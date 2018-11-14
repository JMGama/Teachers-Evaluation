from django.shortcuts import render, redirect
from django.views import View
from easy_pdf.rendering import render_to_pdf_response
from .general_functions import *

class TeacherReports(View, GeneralFunctions):
    template_login = 'evaluations/login.html'

    def get(self, request, report_type):
        """Function that make the reports"""
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        if report_type == 'all_teachers_report':
            pass
        elif report_type =='all_teachers_report':
            pass
        elif report_type == 'teacher_report':
            pass
        elif report_type == 'career_teachers_report':
            pass

        return redirect('monitoring/')
