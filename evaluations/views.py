from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from .models import *
# Create your views here.


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
        try:
            student = EvaluationsStudents.objects.get(
                enrollment__exact=request.POST['id_matricula'])
            if student.value == request.POST['password']:
                request.session['id_student'] = student.idperson
                request.session['session'] = True
                return redirect('home/')
        except Exception as e:
            pass

        return render(request, self.template_login, {'second_time': True, 'validate': 'invalid'})


class HomeView(View):

    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False):
            return render(request, self.template_login)
        # Values for the navigation bar
        student = EvaluationsStudents.objects.get(idperson=request.session['id_student'])
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=student.idcareer) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__exact=student.idperson, status="ACTIVO")

        print(user_groups)

        # Values for the view
        context = {
            'student': student,
            'user_exams': user_exams,
            'user_groups': user_groups,
        }
        return render(request, self.template_home, context)


class EvaluationView(View):

    template_evaluation = 'evaluations/evaluation_form.html'
    template_home = 'evaluations/home.html'
    template_login = 'evaluations/login.html'
    test = 'evaluations/detail.html'

    def get(self, request, exam_id, detail_group_id):
        if not request.session.get('session', False):
            return render(request, self.template_login)

        # Values for the navigation bar
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=request.session['carrera']) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__enrollment__exact=request.session['matricula'], status="ACTIVO")

        # Values for the view
        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)

        detail_group = EvaluationsDetailStudentGroup.objects.get(
            id__exact=detail_group_id)
        career = ParkingCareer.objects.get(
            idcareer__exact=request.session['carrera'])

        context = {
            'user_exams': user_exams,
            'user_groups': user_groups,
            'exam_questions': exam_questions,
            'detail_group': detail_group,
            'career': career,
            'exam_id': exam_id,
            'detail_group_id': detail_group_id,
        }

        return render(request, self.template_evaluation, context)

    def post(self, request, exam_id, detail_group_id):
        # Verify if the user is correctly logged in
        if not request.session.get('session', False):
            return render(request, self.template_login)

        # Values for the navigation bar
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=request.session['carrera']) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__enrollment__exact=request.session['matricula'], status="ACTIVO")

        # Get exam answers
        exam_questions = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam_id)

        # Submit every exam answer
        num_answers = 0
        for question in exam_questions:
            try:
                submitted_answer = request.POST['answer_' + str(question.id)]
                answer = EvaluationsAnswers(
                    idstudent=EvaluationsStudents.objects.get(
                        idperson__exact=request.session['id_estudiante']),
                    idgroup=EvaluationsDetailStudentGroup.objects.get(
                        id__exact=detail_group_id).idgroup,
                    iddetailquestion=EvaluationsDetailExamQuestion.objects.get(
                        id__exact=question.id),
                    answer=submitted_answer.upper())

                answer.save()
                num_answers += 1
            except Exception as e:
                print(e)
                pass

        # Validate all answers well submitted to the DB.
        if num_answers == len(exam_questions):

            # Change status to evaluated on the evaluations_detail_student_group table.
            student_grup_detail = EvaluationsDetailStudentGroup.objects.get(
                id__exact=detail_group_id)
            student_grup_detail.evaluated = 'YES'
            student_grup_detail.save()

            context = {
                'user_exams': user_exams,
                'user_groups': user_groups,
                'exam_questions': exam_questions,
                # [text, color]
                'message': ['La evaluacion se realizo correctamente.', 'green'],
            }
            return render(request, self.template_home, context)
        else:
            detail_group = EvaluationsDetailStudentGroup.objects.get(
                id__exact=detail_group_id)
            career = ParkingCareer.objects.get(
                idcareer__exact=request.session['carrera'])
            context = {
                'user_exams': user_exams,
                'user_groups': user_groups,
                'exam_questions': exam_questions,
                'detail_group': detail_group,
                'career': career,
                'exam_id': exam_id,
                'detail_group_id': detail_group_id,
                'message': ['Ocurrio un error al enviar la evaluacion.', 'red'],
            }
            return render(request, self.template_evaluation, context)


class LogoutView(View):
    def get(self, request):
        try:
            request.session.flush()
        except KeyError:
            pass
        return redirect('/evaluations')
