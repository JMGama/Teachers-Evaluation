import csv

from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from evaluations.models import (EvaluationsCareer, EvaluationsCoordinator,
                                EvaluationsDtlCoordinatorCareer)


class MonitoringView(View):

    template_monitoring = 'evaluations/monitoring.html'
    template_login = 'evaluations/login.html'

    def get(self, request):

        # Verify if the coordinator is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view and the monitoring navigation bar.
        coordinator = EvaluationsCoordinator.objects.get(
            pk__exact=request.session['id_coordinator'])
        careers_id = EvaluationsDtlCoordinatorCareer.objects.filter(
            fk_coordinator__exact=coordinator.id).values('fk_career')
        careers = EvaluationsCareer.objects.filter(pk__in=careers_id)

        # Get the general result for all the evaluations.
        general_data = self.get_general_results()

        # Render the home view for the coordintators.
        context = {
            'coordinator': coordinator,
            'careers': careers,
            'general_data': general_data,
        }

        # If the  coordinator is admin, set it true in the context to show admin things (reports, actions, etc).
        if coordinator.type == 'ADMINS':
            context['admin_user'] = True

        return render(request, self.template_monitoring, context)

    def get_general_results(self):
        """Get the general results for all the evaluations"""
        data = {}
        with connection.cursor() as cursor:

            # Get the total of students in the database.
            cursor.execute(
                'SELECT COUNT(id) FROM evaluations_student WHERE status = "ACTIVE"')
            data['total_students'] = cursor.fetchone()[0]

            # Get the total of students evaluated.
            cursor.execute(
                'SELECT COUNT( DISTINCT ( D.fk_student ) ) FROM evaluations_signature_evaluated A JOIN evaluations_student_signature D ON A.fk_student_signature = D.id')
            data['students_evaluated'] = cursor.fetchone()[0]

            # Get the total of YES answer in not optional questions for the general average.
            cursor.execute(
                'SELECT COUNT(id) FROM evaluations_answer WHERE answer = "yes"')
            data['yes_answers'] = cursor.fetchone()[0]

            # Get the total of NO answer in not optional questions for the general average.
            cursor.execute(
                'SELECT COUNT(id) FROM evaluations_answer WHERE answer = "no"')
            data['no_answers'] = cursor.fetchone()[0]

        # Calculatate the total of answers in all the evaluations.
        data['total_answers'] = data['no_answers'] + data['yes_answers']
        return data
