from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from evaluations.models import (EvaluationsExam, EvaluationsTeacher,
                                EvaluationsTeacherSignature,
                                EvaluationsTeacherSignatureEvaluated, EvaluationsDtlQuestionExam, EvaluationsTeacherSignatureQuestionResult)


class TeacherEvaluationView(View):
    template_evaluation = 'evaluations/teacher_evaluation_form.html'
    template_home = 'evaluations/teacher_home.html'
    template_login = 'evaluations/login.html'

    def get(self, request, exam_id, signature_dtl_id):
        """ Get the necesary values to show the formulary for the evaluation"""

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
                fk_teacher__exact=teacher.id, fk_period__exact=exam.fk_period, status='ACTIVE')
            signatures_detail.append(
                {'exam': exam, 'signatures_dtl': signatures_dtl})

        # Get the evaluations already made.
        evaluated_signatures = self.get_teacher_signatures_evaluated(
            teacher, teacher_exams)

        # Values for the view
        exam_questions = EvaluationsDtlQuestionExam.objects.filter(
            fk_exam__exact=exam_id, status='ACTIVE')
        signature_detail = EvaluationsTeacherSignature.objects.get(
            pk__exact=signature_dtl_id, status='ACTIVE')
        
        context = {
            'teacher': teacher,
            'exams_signatures': signatures_detail,
            'evaluated_signatures': evaluated_signatures,
            'signature_detail': signature_detail,
            'exam_questions': exam_questions,
            'exam_id':exam_id,
            'signature_dtl_id':signature_dtl_id
        }

        return render(request, self.template_evaluation, context)

    def post(self, request, exam_id, signature_dtl_id):
        """Make the full process to upload the answers of the evaluation that was finish"""

        # Verify if the user loggedin is a teacher, if it isn't return him to the login page.
        if not request.session.get('session', False) or not request.session['type'] == 'teacher':
            return render(request, self.template_login)

        # Get the information for the teacher that is going to submit the evaluation.
        teacher = EvaluationsTeacher.objects.get(
            pk__exact=request.session['id_teacher'], status='ACTIVE')

        # Get the exam and signature detail evaluated.
        exam = EvaluationsExam.objects.get(pk__exact=exam_id, status='ACTIVE')
        signature_dtl = EvaluationsTeacherSignature.objects.get(
            pk__exact=signature_dtl_id, status='ACTIVE')

        # Submit the results of the evaluation to the Database.
        self.submit_results(request, exam, signature_dtl, teacher)

        # Get the exams for the teacher.
        teacher_exams = EvaluationsExam.objects.filter(
            type__exact='DOCENTE', status='ACTIVE')

        # Get the signatures information to be evaluated for each exam.
        signatures_detail = []
        for exam in teacher_exams:
            signatures_dtl = EvaluationsTeacherSignature.objects.filter(
                fk_teacher__exact=teacher.id, fk_period__exact=exam.fk_period, status='ACTIVE')
            signatures_detail.append(
                {'exam': exam, 'signatures_dtl': signatures_dtl})

        # Get the evaluations already made.
        evaluated_signatures = self.get_teacher_signatures_evaluated(
            teacher, teacher_exams)

        # Return the next evaluation to be made for the teacher in the exams.
        next_evaluation = self.get_teacher_next_eval_signature(
            signatures_detail, evaluated_signatures)

        # Exit if there is no more evaluations
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
        print('salida post:',next_evaluation['signature_dtl'].id)
        return self.get(request, next_evaluation['exam'].id, next_evaluation['signature_dtl'].id)

    @transaction.atomic
    def submit_results(self, request, exam, signature_dtl, teacher):
        """Submit to the database the results of the valuation made by the teacher"""

        # Get the exam questions.
        exam_questions = EvaluationsDtlQuestionExam.objects.filter(
            fk_exam__exact=exam.id, status='ACTIVE')

        # Submit tto the database the result of each question in the evaluation.
        for question_dtl in exam_questions:

            # Verify if the question is optional or not
            try:
                submitted_answer = request.POST['answer_' +
                                                str(question_dtl.fk_question.id)]
            except Exception:
                submitted_answer = request.POST['answer_' +
                                                str(question_dtl.fk_question.id) + "_optional"]

            # Fill the question result with the evaluation information and the result subbmited of that question, then save to DB.
            question_result = EvaluationsTeacherSignatureQuestionResult(
                group=signature_dtl.group,
                result=submitted_answer,
                fk_question=question_dtl.fk_question,
                fk_teacher=teacher,
                fk_signature=signature_dtl.fk_signature,
                fk_exam=exam
            )
            question_result.save()

        # Add the signature to the evaluated table in the database.
        signature_evaluated = EvaluationsTeacherSignatureEvaluated(
            evaluated='YES',
            fk_exam=exam,
            fk_teacher_signature=signature_dtl
        )
        signature_evaluated.save()

    def get_teacher_signatures_evaluated(self, teacher, exams):
        """Return the exam an the signatures already evaluated for that exam"""
        data = []

        # Get the signatures evaluated for each exam.
        for exam in exams:
            teacher_signatures = []
            signatures_evaluated = EvaluationsTeacherSignatureEvaluated.objects.filter(
                fk_exam__exact=exam.id, fk_teacher_signature__fk_teacher=teacher.id, status='ACTIVE')

            for teacher_signature in signatures_evaluated:
                teacher_signatures.append(teacher_signature.fk_teacher_signature)

            data.append({'exam': exam,
                            'signatures_evaluated': teacher_signatures})
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