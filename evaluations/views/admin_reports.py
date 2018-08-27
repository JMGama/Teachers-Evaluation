from django.views import View
from django.http import HttpResponse
from django.utils.encoding import smart_str
from evaluations.models import EvaluationsDetailCoordinatorCareer, EvaluationsCareers
from .general_functions import GeneralFunctions

import csv


class AdminReports(View, GeneralFunctions):

    def get(self, request):
        response = self.general_report(request)
        return response

    def general_report(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Resultados_Generales.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        general_data = self.get_general_data()

        titles = ['Total de alumnos', 'Alumnos evaluados',
                  'Respuestas SI', 'Respuestas NO', 'Total de respuestas']
        data_matrix = [general_data[key] for key in general_data]

        writer.writerow(
            ['', '', 'RESULTADOS GENERALES DE LA EVALUACION DOCENTE'])
        self.write_to_csv(
            writer, titles, data_matrix)
        writer.writerow([])  # write empty row
        writer.writerow([])  # write empty row

        careers_results = self.get_all_career_results(request)
        titles = ['Carrera', 'Alumnos no evaluados', 'Alumnos evaluados', 'Rrespuestas SI',
                  'Respuestas NO', 'Promedio alumnos', 'Promedio evaluaciones']

        writer.writerow(
            ['', '', 'RESULTADOS POR CARRERA DE LA EVALUACION DOCENTE'])
        self.write_to_csv(
            writer, titles, careers_results)

        return response

    def get_all_career_results(self, request):
        """
        Return all the final results from the career
        (career name, evaluated, not evaluated, yes and no answers, 
        average evaluated, average answers
        """

        careers_id = EvaluationsDetailCoordinatorCareer.objects.filter(
            idcoordinator__exact=request.session['id_coordinator']).values_list('idcareer', flat=True)
        all_careers_results = []

        for career_id in careers_id:
            career_results = []

            career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
            career_data = self.get_career_data(career)

            career_results.append(career.description)
            career_results.append(
                len(career_data['students']['not_evaluated']))
            career_results.append(len(career_data['students']['evaluated']))
            career_results.append(career_data['average_data']['yes'])
            career_results.append(career_data['average_data']['no'])
            career_results.append(
                career_results[2] / (career_results[1] + career_results[2]) * 100)
            career_results.append(career_data['average_data']['average'])

            all_careers_results.append(career_results)

        return all_careers_results

    def write_to_csv(self, writer, titles, data):
        """
        Writes into the CSV with the data that were past:
        titles: the titles of the rows that are going to be
        data_matrix: a matrix(list of lists) or a list with the information 
        that is going to be in each row, with the same order that the titles
        """
        writer.writerow([smart_str(u""+title) for title in titles])

        for values in data:
            if type(values) == (list or tuple):
                data_row = []
                for value in values:
                    data_row.append(smart_str(value))
                writer.writerow(data_row)
            else:
                writer.writerow(data)
                break
