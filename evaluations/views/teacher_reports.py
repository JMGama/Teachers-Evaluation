from django.shortcuts import render
from django.views import View
from easy_pdf.rendering import render_to_pdf_response
from .general_functions import *

class TeacherReports(View, GeneralFunctions):
    def get(self, request, career_id, teacher_id):
        pass
