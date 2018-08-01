from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q

from evaluations.models import *
from .general_functions import *

class LogoutView(View, GeneralFunctions):
    template_login = 'evaluations/login.html'

    def get(self, request):
        try:
            request.session.flush()
        except KeyError:
            pass
        return render(request, self.template_login)
