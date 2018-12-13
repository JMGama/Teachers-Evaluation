from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from evaluations.models import *


class LogoutView(View, ):
    template_login = 'evaluations/login.html'

    def get(self, request):
        """Flush the session and redirects to the login page"""
        try:
            request.session.flush()
        except KeyError:
            pass
        return render(request, self.template_login)
