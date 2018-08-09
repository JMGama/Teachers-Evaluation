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
#           Para extraer carreras del cordinador coord_career.idcareer
        coordinator_careers = EvaluationsDetailCoordinatorCareer.objects.select_related(
        'idcoordinator').filter(idcoordinator=coordinator.idperson)
        x=self.getInfo(coordinator_careers)
#        self.dumps(x[0])
        context = {
        'all' : self.getInfo(coordinator_careers),
        'questions': self.getQuestions(self.exam)
        }
        return render_to_pdf_response(request,template,context)
#       return render(request, template, context)

    def getTeachers(self, coordinator_careers):
        teachers = {}
        for coord_career in coordinator_careers:
            career_teachers = EvaluationsDetailGroupPeriodSignature.objects.select_related(
            'idsignature','idteacher').filter(idteacher=coord_career.idcareer.idcareer)
            for career_teacher in career_teachers:
                teachers[career_teacher.iddocente]=career_teacher.idsignature
        return teachers

    def getInfo(self, coordinator_careers):
        data = []
        aux = {}
        j=1
        aux["signature"] = ""
        for coord_career in coordinator_careers:
            teachers = EvaluationsDetailTeacherCareer.objects.filter(idcareer__exact=coord_career.idcareer).select_related('iddocente')
            for teacher in teachers:
                signatures = EvaluationsDetailStudentSignatureExam.objects.filter(idteacher__exact=teacher.iddocente).select_related('idstudent')
                j=1
                aux["signature"] = ""
                for sig in signatures:
                    if j==1:
                        if aux["signature"] != sig.idsignature.name:
                            aux["signature"] = sig.idsignature.name
                            aux["name"] = teacher.iddocente.name + " " + teacher.iddocente.lastname + " " + teacher.iddocente.lastname2
                            for i in [1,2,3,4,5]:
                                if i != 5:
                                    for q in Average.objects.raw("select fnQavg(%s,%s) as avg",[i,sig.idsignature.id]):
                                        aux["Q"+str(i)] = q.avg
                                else:
                                    query = "SELECT GROUP_CONCAT(ANS.answer SEPARATOR ':') as avg FROM evaluations_answers ANS INNER JOIN evaluations_detail_student_group DET ON DET.id=ANS.idGroup WHERE ANS.idQuestion = 5 AND DET.idSignature = " + str(sig.idsignature.id)
                                    for q in Average.objects.raw(query):
                                        if q.avg:
                                            aux["Q"+str(i)] = q.avg.split(':')
                            data.append(aux)
                            aux={}
                        else:
                            aux["signature"] = sig.idsignature.name
                    else:
                        aux["signature"] = ""
                    j+=1
        return data

    def getQuestions(self, exam):
        qst=[]
        questions = EvaluationsDetailExamQuestion.objects.select_related('idquestion').filter(
        idexam=exam)
        for question in questions:
            qst.append(question.idquestion.description)
        return qst
