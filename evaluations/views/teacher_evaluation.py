from django.views import View
from django.http import HttpResponse

from .general_functions import *

class TeacherEvaluationView(View, GeneralFunctions):
    def get(self, request):
        return HttpResponse("WELCOME TO THE TEACHERS VIEW")