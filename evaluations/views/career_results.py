from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import *
from .general_functions import *

import csv
import xlsxwriter


class CareerResultsView(View, GeneralFunctions):

    template_monitoring = 'evaluations/career_monitoring.html'
    template_login = 'evaluations/login.html'

    def get(self, request, career_id):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view
        coordinator = EvaluationsCoordinators.objects.get(
            idperson__exact=request.session['id_coordinator'])
        careers_id = EvaluationsDetailCoordinatorCareer.objects.filter(
            idcoordinator__exact=coordinator.idperson).values('idcareer')
        careers = EvaluationsCareers.objects.filter(idcareer__in=careers_id)

        career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
        career_data = self.get_career_data(career)
        
        # Getting teachers results
        # career_data = self.get_career_data(career)
        # teachers_signatures_results = self.get_teachers_signatures_results(
        #     career, career_data)
        # teachers_results = teachers_signatures_results
        
        teachers = self.get_career_teachers(career)

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
            career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
            careers = self.get_career_data(career)
            students = careers['students']['not_evaluated']

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=Alumnos_No_Evaluados_' + \
                str(career).capitalize() + '.csv'
            writer = csv.writer(response, csv.excel)
            response.write(u'\ufeff'.encode('utf8'))

            self.write_to_excel(students, career, writer)
            return response
