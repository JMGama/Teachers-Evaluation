from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from evaluations.models import (EvaluationsExam, EvaluationsTeacher,
                                EvaluationsTeacherSignature,
                                EvaluationsTeacherSignatureEvaluated)


class TeacherHomeView(View):

    template_teacher_evaluation = 'evaluations/teacher_home.html'
    template_login = 'evaluations/login.html'

    def get(self, request):

        # Verify if the user loggedin is a teacher, if it isn't return him to the login page.
        if not request.session.get('session', False) or not request.session['type'] == 'teacher':
            return render(request, self.template_login)

        # Get the information for the teacher that is going to make the evaluation.
        teacher = EvaluationsTeacher.objects.get(
            pk__exact=request.session['id_teacher'], status='ACTIVE')
        teacher_exams = EvaluationsExam.objects.filter(
            type__exact='DOCENTE', status='ACTIVE')

        # Get the signatures information to be evaluated for each exam.
        signatures_detail = []
        for exam in teacher_exams:
            signatures_dtl = EvaluationsTeacherSignature.objects.filter(
                fk_teacher__exact=teacher.id, fk_period__exact=exam.fk_period)
            signatures_detail.append(
                {'exam': exam, 'signatures_dtl': signatures_dtl})

        # Get the evaluations already made.
        evaluated_signatures = self.get_teacher_signatures_evaluated(
            teacher, teacher_exams)

        # Return the next evaluation to be made for the teacher in the exams.
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
            'exams_signatures': signatures_detail,
            'next_evaluation': next_evaluation,
            'evaluated_signatures': evaluated_signatures,
        }
        return render(request, self.template_teacher_evaluation, context)

    def get_teacher_signatures_evaluated(self, teacher, exams):
        """Return the exam an the signatures already evaluated for that exam"""
        data = []

        # Get the signatures evaluated for each exam.
        for exam in exams:
            signatures_evaluated = EvaluationsTeacherSignatureEvaluated.objects.filter(
                fk_exam__exact=exam.id, status='ACTIVO')
            data.append({'exam': exam,
                         'signatures_evaluated': signatures_evaluated})

        return data

    def get_teacher_next_eval_signature(self, signatures, evaluated_signatures):
        """return the exam and group that is the next to evaluate (havent evaluated) for the teacher"""

        next_evaluation = {}

        for exam_signatures in signatures:
            for exam_signatures_eval in evaluated_signatures:
                if exam_signatures['exam'] == exam_signatures_eval['exam']:
                    for signature in exam_signatures['signatures_dtl']:
                        if not signature in exam_signatures_eval['signatures_evaluated']:
                            return {'exam': exam_signatures['exam'], 'signature_dtl': signature}

        return next_evaluation
