from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import *
from .general_functions import *

import csv


class MonitoringView(View, GeneralFunctions):

    template_monitoring = 'evaluations/monitoring.html'
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

        general_data = self.get_general_data()
        context = {
            'coordinator': coordinator,
            'careers': careers,
            'general_data': general_data,
        }

        if coordinator.type == 'ADMINISTRATIVO':
            context['admin_user'] = True

        return render(request, self.template_monitoring, context)

    def post(self, request):
        if request.POST['action'] == 'excel':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=Alumnos_No_Evaluados.csv'
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
