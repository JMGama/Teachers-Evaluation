from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import EvaluationsStudent, EvaluationsDtlQuestionExam, EvaluationsTeacherSignature, EvaluationsAnswer, EvaluationsExam, EvaluationsStudentSignature, EvaluationsSignatureEvaluated
from .general_functions import get_evaluations, get_evaluated_signatures, get_evaluations_and_evaluated


class EvaluationView(View,):

    template_evaluation = 'evaluations/evaluation_form.html'
    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request, exam_id, signature):
        """Get all the necesary information to show the evaluation form page, for the requested signature and exam"""

        # Verify if the student is correctly logged in
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

        # Values for the view
        exam_questions = EvaluationsDtlQuestionExam.objects.filter(
            fk_exam__exact=exam_id, status__exact="ACTIVE")

        # Get the group of the student in the signature for the given exam.
        signature_group = None
        for exam in evaluations:
            if str(exam['exam'].id) == str(exam_id):
                for signature_student in exam['groups']:
                    if str(signature_student.fk_signature.id) == str(signature):
                        signature_group = signature_student.group

        teacher_signature = EvaluationsTeacherSignature.objects.get(
            fk_signature__exact=signature, group__exact=signature_group, status__exact="ACTIVE")

        # Render the evaluation form page passing the evaluation data.
        context = {
            'student': student,
            'exam_questions': exam_questions,
            'result_evaluations': result_evaluations,
            'teacher_signature': teacher_signature,
            'exam_id': exam_id,
            'signature': signature,
        }
        return render(request, self.template_evaluation, context)

    # def post(self, request, exam_id, signature):
    #     """Submit the answers to the questions and add the info to the signature_evaluated table in the Data Base"""

    #     # Verify if the student is correctly logged in
    #     if not request.session.get('session', False) or not request.session['type'] == 'student':
    #         return render(request, self.template_login)

    #     # Load data to be submitted
    #     exam_questions = EvaluationsDtlQuestionExam.objects.filter(
    #         fk_exam__exact=exam_id, status__exact="ACTIVE").select_related('fk_question')
    #     student = EvaluationsStudent.objects.get(
    #         pk__exact=request.session['id_student'])
    #     exam = EvaluationsExam.objects.get(id__exact=exam_id)
    #     student_signature = EvaluationsStudentSignature.objects.get(
    #         fk_student__exact=student.id, fk_signature__exact=signature)

    #     # Submit every exam answer
    #     for question_detail in exam_questions:
    #         question = question_detail.fk_question

    #         # Verify if the question is optional or not
    #         try:
    #             submitted_answer = request.POST['answer_' +
    #                                             str(question.id)]
    #         except Exception:
    #             submitted_answer = request.POST['answer_' +
    #                                             str(question.id) + "_optional"]

    #         # Creates the data for the answer to be submitted
    #         answer = EvaluationsAnswer(
    #             answer=submitted_answer.upper() if submitted_answer != "" else None,
    #             fk_question=question.fk_question,
    #             fk_exam=exam,
    #             fk_student_signature=student_signature)
    #         answer.save()

    #     # Add the evaluation to the Signature_evaluated table so it appears as an evaluated signatures in the view.
    #     signature_evaluated = EvaluationsSignatureEvaluated(
    #         evaluated='YES',
    #         fk_exam=exam,
    #         fk_student_signature=student_signature
    #     )
    #     signature_evaluated.save()

    #     return self.get(request, exam_id, signature)
    #     # Validate all answers well submitted to the DB.
    #     if num_answers == len(exam_questions):
    #         # Change status to evaluated on the evaluations_detail_student_group table.
    #         evaluations = self.get_evaluations(student)
    #         signature_group = None
    #         for evaluation in evaluations:
    #             if str(evaluation['exam'].id) == str(exam_id):
    #                 for group in evaluation['groups']:
    #                     if str(group.idsignature.id) == str(signature):
    #                         signature_group = group.idgroup

    #         group_detail = EvaluationsDetailGroupPeriodSignature.objects.get(
    #             idsignature__exact=signature, idgroup__exact=signature_group)

    #         evaluated_signature = EvaluationsDetailStudentSignatureExam(
    #             idsignature=EvaluationsSignatures.objects.get(
    #                 id__exact=signature),
    #             idteacher=group_detail.idteacher,
    #             idperiod=group_detail.idperiod,
    #             idgroup=EvaluationsDetailStudentGroup.objects.get(
    #                 idsignature__exact=signature, idperiod__exact=group_detail.idperiod, idstudent__exact=student.idperson).id,
    #             idstudent=student,
    #             idexam=EvaluationsExams.objects.get(id__exact=exam_id),
    #             evaluated='YES',
    #             status='ACTIVO',
    #         )
    #         evaluated_signature.save()

    #         # Value for navigation bar
    #         evaluations = self.get_evaluations(student)
    #         evaluated_signatures = self.get_evaluated_signatures(
    #             student)
    #         next_evaluation = self.get_next_evaluation(
    #             student, evaluations, evaluated_signatures)

    #         if not next_evaluation:
    #             try:
    #                 request.session.flush()
    #             except KeyError:
    #                 pass
    #             context = {
    #                 'student': student,
    #                 'complete': 'YES',
    #             }
    #             return render(request, self.template_login, context)
    #         return self.get(request, next_evaluation['exam'].id, next_evaluation['group'].idsignature.id)

    #     else:
    #         # Value for navigation bar
    #         evaluations = self.get_evaluations(student)
    #         evaluated_signatures = self.get_evaluated_signatures(
    #             student)

    #         signature_group = None
    #         for evaluation in evaluations:
    #             if str(evaluation['exam'].id) == str(exam_id):
    #                 for group in evaluation['groups']:
    #                     if str(group.idsignature.id) == str(signature):
    #                         signature_group = group.idgroup

    #         # Values for the view
    #         exam_questions = EvaluationsDetailExamQuestion.objects.filter(
    #             idexam__exact=exam_id)
    #         detail_group = EvaluationsDetailGroupPeriodSignature.objects.get(
    #             idsignature__exact=signature, idgroup__exact=signature_group)

    #         context = {
    #             'student': student,
    #             'evaluations': evaluations,
    #             'evaluated_signatures': evaluated_signatures,
    #             'exam_questions': exam_questions,
    #             'detail_group': detail_group,
    #             'exam_id': exam_id,
    #             'signature': signature,
    #             'message': ['Ocurrio un error al enviar la evaluacion.', 'red'],
    #         }
    #         return render(request, self.template_evaluation, context)
