from django.views import View
from django.http import HttpResponse
from django.utils.encoding import smart_str
from evaluations.models import EvaluationsDetailCoordinatorCareer, EvaluationsCareers
from .general_functions import GeneralFunctions

import csv


class AdminReports(View, GeneralFunctions):

    def get(self, request):
        pass

    def general_report(self, request):
        general_data = self.get_general_data()
        careers_results = self.get_all_career_results(request)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Resultados_Generales' + '.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        self.write_to_csv(
            writer, ['Evaluaciones Realizadas', 'Promedio General'], general_data)
        return response

    def get_all_career_results(self, request):
        careers_id = EvaluationsDetailCoordinatorCareer.objects.filter(
            idcoordinator__exact=request.session['id_coordinator']).values('idcareer')
        careers_results = {}
        for career_id in careers_id:
            career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
            career_data = self.get_career_data(career)
            careers_results[career.description] = career_data

        return careers_results
