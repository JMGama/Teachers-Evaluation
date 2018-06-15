from django.db import models

# Create your models here.


class Alumno(models.Model):
    id_matricula = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200)
    apellido_paterno = models.CharField(max_length=200)
    apellido_materno = models.CharField(max_length=200)
    telefono = models.BigIntegerField(default=0)
    correo = models.EmailField(max_length=200)
    password = models.CharField(('Contraseña'), max_length=128)
    # carrera

    def __str__(self):
        return self.nombre + " " + self.apellido_paterno + " " + self.apellido_materno


class Docente(models.Model):
    id_clave = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200)
    apellido_paterno = models.CharField(max_length=200)
    apellido_materno = models.CharField(max_length=200)
    telefono = models.BigIntegerField(default=0)
    correo = models.EmailField(max_length=200)
    password = models.CharField(('Contraseña'), max_length=128)
    # carrera

    def __str__(self):
        return self.nombre + " " + self.apellido_paterno + " " + self.apellido_materno


class Carrera(models.Model):
    id_carrera = models.CharField(max_length=200)
    #nivel_escolar = models.CharField(max_length=200)
    nombre_carrera = models.CharField(max_length=200)
    # coordinador

    def __str__(self):
        return self.nombre_carrera


class Materia(models.Model):
    id_materia = models.CharField(max_length=200)
    #nivel_escolar = models.CharField(max_length=200)
    nombre_materia = models.CharField(max_length=200)
    # carrera

    def __str__(self):
        return self.nombre_materia


class Ciclo(models.Model):
    id_ciclo = models.CharField(max_length=200)
    nombre_ciclo = models.CharField(max_length=200)
    fecha_inicio = models.DateField(auto_now=False, auto_now_add=False)
    fecha_final = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.id_ciclo


class Pregunta(models.Model):
    TIPO_SELECCION_OPTIONS = (
        ('radiobutton', 'Seleeccion Si ó No'),
        ('textarea', 'Abierta')
    )

    id_pregunta = models.CharField(max_length=200)
    pregunta = models.CharField(max_length=200)
    tipo_seleccion = models.CharField(max_length=200, choices=TIPO_SELECCION_OPTIONS, default='radiobutton')

    def __str__(self):
        return self.pregunta
