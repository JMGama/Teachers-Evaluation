import csv

from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.views import View

from evaluations.models import (EvaluationsCareer, EvaluationsDtlQuestionExam,
                                EvaluationsExam, EvaluationsSignature,
                                EvaluationsSignatureQuestionResult,
                                EvaluationsSignatureResult, EvaluationsTeacher,
                                EvaluationsTeacherSignature)


class AdminReportsView(View):

    def get(self, request, career_type):
        """Creates the CSV with all the results of the teachers for each exam and signatures that are active"""

        # Create the response that will be a download of the CSV with the information.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Resultados_Generales.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        # Get all the active exams to get their results.
        exams = EvaluationsExam.objects.filter(
            type=career_type.upper(), status="ACTIVE")
        exams_resuts = []
        for exam in exams:

            # For each exam get the results of the teachers in the careers.
            results = self.get_career_teachers_results(
                career_type.upper(), exam)
            exams_resuts.append({
                'exam': exam,
                'results': results
            })

        # Wtire all the results in the CVS.
        self.write_exam_results(exams_resuts, writer)
        return response

    def write_exam_results(self, exams_resutls, writer):
        """Write all the exam results information to the CSV (writer received)"""

        # Get the results for each exam.
        for exam in exams_resutls:

            # Add the titles to the CSV.
            writer.writerow([smart_str(u""+exam['exam'].description)])
            questions = EvaluationsDtlQuestionExam.objects.filter(
                fk_exam__exact=exam['exam'].id, status="ACTIVE")
            titles = [
                'CARRERA',
                'MATERIA',
                'DOCENTE',
                'GRUPO',
                'TOTAL ALUMNOS EVALUADOS',
                'PROMEDIO'
            ]

            # Get the questions for the exam, to add them to the titles in the CVS.
            for question in questions:
                titles.append('P' + str(question.id))
            writer.writerow([smart_str(u""+title) for title in titles])

            # Get the results for each career in the exam.
            for career in exam['results']:

                # Get the results for the signature/teacher.
                for signature in career['signatures_results']:

                    # This is the things that will be writed in the same line of the CVS.
                    to_write = [
                        smart_str(u""+career['career']),
                        smart_str(u""+signature['signature']),
                        smart_str(u""+signature['teacher']),
                        smart_str(u""+signature['group']),
                        smart_str(u""+str(signature['total_evaluated'])),
                        smart_str(u""+signature['average'])
                    ]

                    # Get the results for each question on the exam in the actual career.
                    for question in signature['questions']:
                        for _, question_result in question.items():
                            to_write.append(
                                smart_str(u""+str(question_result)))

                    # Write the information of the signature in the CVS.
                    writer.writerow(to_write)
        return True

    def get_career_teachers_results(self, careers_type, exam):
        results = []

        # Get all the careers of that type (semestral or cuatrimestral).
        careers = EvaluationsCareer.objects.filter(
            type__exact=careers_type, status="ACTIVE")

        # Get the results for the signatures in each of the careers.
        for career in careers:
            career_resutls = {
                'career': career.description,
                'signatures_results': []
            }
            # Get all the sinatures for that career.
            career_signatures = EvaluationsSignature.objects.filter(
                fk_career__exact=career.id, status="ACTIVE")

            # Get the results for each signature in the career.
            for signature in career_signatures:
                signature_data = {}

                # Get the signature result(s).
                signature_results = EvaluationsSignatureResult.objects.filter(
                    fk_signature__exact=signature.id, fk_exam__exact=exam.id, status="ACTIVE")

                # Get the teacher(s) for the signature results, (multiple teachers in case the signature is given by different teacher in different gruops).
                for signature_result in signature_results:
                    teacher = EvaluationsTeacherSignature.objects.get(
                        fk_signature__exact=signature_result.fk_signature,
                        group__exact=signature_result.group,
                        fk_period__exact=exam.fk_period,
                        status="ACTIVE",
                    ).fk_teacher

                    # Get the questions reuslts.
                    signature_questions_results = EvaluationsSignatureQuestionResult.objects.filter(
                        fk_signature__exact=signature.id,
                        fk_exam__exact=exam,
                        group__exact=signature_result.group,
                        status="ACTIVE"
                    ).select_related('fk_question')

                    # Add the results to the signature data dictionary.
                    signature_data['signature'] = signature.description
                    signature_data['teacher'] = teacher.name + ' ' + \
                        teacher.last_name + ' ' + teacher.last_name_2
                    signature_data['group'] = signature_result.group
                    signature_data['average'] = signature_result.average
                    signature_data['total_evaluated'] = signature_result.total_evaluated
                    signature_data['questions'] = [
                        {question_res.fk_question.id: question_res.result}for question_res in signature_questions_results]
                    career_resutls['signatures_results'].append(signature_data)

            # Add the career results to the final dictionary.
            results.append(career_resutls)

        return results
