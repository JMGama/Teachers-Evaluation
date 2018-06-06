from django.contrib import admin

from .models import Alumno, Docente, Carrera, Materia
# Register your models here.
admin.site.register(Alumno)
admin.site.register(Docente)
admin.site.register(Carrera)
admin.site.register(Materia)
