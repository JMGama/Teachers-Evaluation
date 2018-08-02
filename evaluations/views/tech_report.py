from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q
from easy_pdf.rendering import render_to_pdf_response
from evaluations.models import *
from .general_functions import *

class tech_report(View, GeneralFunctions):
    template_name  = 'evaluations/teach_report.html'
    template_login = 'evaluations/login.html'

    def get(self, request):
        if not request.session.get('session', False) or not request.session['type'] == 'coordinator':
            return render(request, self.template_login)

        template = self.template_name
#        kucing = Kucing.objects.get(id = id)
        coordinator = EvaluationsCoordinators.objects.get(
            idperson__exact=request.session['id_coordinator'])
        teachers={1:"z",2:"y"}
#        self.dumps(coord_career)
        context = {'teachers' : teachers}
        return render_to_pdf_response(request,template,context)
        #return render(request, template, context)

    def get_teachers(self, coordinator):
        coordinator_careers = EvaluationsDetailCoordinatorCareer.objects.filter(
        idcoordinator=coordinator.idperson)
        teachers = []
        for coord_career in coordinator_careers:
            career_teachers = EvaluationsDetailTeacherCareer.objects.filter(
                idcareer=coord_career.idcareer.idcareer)
            teachers.append(career_teachers.iddocente)
        return teachers

    def getTeacherSubjects(self, career_teachers):
        subjects = []
        for career_teacher in career_teachers:
            teacher = EvaluationsTeachers.objects.get(
                idperson=career_teacher.iddocente)
            signature = EvaluationsDetailGroupPeriodSignature.objects.filter(
                idteacher=career_teacher.iddocente)
        return career_teachers
