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
        evaluated_signatures = self.get_teacher_eval_signatures(
            teacher, signatures_detail)
        print(evaluated_signatures)
        return HttpResponse("WELCOME TO THE TEACHERS VIEW")

    def get_teacher_eval_signatures(self, teacher, signatures_detail):
        """return a list of all the evaluations (groupid) already made by the teacher"""
        teacher_exams = EvaluationsExams.objects.filter(
            Q(type='DOCENTES') & Q(status__exact='ACTIVO'))

        result = {}
        for exam in teacher_exams:
            eval_signatures = []
            for signature_dtl in signatures_detail:
                eval_signatures.append(EvaluationsDetailTeacherSignatureExam.objects.filter(
                    idexam__exact=exam, idgroup__exact=signature_dtl.idgroup, idsignature__exact=signature_dtl.idsignature))
            result[exam]= eval_signatures
        return result
