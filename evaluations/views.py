from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from .models import *

# Create your views here.


class GeneralFunctions(object):

    @classmethod
    def get_evaluated_signatures(self, student):
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=student.idcareer) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__exact=student.idperson, status="ACTIVO")
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

    @classmethod
    def get_evaluations(self, student):
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=student.idcareer) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__exact=student.idperson, status="ACTIVO")

        evaluations = []
        for exam in user_exams:
            evaluations_exam = {'exam': exam}
            groups = []
            for detail_group in user_groups:
                if detail_group.idstudent.idcareer == exam.idcareer or exam.idcareer == None:
                    groups.append(detail_group)
            evaluations_exam['groups'] = groups
            evaluations.append(evaluations_exam)
        return evaluations

    @classmethod
    def get_next_evaluation(self, student, evaluations, evaluated_signatures):
        next_evaluation = {}
        for evaluation in evaluations:
            for group in evaluation['groups']:
                if not group.id in evaluated_signatures:
                    next_evaluation['exam'] = evaluation['exam']
                    next_evaluation['group'] = group
                    break
        return next_evaluation


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
        evaluations = self.get_evaluations(student)
        evaluated_signatures = self.get_evaluated_signatures(student)
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

        context = {
            'student': student,
            'next_evaluation': next_evaluation,
            'evaluations': evaluations,
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
            except Exception as e:
                print(e)

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
            # Values for the view
            exam_questions = EvaluationsDetailExamQuestion.objects.filter(
                idexam__exact=exam_id)
            detail_group = EvaluationsDetailGroupPeriodSignature.objects.get(
                idsignature__exact=signature)

            # Value for navigation bar
            evaluations = self.get_evaluations(student)
            evaluated_signatures = self.get_evaluated_signatures(
                student)

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


class LogoutView(View, GeneralFunctions):
    template_login = 'evaluations/login.html'

    def get(self, request):
        try:
            request.session.flush()
        except KeyError:
            pass
        return render(request, self.template_login)


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
