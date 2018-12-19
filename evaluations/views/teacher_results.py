import csv

import xlsxwriter
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from evaluations.models import (EvaluationsCareer, EvaluationsCoordinator,
                                EvaluationsDtlCoordinatorCareer,
                                EvaluationsDtlQuestionExam, EvaluationsExam,
                                EvaluationsSignatureQuestionResult,
                                EvaluationsSignatureResult, EvaluationsTeacher,
                                EvaluationsTeacherSignature)


class TeacherResultsView(View):

    template_teacher_results = 'evaluations/teacher_results.html'
    template_monitoring = 'evaluations/career_monitoring.html'
    template_login = 'evaluations/login.html'

    def get(self, request, career_id, teacher_id):

        # Verify if the coordinator is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view and the monitoring navigation bar.
        coordinator = EvaluationsCoordinator.objects.get(
            pk__exact=request.session['id_coordinator'])
        careers_id = EvaluationsDtlCoordinatorCareer.objects.filter(
            fk_coordinator__exact=coordinator.id).values('fk_career')
        careers = EvaluationsCareer.objects.filter(pk__in=careers_id)

        career = EvaluationsCareer.objects.get(
            pk__exact=career_id, status="ACTIVE")

        # Get the teacher.
        teacher = EvaluationsTeacher.objects.get(pk__exact=teacher_id)

        # Get the teacher signatures in the career.
        signatures = [signature_dtl.fk_signature for signature_dtl in EvaluationsTeacherSignature.objects.filter(
            fk_teacher=teacher.id,
            fk_signature__fk_career__exact=career.id,
            status="ACTIVE"
        ).select_related('fk_signature')]

        # Get the teacher results average of each exam.
        teacher_results = self.get_teacher_average_results(career, teacher)

        # Calculate the general average of the teacher from all the exams.
        general_average = []
        for exam in teacher_results:
            general_average.append(exam['average'])
        general_average = round(
            sum(general_average)/len(general_average) if len(general_average) > 0 else 0)

        # Render the teacher results view with all the things to show.
        context = {
            'results': teacher_results,
            'general_average': general_average,
            'signatures': signatures,
            'teacher': teacher,
            'coordinator': coordinator,
            'careers': careers,
            'career': career
        }

        return render(request, self.template_teacher_results, context)

    def get_teacher_average_results(self, career, teacher):
        """Returns a list with the average result of the signature, the questions results and comments in each exam of the career"""
        data = []

        # Get all the exams for the career.
        exams = EvaluationsExam.objects.filter(
            type__exact=career.type, status__exact='ACTIVE')

        # Get a list with all the teacher-signature detail of the teacher in that career.
        signatures_dtl = EvaluationsTeacherSignature.objects.filter(
            fk_teacher=teacher.id,
            fk_signature__fk_career__exact=career.id,
            status="ACTIVE"
        ).select_related('fk_signature')

        # Results for each exam of the career.
        for exam in exams:

            # Get the average of all the signatures.
            average = self.get_signatures_average(signatures_dtl, exam)

            # If the average is false (dosn't have evaluations) continue to the next exam.
            if not average:
                break

            # Get the averages of all the questions in the exam, for all the signatures.
            questions = self.get_signatures_questions_averages(
                signatures_dtl, exam)

            # Add the result of the exam to the return data.
            exam_results = {
                'exam': exam,
                'average': average,
                'questions': questions
            }
            data.append(exam_results)

        return data

    def get_signatures_average(self, signatures_dtl, exam):
        """Return the final average of the result signatures in the exam"""
        averages = []
        for dtl_signature in signatures_dtl:
            try:
                # Get the average of the signature.
                signature_average = EvaluationsSignatureResult.objects.get(
                    group__exact=dtl_signature.group,
                    fk_signature__exact=dtl_signature.fk_signature.id,
                    fk_exam__exact=exam.id,
                    status="ACTIVE"
                ).average
                averages.append(float(signature_average))
            except ObjectDoesNotExist:
                pass

        # Calculate the general average for the teacher.
        average = False
        if len(averages) > 0:
            average = round((sum(averages)/len(averages)))
        return average

    def get_signatures_questions_averages(self, signatures_dtl, exam):
        """Return a dictionary with the questions as the key and the average or comments as value. This will return a empty dict if there isn't any result for the exam"""

        # Get all the questions for the exam.
        questions = [question.fk_question for question in EvaluationsDtlQuestionExam.objects.filter(
            fk_exam=exam.id, status="ACTIVE").select_related('fk_question')]

        # Get the average for each question on each signature.
        data = {}
        for question in questions:

            # Get the average or comments of the question for each signature.
            question_result = []
            for dtl_signature in signatures_dtl:
                try:
                    result = EvaluationsSignatureQuestionResult.objects.get(
                        group__exact=dtl_signature.group,
                        fk_question__exact=question.id,
                        fk_signature__exact=dtl_signature.fk_signature.id,
                        fk_exam__exact=exam.id,
                    ).result
                    question_result.append(result)

                except ObjectDoesNotExist:
                    pass

            # If the question is optional calculate the final average in other case return all the comments.
            if len(question_result) > 0:
                if question.optional != "YES":
                    # Calculate the final average for the question with all the signature-question results and asign it to the result dict.
                    question_result = list(map(float, question_result))
                    average = round(
                        (sum(question_result)/len(question_result)))
                    data[question] = average
                else:
                    # Add all the comments of the signature in the result data.
                    data['comments'] = question_result

        return data
