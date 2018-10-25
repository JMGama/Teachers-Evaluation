from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from .general_functions import *


class TeacherEvaluationView(View, GeneralFunctions):

    template_teacher_evaluation = 'evaluations/teacher_evaluation.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'teacher':
            return render(request, self.template_login)

        teacher = EvaluationsTeachers.objects.get(
            idperson__exact=request.session['id_teacher'])
        signatures_detail = EvaluationsDetailGroupPeriodSignature.objects.filter(
            idteacher__exact=teacher.idperson)


        return HttpResponse("WELCOME TO THE TEACHERS VIEW")

    def get_teacher_eval_signatures(self, teacher):
        pass
