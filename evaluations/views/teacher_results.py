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

        teacher_results = self.get_teacher_signatures_results(
            career, career_data, teacher)
        exams_averages, final_average = self.get_teacher_exams_averages(
            teacher_results)
        
        questions, questions_results, comments = self.get_exam_questions_results(teacher_results)

        context = {
            'final_average': final_average,
            'exams_averages': exams_averages,
            'teacher_results': teacher_results,
            'teacher': teacher,
            'coordinator': coordinator,
            'careers': careers,
            'career': career,
            'career_data': career_data,
            'questions': questions,
            'questions_results': questions_results,
            'comments': comments
        }

        return render(request, self.template_teacher_results, context)

    def get_teacher_exams_averages(self, teacher_results):
        exams_averages = {}
        final_average = []
        for exam, signatures in teacher_results.items():
            averages = []
            for results in signatures.values():
                averages.append(results['average'])
            evaluation_average = round(sum(averages)/len(averages), 2)
            exams_averages[exam] = {
                'averages': averages, 'evaluation_average': evaluation_average}
            final_average.append(evaluation_average)

        final_average = round(sum(final_average)/len(final_average), 2)
        return exams_averages, final_average

    def get_exam_questions_results(self, teacher_results):
        """Return a dict with the result of the question of each exam,
         a list with the questions and a list with all the comments of that career"""

        questions_results = {}
        questions = []
        comments = []
        
        for exam, signatures in teacher_results.items():
            for options in signatures.values():
                questions_info = {}
                for question, items in options['questions'].items():
                    # Add the questions, comments and questions results.
                    questions.append(question)
                    if 'average' in items:
                        questions_info[question]=items['average']
                    else: 
                        for comment in items['answers']:
                            comments.append(comment)
                questions_results[exam] = questions_info
        print(questions_results)
        return questions, questions_results, comments