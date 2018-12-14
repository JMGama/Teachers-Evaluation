from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from evaluations.models import (EvaluationsAnswer, EvaluationsDtlQuestionExam,
                                EvaluationsExam, EvaluationsSignatureEvaluated,
                                EvaluationsSignatureQuestionResult,
                                EvaluationsSignatureResult, EvaluationsStudent,
                                EvaluationsStudentSignature,
                                EvaluationsTeacherSignature)

from .general_functions import (get_evaluated_signatures, get_evaluations,
                                get_evaluations_and_evaluated,
                                get_next_evaluation)


class EvaluationView(View,):

    template_evaluation = 'evaluations/evaluation_form.html'
    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request, exam_id, signature):
        """Get all the necesary information to show the evaluation form page, for the requested signature and exam."""

        # Verify if the student is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'student':
            return render(request, self.template_login)

        # Values for the navigation bar.
        student = EvaluationsStudent.objects.get(
            pk__exact=request.session['id_student'], status__exact="ACTIVE")
        evaluations = get_evaluations(student)
        evaluated_signatures = get_evaluated_signatures(
            student, evaluations)
        result_evaluations = get_evaluations_and_evaluated(
            evaluations, evaluated_signatures)

        # Values for the view.
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

    @transaction.atomic
    def post(self, request, exam_id, signature):
        """Submit the answers to the questions and add the info to the signature_evaluated table in the database."""

        # Verify if the student is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'student':
            return render(request, self.template_login)

        # Load data to be submitted.
        exam_questions = EvaluationsDtlQuestionExam.objects.filter(
            fk_exam__exact=exam_id, status__exact="ACTIVE").select_related('fk_question')
        student = EvaluationsStudent.objects.get(
            pk__exact=request.session['id_student'], status__exact="ACTIVE")
        exam = EvaluationsExam.objects.get(
            id__exact=exam_id, status__exact="ACTIVE")
        student_signature = EvaluationsStudentSignature.objects.get(
            fk_student__exact=student.id, fk_signature__exact=signature, status__exact="ACTIVE")

        # The final average and total no optional questions for the Signature_Result.
        signature_average_result = 0
        questions_no_optional = 0

        # Submit every exam answer and create or update the Signature_Question_Result info.
        for question_detail in exam_questions:
            question = question_detail.fk_question
            optional = False

            # Verify if the question is optional or not.
            try:
                submitted_answer = request.POST['answer_' +
                                                str(question.id)]
            except Exception:
                submitted_answer = request.POST['answer_' +
                                                str(question.id) + "_optional"]
                optional = True

            # Creates the data for the answer to be submitted in the database.
            answer = EvaluationsAnswer(
                answer=submitted_answer.upper() if submitted_answer != "" else None,
                fk_question=question,
                fk_exam=exam,
                fk_student_signature=student_signature
            )
            answer.save()

            # Load the Signature_Question_Result to be updated if the question is already in the database.
            try:
                signature_question_result = EvaluationsSignatureQuestionResult.objects.get(
                    group=student_signature.group,
                    fk_question=question.id,
                    fk_signature=student_signature.fk_signature.id,
                    fk_exam=exam.id,
                    status="ACTIVE"
                )

                # New values to be updated in the Signature_Question_Result.
                total_evaluated = float(
                    signature_question_result.total_evaluated)
                result = signature_question_result.result

                # If the answer isn't optional the result will be numeric.
                if not optional:

                    # Information to calculate the new result.
                    average = float(result)
                    total_yes = ((average*total_evaluated)/100)

                    # The result value will be the average with the actual result and total_evaluated.
                    if submitted_answer.upper() == 'YES':
                        total_evaluated += 1
                        total_yes += 1
                        result = ((total_yes)*100)/(total_evaluated)
                    else:
                        total_evaluated += 1
                        result = ((total_yes)*100)/(total_evaluated)

                    # Add the actual question average and increment total of no optional questions to the signature_average.
                    signature_average_result += result
                    questions_no_optional += 1

                # If the answer is optional will be comments.
                else:
                    # If the comment is empty leave it that way, else append a pipe at the end to separate from other comments.
                    total_evaluated += 1
                    result += submitted_answer.upper() + " | " if submitted_answer != "" else ""

                # Update the Signature_Question_Result info with the new answer.
                signature_question_result.total_evaluated = total_evaluated
                signature_question_result.result = result
                signature_question_result.save()

            # If the question isn't in the Signature_Question_Result table, creates it and submit to the database.
            except ObjectDoesNotExist:
                result = ""

                # If the answer isn't optional the result will be numeric.
                if not optional:

                    # If the submitted answer is YES then it will be 100 else 0 because its the first tiem in the database.
                    if submitted_answer.upper() == 'YES':
                        result = 100
                    else:
                        result = 0

                    # Add the actual question average and increment total of no optional questions to the signature_average.
                    signature_average_result += result
                    questions_no_optional += 1

                # If the answer is optional will be comments.
                else:
                    # If the comment is empty leave it that way, else append a pipe at the end to separate from other comments.
                    result = submitted_answer.upper() + " | " if submitted_answer != "" else ""

                # Add the Signature_Question_Result to the database.
                signature_question_result = EvaluationsSignatureQuestionResult(
                    group=student_signature.group,
                    result=result,
                    total_evaluated=1,
                    fk_question=question,
                    fk_signature=student_signature.fk_signature,
                    fk_exam=exam,
                )
                signature_question_result.save()

        # Load the Signature_Result to be updated if the question is already in the database.
        try:
            signature_result = EvaluationsSignatureResult.objects.get(
                group=student_signature.group,
                fk_signature=student_signature.fk_signature.id,
                fk_exam=exam,
                status='ACTIVE'
            )

            # Get the average for the signature result.
            average = (signature_average_result/questions_no_optional)

            # Asign the new values to the Signature_Result and submit it to the database.
            signature_result.average = average
            signature_result.total_evaluated += 1
            signature_result.save()

        # If the signature isn't in the Signature_Result table, creates it and submit to the database.
        except ObjectDoesNotExist:

            # Get the average for the signature result.
            average = (signature_average_result/questions_no_optional)

            # Creates the Signature_Result with the asigned values and creates in on the database.
            signature_result = EvaluationsSignatureResult(
                group=student_signature.group,
                average=average,
                total_evaluated=1,
                fk_signature=student_signature.fk_signature,
                fk_exam=exam
            )
            signature_result.save()

        # Add the evaluation info to the Signature_evaluated table in the database so it appears as evaluated.
        signature_evaluated = EvaluationsSignatureEvaluated(
            evaluated='YES',
            fk_exam=exam,
            fk_student_signature=student_signature
        )
        signature_evaluated.save()

        # Load the Values fto redirect for the next evaluation.
        student = EvaluationsStudent.objects.get(
            pk__exact=request.session['id_student'], status__exact="ACTIVE")
        evaluations = get_evaluations(student)
        evaluated_signatures = get_evaluated_signatures(
            student, evaluations)
        next_evaluation = get_next_evaluation(
            student, evaluations, evaluated_signatures)

        # If there is not next evaluation, close the session ant return to the login page.
        if not next_evaluation:
            request.session.flush()
            context = {
                'student': student,
                'complete': 'YES',
            }
            return render(request, self.template_login, context)

        # Redirects to the get function with the next exam and signature to be done.
        return self.get(request, next_evaluation['exam'].id, next_evaluation['group'].fk_signature.id)
