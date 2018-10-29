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
        teacher_exams = EvaluationsExams.objects.filter(
            Q(type='DOCENTES') & Q(status__exact='ACTIVO'))    
        signatures_detail = EvaluationsDetailGroupPeriodSignature.objects.filter(
            idteacher__exact=teacher.idperson)
        evaluated_signatures = self.get_teacher_eval_signatures(
            teacher, signatures_detail,teacher_exams)
        next_evaluation = self.get_teacher_next_eval_signature(
            signatures_detail, evaluated_signatures)

        if not next_evaluation:
            try:
                request.session.flush()
            except KeyError:
                pass
            context = {
                'student': teacher,
                'complete': 'YES',
            }
            return render(request, self.template_login, context)

        context = {
            'teacher': teacher,
            'teacher_exams': teacher_exams,
            'next_evaluation': next_evaluation,
            'signatures_detail': signatures_detail,
            'evaluated_signatures': evaluated_signatures,
        }
        return render(request, self.template_teacher_evaluation, context)

    def get_teacher_eval_signatures(self, teacher, signatures_detail, teacher_exams):
        """return a list of all the evaluations (groupid) already made by the teacher"""

        eval_exam_signatures = {}
        for exam in teacher_exams:
            eval_signatures = []
            for signature_dtl in signatures_detail:
                evaluated = EvaluationsDetailTeacherSignatureExam.objects.filter(
                    idexam__exact=exam, idgroup__exact=signature_dtl.idgroup, idsignature__exact=signature_dtl.idsignature)
                if evaluated:
                    eval_signatures.append(signature_dtl)
            eval_exam_signatures[exam] = eval_signatures
        return eval_exam_signatures

    def get_teacher_next_eval_signature(self, signatures, evaluated_signatures):
        """return the exam and group that is the next to evaluate (havent evaluated) for the teacher"""

        next_evaluation = {}
        for signature_dtl in signatures:
            if signature_dtl not in evaluated_signatures:
                next_evaluation = signature_dtl
        return next_evaluation
