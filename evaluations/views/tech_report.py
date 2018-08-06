from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q, Func, F
from easy_pdf.rendering import render_to_pdf_response
from evaluations.models import *
from .general_functions import *

class tech_report(View, GeneralFunctions):
    template_name  = 'evaluations/teach_report.html'
    template_login = 'evaluations/login.html'
    exam = 1

    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        template = self.template_name
#           Datos del Coordinador
        coordinator = EvaluationsCoordinators.objects.get(
            idperson__exact=request.session['id_coordinator'])
#           Carreras x coordinador
        coordinator_careers = EvaluationsDetailCoordinatorCareer.objects.select_related(
        'idcoordinator').filter(idcoordinator=coordinator.idperson)
#           Datos del maestro
#           Para extraer nombre career_teachers.iddocente.name
        career_teachers=getTeachers(coordinator_careers)

        teachers={1:"z",2:"y"}

#        self.dumps(coord_career)
        context = {
        'teachers' : career_teachers,
        'questions': self.getQuestions(self.exam)
        }
        return render_to_pdf_response(request,template,context)
        #return render(request, template, context)

    def getTeachers(self, coordinator_careers):
        teachers = {}
        for coord_career in coordinator_careers:
            career_teachers = EvaluationsDetailTeacherCareer.objects.select_related(
            'iddocente','idcareer').filter(idcareer=coord_career.idcareer)
            teachers[coord_career.idcareer]=career_teachers
        return teachers

    def getTeacherSubjects(self, career_teachers):
        subjects = []
        for career_teacher in career_teachers:
            teacher = EvaluationsTeachers.objects.get(
                idperson=career_teacher.iddocente)
            signature = EvaluationsDetailGroupPeriodSignature.objects.filter(
                idteacher=career_teacher.iddocente)
        return career_teachers

    def getQuestions(self, exam):
        qst=[]
        questions = EvaluationsDetailExamQuestion.objects.select_related('idquestion').filter(
        idexam=exam)
        for question in questions:
            qst[]=question.idquestion
        return qst

    def getAverage(self, question):
        EvaluationsAnswers.objects.get()
        return
