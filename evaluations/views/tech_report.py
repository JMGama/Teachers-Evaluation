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
#Ejecuta este conmando em marydb para aumentar el espacio en memoria del group concat
#SET session group_concat_max_len=15000;
#SET group_concat_max_len=15000;
    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)
        template = self.template_name
        #Datos del Coordinador
        coordinator = EvaluationsCoordinators.objects.get(idperson__exact=request.session['id_coordinator'])
        #Carreras x coordinador
        #Para extraer carreras del cordinador coord_career.idcareer
        data = []
        coordinator_careers = EvaluationsDetailCoordinatorCareer.objects.select_related(
        'idcareer').filter(idcoordinator__exact=coordinator.idperson)
        for dcarrer in coordinator_careers:
            data.append(self.getInfo2(dcarrer.idcareer))
        context = {
        'all' : data
        }
        return render_to_pdf_response(request,template,context)
        #return render(request, template, context)

    def getQuestions(self, exam):
        qst=[]
        questions = EvaluationsDetailExamQuestion.objects.select_related('idquestion').filter(
        idexam=exam)
        for question in questions:
            qst.append(question.idquestion)
        return qst

    def getInfo2(self, career):
        data1 = []
        aux = {}
        data=self.get_career_teachers_signatures(career)
        #key maestro #val materia
        for key,val in data.items():
            for signature in val:
                aux["name"]=self.html_decode(str(key.name) + " " + str(key.lastname) + " " + str(key.lastname2))
                aux["signature"] = self.html_decode(signature.name)
                #Total de Estudiantes
                query = "SELECT COUNT(DISTINCT ANS.idStudent) as avg FROM evaluations_answers ANS INNER JOIN evaluations_detail_student_group DET ON DET.id=ANS.idGroup WHERE DET.idSignature = " + str(signature.id)
                for q in Average.objects.raw(query):
                    aux["Stotal"] = q.avg
                #Falta lista con totales
                aux["rst"]=self.getAvgs(signature.id)
                #Q5
                query = "SELECT GROUP_CONCAT(ANS.answer SEPARATOR ':') as avg FROM evaluations_answers ANS INNER JOIN evaluations_detail_student_group DET ON DET.id=ANS.idGroup WHERE ANS.idQuestion = 5 AND DET.idSignature = " + str(signature.id)
                for q in Average.objects.raw(query):
                    if q.avg:
                        aux["Q5"] = self.html_decode(q.avg).split(':')
            data1.append(aux)
            aux={}
        return data1

    def getAvgs(self, id):
        data = {}
        i=1
        avgT=0
        for qst in self.getQuestions(self.exam):
            if i != 5:
                for q in Average.objects.raw("select fnQavg(%s,%s) as avg",[i,id]):
                    data[self.html_decode(qst.description)]=q.avg
                    avgT+=q.avg
            i+=1
        data["Promedio general"]=avgT/(i-2)
        return data

    def html_decode(self, s):
        """
        Returns the ASCII decoded version of the given HTML string. This does
        NOT remove normal HTML tags like <p>.
        """
        htmlCodes = {
                ("¿", '&iquest;'),
                ("'", '&#39;'),
                ('"', '&quot;'),
                ('>', '&gt;'),
                ('<', '&lt;'),
                ('ó', '&oacute;'),
                ('Ó', '&Oacute;'),
                ('Á', '&Aacute;'),
                ('É', '&Eacute;'),
                ('Í', '&Iacute;'),
                ('Ú', '&Uacute;'),
                ('á', '&aacute;'),
                ('é', '&eacute;'),
                ('í', '&iacute;'),
                ('ó', '&oacute;'),
                ('ú', '&uacute;'),
                ('Ñ', '&Ntilde;'),
                ('ñ', '&ntilde;')
                }
        for code in htmlCodes:
            s = s.replace(code[0], code[1])
        return s
