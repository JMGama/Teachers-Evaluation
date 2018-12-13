from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from evaluations.models import EvaluationsStudent

from .general_functions import (get_evaluated_signatures, get_evaluations,
                                get_evaluations_and_evaluated,
                                get_next_evaluation)


class HomeView(View,):

    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        """Load the information of the student for the evaluations home page."""
        
        # Verify if the student is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'student':
            return render(request, self.template_login)

        # Load the Values for the navigation bar.
        student = EvaluationsStudent.objects.get(
            pk__exact=request.session['id_student'], status__exact="ACTIVE")
        evaluations = get_evaluations(student)
        evaluated_signatures = get_evaluated_signatures(
            student, evaluations)
        result_evaluations = get_evaluations_and_evaluated(
            evaluations, evaluated_signatures)

        # Get the next evaluation to be made for the student.
        next_evaluation = get_next_evaluation(
            student, evaluations, evaluated_signatures)

        # If there is not next evaluation, close the session ant return to the login page.
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

        # Render the home page.
        context = {
            'student': student,
            'next_evaluation': next_evaluation,
            'result_evaluations': result_evaluations,
        }
        return render(request, self.template_home, context)
