import csv

from django.shortcuts import HttpResponse, redirect, render
from django.views import View
from easy_pdf.rendering import render_to_pdf_response

from evaluations.models import (EvaluationsCareer, EvaluationsCoordinator,
                                EvaluationsDtlCoordinatorCareer,
                                EvaluationsExam, EvaluationsTeacher,
                                EvaluationsTeacherSignature,
                                EvaluationsSignatureResult, EvaluationsSignatureQuestionResult)


class TeachersReportsView(View):
    template_login = 'evaluations/login.html'

    def get(self, request, report_type):
        """Function that make the teacher/s reports"""

        # Verify if the coordinator is correctly logged in.
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        template = ''
        context = {}

        if report_type == 'teacher_report':
            template, context = self.teacher_report(request)
        elif report_type == 'career_teachers_report':
            template, context = self.career_teachers_report(request)
        elif report_type == 'career_teachers_excel':
            return self.career_teachers_excel(request)

        if template and context:
            return render_to_pdf_response(request, template, context)

        return redirect('/evaluations/career_results/32/47740/#reportes')

    def teacher_report(self, request):
        template = 'evaluations/teachers_report.html'

        career_id = request.GET.get('career_id', '')
        teacher_id = request.GET.get('teacher_id', '')

        career = EvaluationsCareer.objects.get(pk__exact=career_id)
        teacher = EvaluationsTeacher.objects.get(pk__exact=teacher_id)

        data = self.get_teacher_career_results(teacher, career)

        # print(data)

        context = {
            'data': data,
        }
        return template, context

    def career_teachers_report(self, request):
        template = 'evaluations/teachers_report.html'

        career_id = request.GET.get('career_id', '')
        data = {}

        career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
        career_teachers = self.get_career_teachers(career)
        career_data = self.get_career_data(career)

        for teacher in career_teachers:
            data[teacher] = self.get_teacher_signatures_results(
                career, career_data, teacher, exam=career_data['exams'][0])

        context = {
            'data': data,
            'exam': career_data['exams'][0],
        }

        return template, context

    def career_teachers_excel(self, request):
        career_id = request.GET.get('career_id', '')
        career = EvaluationsCareers.objects.get(idcareer__exact=career_id)
        results = self.get_teachers_results(career)
        response = self.teacher_results_excel(request, results)
        return response





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

                # Get the results  for each question in the exam for the signature.
                questions_results = EvaluationsSignatureQuestionResult.objects.filter(
                    group=signature_dtl.group,
                    fk_signature=signature_dtl.fk_signature.id,
                    fk_exam=exam.id,
                    fk_question__optional='NO',
                    status="ACTIVE"
                ).values_list('fk_question__description', 'result')

                # Get the comments of the ecaluation.
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





    def get_teachers_results(self, career):
        results = {}

        data = {}
        career_teachers = self.get_career_teachers(career)
        career_data = self.get_career_data(career)

        for teacher in career_teachers:
            data[teacher] = self.get_teacher_signatures_results(
                career, career_data, teacher, exam=career_data['exams'][0])
        results[career] = data

        return results

    def teacher_results_excel(self, request, results):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=Resultados_Docentes.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8'))

        titles = ['CARRERA', 'MATERIA', 'DOCENTE', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6',
                  'P7', 'P8', 'P9', 'P10', 'P11', 'P12', 'TOTAL ALUMNOS EVALUADOS']

        writer.writerow([smart_str(u""+title) for title in titles])
        for career, teachers in results.items():
            for teacher, signatures in teachers.items():
                for singature, items in signatures.items():
                    teacher_data = [career.description, singature.name,
                                    teacher.name+" "+teacher.lastname+" "+teacher.lastname2]
                    for question, data in items['questions'].items():
                        if 'average'in data:
                            teacher_data.append(str(data['average']) + "%")
                        else:
                            comments = ''
                            for answer in data['answers']:
                                if len(answer.answer) > 2:
                                    comments += answer.answer + " | "
                            comments.replace('\n', '').replace('\r', '')
                            teacher_data.append(comments)
                    teacher_data.append(items['evaluated'])
                    writer.writerow(teacher_data)
            writer.writerow([])
        return response
