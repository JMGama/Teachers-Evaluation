from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from .models import *
# Create your views here.


class GeneralFunctions(object):

    @classmethod
    def get_evaluated_signatures(self, student, user_exams, user_groups):
        evaluated_signatures = EvaluationsDetailStudentSignatureExam.objects.filter(
            idstudent__exact=student)

        exam_group_evaluated = []
        for exam in user_exams:
            for group in user_groups:
                if group.idstudent.idcareer == exam.idcareer or exam.idcareer == None:
                    for evaluated_signature in evaluated_signatures:
                        if evaluated_signature.idgroup == group.id and evaluated_signature.idperiod == group.idperiod and evaluated_signature.idexam.id == exam.id:
                            exam_group_evaluated.append(group.id)
        return exam_group_evaluated


class LoginView(View):

    template_login = 'evaluations/login.html'

    def get(self, request):
        try:
            if request.session['session']:
                return redirect('home/')
        except KeyError:
            pass
        return render(request, self.template_login)

    def post(self, request):
        # Try to load student
        try:
            student = EvaluationsStudents.objects.get(
                enrollment__exact=request.POST['id_matricula'])
            if student.value == request.POST['password']:
                request.session['id_student'] = student.idperson
                request.session['session'] = True
                request.session['type'] = 'student'
                return redirect('home/')
        except Exception as e:
        # Try to load coordinator
            try:
                coordinator = EvaluationsCoordinators.objects.get(
                    enrollment__exact=request.POST['id_matricula'])
                if coordinator.value == request.POST['password']:
                    request.session['id_coordinator'] = coordinator.idperson
                    request.session['session'] = True
                    request.session['type'] = 'coordinator'
                    return redirect('monitoring/')
            except Exception as e:
                pass

        return render(request, self.template_login, {'second_time': True, 'validate': 'invalid'})


class HomeView(View, GeneralFunctions):

    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False):
            return render(request, self.template_login)

        # Values for the navigation bar
        student = EvaluationsStudents.objects.get(
            idperson=request.session['id_student'])
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=student.idcareer) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__exact=student.idperson, status="ACTIVO")
        evaluated_signatures = self.get_evaluated_signatures(
            student, user_exams, user_groups)

        # See if the exam have groups already evaluated by the student

        # Values for the view
        context = {
            'student': student,
            'user_exams': user_exams,
            'user_groups': user_groups,
            'evaluated_signatures': evaluated_signatures,
        }
        return render(request, self.template_home, context)


class EvaluationView(View, GeneralFunctions):

    template_evaluation = 'evaluations/evaluation_form.html'
    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request, exam_id, signature):
        if not request.session.get('session', False):
            return render(request, self.template_login)

        # Values for the navigation bar
        student = EvaluationsStudents.objects.get(
            idperson=request.session['id_student'])
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=student.idcareer) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__exact=student.idperson, status="ACTIVO")
        evaluated_signatures = self.get_evaluated_signatures(
            student, user_exams, user_groups)

        # Values for the view
        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)
        detail_group = EvaluationsDetailGroupPeriodSignature.objects.get(
            idsignature__exact=signature)

        context = {
            'user_exams': user_exams,
            'user_groups': user_groups,
            'student': student,
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
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=student.idcareer) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__exact=student.idperson, status="ACTIVO")

        # Get exam questions
        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)

        # Submit every exam answer
        num_answers = 0
        for question in exam_questions:
            try:
                submitted_answer = request.POST['answer_' + str(question.id)]
                answer = EvaluationsAnswers(
                    idstudent=student,
                    idgroup=EvaluationsDetailStudentGroup.objects.get(
                        idstudent__exact=student.idperson, idsignature__exact=signature),
                    iddetailquestion=EvaluationsDetailExamQuestion.objects.get(
                        id__exact=question.id),
                    answer=submitted_answer.upper(),
                    idexam=EvaluationsExams.objects.get(id__exact=exam_id),
                )

                answer.save()
                num_answers += 1
            except Exception as e:
                print(e)
                pass

        # Validate all answers well submitted to the DB.
        if num_answers == len(exam_questions):
            # Change status to evaluated on the evaluations_detail_student_group table.
            group_detail = EvaluationsDetailGroupPeriodSignature.objects.get(
                idsignature__exact=signature)

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
            evaluated_signatures = self.get_evaluated_signatures(
                student, user_exams, user_groups)

            context = {
                'user_exams': user_exams,
                'user_groups': user_groups,
                'student': student,
                'evaluated_signatures': evaluated_signatures,
                # [text, color]
                'message': ['La evaluacion se realizo correctamente.', 'green'],
            }
            return render(request, self.template_home, context)
        else:
            # Values for the view
            exam_questions = EvaluationsDetailExamQuestion.objects.filter(
                idexam__exact=exam_id)
            detail_group = EvaluationsDetailGroupPeriodSignature.objects.get(
                idsignature__exact=signature)

            context = {
                'user_exams': user_exams,
                'user_groups': user_groups,
                'student': student,
                'evaluated_signatures': evaluated_signatures,
                'exam_questions': exam_questions,
                'detail_group': detail_group,
                'exam_id': exam_id,
                'signature': signature,
                'message': ['Ocurrio un error al enviar la evaluacion.', 'red'],
            }
            return render(request, self.template_evaluation, context)


class LogoutView(View, GeneralFunctions):
    def get(self, request):
        try:
            request.session.flush()
        except KeyError:
            pass
        return redirect('/evaluations')


class MonitoringView(View, GeneralFunctions):

    template_monitoring = 'evaluations/monitoring.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        # Values for the view
        coordinator = EvaluationsCoordinators.objects.get(
            idperson__exact=request.session['id_coordinator'])

        context = {
            'coordinator': coordinator,
        }

        return render(request, self.template_monitoring, context)
