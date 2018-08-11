from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q, Func, F
from easy_pdf.rendering import render_to_pdf_response
from evaluations.models import *
from .general_functions import *
import csv

class tech_report(View, GeneralFunctions):
    template_name  = 'evaluations/teach_report0.html'
    template_login = 'evaluations/login.html'
    exam = 1
#Ejecuta este conmando em marydb para aumentar el espacio en memoria del group concat
#SET session group_concat_max_len=15000;
#SET group_concat_max_len=15000;
    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)
        template = self.template_name
        coordinator = EvaluationsCoordinators.objects.get(idperson__exact=request.session['id_coordinator'])
        context = {
        'all': self.get_data(coordinator)
        }
        #return render_to_pdf_response(request,template,context)
        return render(request, template, context)

    def post(self, request):
        if request.POST['action'] == 'excel':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=rowData.csv'
            writer = csv.writer(response, csv.excel)
            response.write(u'\ufeff'.encode('utf8'))
            coordinator = EvaluationsCoordinators.objects.get(idperson__exact="5941")
            data=self.get_data(coordinator)
            self.write_to_excelAll(data, writer)
            return response

    def get_data(self, coordinator):
        data={}
        coordinator_careers = EvaluationsDetailCoordinatorCareer.objects.select_related(
        'idcareer').filter(idcoordinator__exact=coordinator.idperson)
        for career in coordinator_careers:
            career = career.idcareer
            career_data = self.get_career_data(career)
            teachers_signatures_results = self.get_teachers_signatures_results(career, career_data)
            data[career] = teachers_signatures_results
        return data
