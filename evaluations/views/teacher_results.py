from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import *
from .general_functions import *

import csv
import xlsxwriter


class TeacherResultsView(View, GeneralFunctions):

    template_teacher_results = 'evaluations/teacher_results.html'
    template_monitoring = 'evaluations/career_monitoring.html'
    template_login = 'evaluations/login.html'

    def get(self, request, career_id, teacher_id):
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
        teacher = EvaluationsTeachers.objects.get(idperson__exact=teacher_id)


        context = {
            'teacher': teacher,
            'coordinator': coordinator,
            'careers': careers,
            'career': career,
            'career_data': career_data,
        }

        return render(request, self.template_teacher_results, context)