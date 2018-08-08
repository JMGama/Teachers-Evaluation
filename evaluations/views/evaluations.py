from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import *
from .general_functions import *

class EvaluationView(View, GeneralFunctions):

    template_evaluation = 'evaluations/evaluation_form.html'
    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request, exam_id, signature):
        if not request.session.get('session', False) or not request.session['type'] == 'student':
            return render(request, self.template_login)

        # Values for the navigation bar
        student = EvaluationsStudents.objects.get(
            idperson=request.session['id_student'])
        evaluations = self.get_evaluations(student)
        evaluated_signatures = self.get_evaluated_signatures(
            student)

        # Values for the view
        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)

        signature_group = None
        for evaluation in evaluations:
            if str(evaluation['exam'].id) == str(exam_id):
                for group in evaluation['groups']:
                    if str(group.idsignature.id) == str(signature):
                        signature_group = group.idgroup

        detail_group = EvaluationsDetailGroupPeriodSignature.objects.get(
            idsignature__exact=signature, idgroup__exact=signature_group)

        context = {
            'student': student,
            'evaluations': evaluations,
            'evaluated_signatures': evaluated_signatures,
            'exam_questions': exam_questions,
            'detail_group': detail_group,
            'exam_id': exam_id,
            'signature': signature,
        }

        return render(request, self.template_evaluation, context)

    def post(self, request, exam_id, signature):
        # Verify if the user is correctly logged in
        if not request.session.get('session', False):
            return render(request, self.template_login)

        # Values for the navigation bar
        student = EvaluationsStudents.objects.get(
            idperson=request.session['id_student'])

        # Get exam questions
        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)

        # Submit every exam answer
        num_answers = 0
        for question in exam_questions:
            try:
                # verify if the question is optional or not
                try:
                    submitted_answer = request.POST['answer_' +
                                                    str(question.id)]
                except Exception as e:
                    submitted_answer = request.POST['answer_' +
                                                    str(question.id) + "_optional"]

                answer = EvaluationsAnswers(
                    idstudent=student,
                    idgroup=EvaluationsDetailStudentGroup.objects.get(
                        idstudent__exact=student.idperson, idsignature__exact=signature),
                    iddetailquestion=EvaluationsDetailExamQuestion.objects.get(
                        id__exact=question.id),
                    answer=submitted_answer.upper() if submitted_answer != "" else None,
                    idexam=EvaluationsExams.objects.get(id__exact=exam_id),
                )
                answer.save()
                num_answers += 1
            except Exception:
                pass

        # Validate all answers well submitted to the DB.
        if num_answers == len(exam_questions):
            # Change status to evaluated on the evaluations_detail_student_group table.
            evaluations = self.get_evaluations(student)
            signature_group = None
            for evaluation in evaluations:
                if str(evaluation['exam'].id) == str(exam_id):
                    for group in evaluation['groups']:
                        if str(group.idsignature.id) == str(signature):
                            signature_group = group.idgroup

            group_detail = EvaluationsDetailGroupPeriodSignature.objects.get(
                idsignature__exact=signature, idgroup__exact=signature_group)

            evaluated_signature = EvaluationsDetailStudentSignatureExam(
                idsignature=EvaluationsSignatures.objects.get(
                    id__exact=signature),
                idteacher=group_detail.idteacher,
                idperiod=group_detail.idperiod,
                idgroup=EvaluationsDetailStudentGroup.objects.get(
                    idsignature__exact=signature, idperiod__exact=group_detail.idperiod, idstudent__exact=student.idperson).id,
                idstudent=student,
                idexam=EvaluationsExams.objects.get(id__exact=exam_id),
                evaluated='YES',
                status='ACTIVO',
            )
            evaluated_signature.save()

            # Value for navigation bar
            evaluations = self.get_evaluations(student)
            evaluated_signatures = self.get_evaluated_signatures(
                student)
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
            return self.get(request, next_evaluation['exam'].id, next_evaluation['group'].idsignature.id)

        else:
            # Value for navigation bar
            evaluations = self.get_evaluations(student)
            evaluated_signatures = self.get_evaluated_signatures(
                student)

            signature_group = None
            for evaluation in evaluations:
                if str(evaluation['exam'].id) == str(exam_id):
                    for group in evaluation['groups']:
                        if str(group.idsignature.id) == str(signature):
                            signature_group = group.idgroup

            # Values for the view
            exam_questions = EvaluationsDetailExamQuestion.objects.filter(
                idexam__exact=exam_id)
            detail_group = EvaluationsDetailGroupPeriodSignature.objects.get(
                idsignature__exact=signature, idgroup__exact=signature_group)

            context = {
                'student': student,
                'evaluations': evaluations,
                'evaluated_signatures': evaluated_signatures,
                'exam_questions': exam_questions,
                'detail_group': detail_group,
                'exam_id': exam_id,
                'signature': signature,
                'message': ['Ocurrio un error al enviar la evaluacion.', 'red'],
            }
            return render(request, self.template_evaluation, context)
