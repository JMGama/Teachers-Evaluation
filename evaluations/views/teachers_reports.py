import csv

from django.shortcuts import HttpResponse, redirect, render
from django.utils.encoding import smart_str
from django.views import View
from easy_pdf.rendering import render_to_pdf_response

from evaluations.models import (EvaluationsCareer, EvaluationsCoordinator,
                                EvaluationsDtlCoordinatorCareer,
                                EvaluationsDtlQuestionExam, EvaluationsExam,
                                EvaluationsSignature,
                                EvaluationsSignatureQuestionResult,
                                EvaluationsSignatureResult, EvaluationsTeacher,
                                EvaluationsTeacherSignature)


class TeachersReportsView(View):
    template_login = 'evaluations/login.html'

    def get(self, request, report_type):
        """Function that make the teacher/s reports"""

        # Verify if the coordinator is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        template = ''
        context = {}

        # Depending the option given return de requested reports.
        if report_type == 'teacher_report':
            template, context = self.teacher_report(request)
        elif report_type == 'career_teachers_report':
            template, context = self.career_teachers_report(request)
        elif report_type == 'career_teachers_excel':
            return self.career_teachers_excel(request)

        # If there is a great request render the PDF's, otheway redirect to the reports view.
        if template and context:
            return render_to_pdf_response(request, template, context)

        return redirect('/evaluations/career_results/32/47740/#reportes')

    def teacher_report(self, request):
        template = 'evaluations/teachers_report.html'

        # Get the teacher and the career to get his results.
        teacher_id = request.GET.get('teacher_id', '')
        career_id = request.GET.get('career_id', '')
        career = EvaluationsCareer.objects.get(
            pk__exact=career_id, status="ACTIVE")
        teacher = EvaluationsTeacher.objects.get(
            pk__exact=teacher_id, status="ACTIVE")

        # Get the results of the teacher for each exam in the given career.
        data = self.get_teacher_career_results(teacher, career)

        # Send the results to the template to render the PDF's.
        context = {
            'data': data,
        }
        return template, context

    def career_teachers_report(self, request):
        template = 'evaluations/teachers_report.html'

        # Get the career to be processed their results.
        career_id = request.GET.get('career_id', '')
        career = EvaluationsCareer.objects.get(pk__exact=career_id)

        # Get the results for each esignature of the carrer en each exam.
        data = self.get_career_results(career)

        # Send the results to the template to render the PDF's.
        context = {
            'data': data
        }
        return template, context

    def career_teachers_excel(self, request):
        """Render a PDF with the career signatures results with their teachers, 
        this is the deliverable document for the teacher"""

        # Get the career to be processed their results.
        career_id = request.GET.get('career_id', '')
        career = EvaluationsCareer.objects.get(pk__exact=career_id)

        # Get the results for each esignature of the carrer en each exam.
        data = self.get_career_results(career)

        # Generates the CSV with the results of the career,then return as downloadable file.
        response = self.get_teacher_results_excel(data)
        return response

    def get_career_results(self, career):
        data = []

        # Get the active exams for the career.
        exams = EvaluationsExam.objects.filter(
            type__exact=career.type, status="ACTIVE")

        # Get the signatures of the career.
        signatures = EvaluationsSignature.objects.filter(
            fk_career__exact=career.id, status="ACTIVE")

        # Get the results for each signature in each exam:
        for exam in exams:
            signatures_resutls = []
            for signature in signatures:

                # Get the results of the signature.
                # If the signature have multiple results, it mean there are different groups in the signature.
                signature_results_dtl = EvaluationsSignatureResult.objects.filter(
                    fk_signature=signature.id,
                    status="ACTIVE"
                )

                # Get the results for each signature group.
                for signature_dtl in signature_results_dtl:

                    # Get the signature questions results.
                    questions_results = EvaluationsSignatureQuestionResult.objects.filter(
                        group=signature_dtl.group,
                        fk_signature=signature_dtl.fk_signature.id,
                        fk_exam=exam.id,
                        fk_question__optional='NO',
                        status="ACTIVE"
                    ).values_list('fk_question__description', 'result')

                    # Get the comments of the signature/group.
                    comments_result = EvaluationsSignatureQuestionResult.objects.get(
                        group=signature_dtl.group,
                        fk_signature=signature_dtl.fk_signature.id,
                        fk_exam=exam.id,
                        fk_question__optional='YES',
                        status="ACTIVE"
                    ).result

                    # Split the comments and add them to a list, only the ones that are not empty.
                    comments = list(filter(None, comments_result.split('|')))

                    # Get the teacher that gives the signature to that group.
                    teacher = EvaluationsTeacherSignature.objects.get(
                        fk_signature__exact=signature_dtl.fk_signature.id,
                        fk_period__exact=exam.fk_period
                    ).fk_teacher

                    # Add the signature results.
                    signature_results = {
                        'signature': signature_dtl.fk_signature.description,
                        'teacher': teacher.name + ' ' + teacher.last_name + ' ' + teacher.last_name_2,
                        'group': signature_dtl.group,
                        'average': signature_dtl.average,
                        'total_evaluated': signature_dtl.total_evaluated,
                        'questions': questions_results,
                        'comments': comments
                    }
                    signatures_resutls.append(signature_results)

            # Add the exam results to the return data.
            data.append({
                'exam': exam,
                'career': career.description,
                'period': exam.fk_period.period,
                'signatures_results': signatures_resutls
            })

        return data

    def get_teacher_career_results(self, teacher, career):
        """Get the signatures results of the teacher in the given career for all the active exams."""
        data = []

        # Get the active exams of the career.
        exams = EvaluationsExam.objects.filter(
            type__exact=career.type, status="ACTIVE")

        # Get the results for each exam.
        for exam in exams:

            # Get the signatures of the teacher for the career in the exam.
            signatures_dtl = EvaluationsTeacherSignature.objects.filter(
                fk_teacher__exact=teacher.id, fk_period__exact=exam.fk_period, status="ACTIVE").select_related('fk_signature')

            signatures_results = []
            for signature_dtl in signatures_dtl:

                # Get the results of the signature.
                signature_results = EvaluationsSignatureResult.objects.get(
                    group=signature_dtl.group,
                    fk_signature=signature_dtl.fk_signature.id,
                    fk_exam=exam.id,
                    status="ACTIVE"
                )

                # Get the results for each question in the exam for the signature.
                questions_results = EvaluationsSignatureQuestionResult.objects.filter(
                    group=signature_dtl.group,
                    fk_signature=signature_dtl.fk_signature.id,
                    fk_exam=exam.id,
                    fk_question__optional='NO',
                    status="ACTIVE"
                ).values_list('fk_question__description', 'result')

                # Get the comments of the signature/group.
                comments_result = EvaluationsSignatureQuestionResult.objects.get(
                    group=signature_dtl.group,
                    fk_signature=signature_dtl.fk_signature.id,
                    fk_exam=exam.id,
                    fk_question__optional='YES',
                    status="ACTIVE"
                ).result

                # Split the comments and add them to a list, only the ones that are not empty.
                comments = list(filter(None, comments_result.split('|')))

                # Crate a dictionary with the results of the signature and the questions.
                signatures_results.append({
                    'teacher': teacher.name + ' ' + teacher.last_name + ' ' + teacher.last_name_2,
                    'signature': signature_dtl.fk_signature.description,
                    'group': signature_dtl.group,
                    'average': signature_results.average,
                    'comments': comments,
                    'total_evaluated': signature_results.total_evaluated,
                    'questions': questions_results
                })

            # Add the results to the exam dictionary.
            exam_results = {
                'exam': exam.description,
                'career': career.description,
                'signatures_results': signatures_results,
                'period': exam.fk_period.period
            }

            # Add the exam results to the list that will be returned at the end.
            data.append(exam_results)

        return data

    def get_teacher_results_excel(self, data):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Resultados_Docentes.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        # Get the results for each exam.
        for exam in data:

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

            # Get the results for the signature/teacher.
            for signature in exam['signatures_results']:

                # This is the things that will be writed in the same line of the CVS.
                to_write = [
                    smart_str(u""+exam['career']),
                    smart_str(u""+signature['signature']),
                    smart_str(u""+signature['teacher']),
                    smart_str(u""+signature['group']),
                    smart_str(u""+str(signature['total_evaluated'])),
                    smart_str(u""+signature['average']),
                ]

                # Get the results for each question on the exam in the actual career.
                for question in signature['questions']:
                    to_write.append(
                        smart_str(u""+str(question[1])))

                # Get the comments and add the to the write dict.
                comments = ''
                for comment in signature['comments']:
                    if len(comment) > 3:
                        comments += comment + '|'
                to_write.append(smart_str(u""+comments))

                # Write the information of the signature in the CVS.
                writer.writerow(to_write)

        return response
