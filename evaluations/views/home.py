from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import *
from .general_functions import *

class HomeView(View, GeneralFunctions):

    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False):
            return render(request, self.template_login)

        # Values for the navigation bar
        student = EvaluationsStudents.objects.get(
            idperson=request.session['id_student'])
        evaluations = self.get_evaluations(student)
        evaluated_signatures = self.get_evaluated_signatures(student)
        next_evaluation = self.get_next_evaluation(
            student, evaluations, evaluated_signatures)

        if not next_evaluation:
            try:
                request.session.flush()
            except KeyError:
                pass
            context = {
                'student': student,
                'complete': 'YES',
            }
            return render(request, self.template_login, context)

        context = {
            'student': student,
            'next_evaluation': next_evaluation,
            'evaluations': evaluations,
            'evaluated_signatures': evaluated_signatures,
        }
        return render(request, self.template_home, context)
