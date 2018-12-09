from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import EvaluationsStudent
from .general_functions import get_evaluations, get_evaluated_signatures, get_evaluations_and_evaluated, get_next_evaluation


class HomeView(View,):

    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'student':
            return render(request, self.template_login)

        # Values for the navigation bar
        student = EvaluationsStudent.objects.get(
            pk__exact=request.session['id_student'], status__exact="ACTIVE")
        evaluations = get_evaluations(student)
        evaluated_signatures = get_evaluated_signatures(
            student, evaluations)
        result_evaluations = get_evaluations_and_evaluated(
            evaluations, evaluated_signatures)

        next_evaluation = get_next_evaluation(
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
            'result_evaluations': result_evaluations,
        }
        return render(request, self.template_home, context)
