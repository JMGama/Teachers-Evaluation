from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .general_functions import *


class TeacherEvaluationView(View, GeneralFunctions):
    template_evaluation = 'evaluations/teacher_evaluation_form.html'
    template_home = 'evaluations/teacher_home.html'
    template_login = 'evaluations/login.html'

    def get(self, request, exam_id, signature_dtl_id):
        """ Get the necesary values to show the formulary for the evaluation"""

        # Verify if the user is correctly logged in
        if not request.session.get('session', False) or not request.session['type'] == 'teacher':
            return render(request, self.template_login)

        # Values for the navigation bar
        teacher = EvaluationsTeachers.objects.get(
            idperson__exact=request.session['id_teacher'])
        teacher_exams = EvaluationsExams.objects.filter(
            Q(type='DOCENTE') & Q(status__exact='ACTIVO'))
        signatures_detail = EvaluationsDetailGroupPeriodSignature.objects.filter(
            idteacher__exact=teacher.idperson)
        evaluated_signatures = self.get_teacher_eval_signatures(
            teacher, signatures_detail, teacher_exams)

        # Values for the view
        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)
        signature_detail = EvaluationsDetailGroupPeriodSignature.objects.get(
            pk__exact=signature_dtl_id)

        context = {
            'teacher': teacher,
            'teacher_exams': teacher_exams,
            'signatures_detail': signatures_detail,
            'evaluated_signatures': evaluated_signatures,
            'signature_detail': signature_detail,
            'exam_questions': exam_questions
        }

        return render(request, self.template_evaluation, context)

    def post(self, request, exam_id, signature_dtl_id):
        """Make the full process to upload the answers of the evaluation that was finish"""

        # Verify if the user is correctly logged in
        if not request.session.get('session', False) or not request.session['type'] == 'teacher':
            return render(request, self.template_login)

        teacher = EvaluationsTeachers.objects.get(
            idperson__exact=request.session['id_teacher'])
        # Get exam questions
        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)

        # Submit anwsers for the evaluation
        self.submit_answers(request, teacher, exam_id,
                            signature_dtl_id, exam_questions)
        # Submit evaluation done
        self.finish_evaluation(request, teacher, exam_id, signature_dtl_id)

        # Values for the navigation bar
        teacher_exams = EvaluationsExams.objects.filter(
            Q(type='DOCENTES') & Q(status__exact='ACTIVO'))
        signatures_detail = EvaluationsDetailGroupPeriodSignature.objects.filter(
            idteacher__exact=teacher.idperson)
        evaluated_signatures = self.get_teacher_eval_signatures(
            teacher, signatures_detail, teacher_exams)
        next_evaluation = self.get_teacher_next_eval_signature(
            signatures_detail, evaluated_signatures, teacher_exams)

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

        return self.get(request, next_evaluation['exam'].id, next_evaluation['signature_dtl'].id)

    @transaction.atomic
    def submit_answers(self, request, teacher, exam_id, signature_dtl_id, exam_questions):
        """Creates a transaction to upload all the answers, if there is an error in one answers 
        it rise an exception and make a rollback in all the answers"""
        num_answers = 0
        for question_dtl in exam_questions:
            # Verify if the question is optional or not
            try:
                submitted_answer = request.POST['answer_' +
                                                str(question_dtl.idquestion.id)]
            except Exception:
                submitted_answer = request.POST['answer_' +
                                                str(question_dtl.idquestion.id) + "_optional"]
            answer = EvaluationsTeachersAnswers(
                idteacher=teacher,
                idteachersignaturedetail=EvaluationsDetailGroupPeriodSignature.objects.get(
                    pk__exact=signature_dtl_id),
                idquestion=question_dtl.idquestion,
                answer=submitted_answer.upper() if submitted_answer != "" else None,
                idexam=EvaluationsExams.objects.get(pk__exact=exam_id)
            )
            answer.save()
            num_answers += 1

        if num_answers != len(exam_questions):
            raise Exception('Error uploading all questions')

    def finish_evaluation(self, request, teacher, exam_id, signature_dtl_id):
        """saves the record in the Database, which says that the evaluation has completed successfully"""
        signature_dtl = EvaluationsDetailGroupPeriodSignature.objects.get(
            pk__exact=signature_dtl_id)

        evaluated_signature = EvaluationsDetailTeacherSignatureExam(
            idsignature=signature_dtl.idsignature,
            idteacher=teacher,
            idperiod=signature_dtl.idperiod,
            idgroup=signature_dtl.idgroup,
            idexam=EvaluationsExams.objects.get(pk__exact=exam_id),
            idcareer=signature_dtl.idsignature.idcareer,
            evaluated='YES',
            status='ACTIVO'
        )
        evaluated_signature.save()

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

    def get_teacher_next_eval_signature(self, signatures, evaluated_signatures, teacher_exams):
        """return the exam and group that is the next to evaluate (havent evaluated) for the teacher"""

        next_evaluation = {}
        for exam in teacher_exams:
            for signature_dtl in signatures:
                if signature_dtl not in evaluated_signatures[exam]:
                    next_evaluation['exam'] = exam
                    next_evaluation['signature_dtl'] = signature_dtl
                    return next_evaluation
