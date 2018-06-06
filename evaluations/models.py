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
        student_information = {
            'id_matricula': self.id_matricula,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'correo': self.correo,
        }
        return student_information


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
        teacher_information = {
            'id_clave': self.id_clave,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'correo': self.correo,
        }
        return teacher_information


class Carrera(models.Model):
    id_carrera = models.CharField(max_length=200)
    #nivel_escolar = models.CharField(max_length=200)
    nombre_carrera = models.CharField(max_length=200)
    # coordinador

    def __str__(self):
        career_information = {
            'id_carrera': self.id_carrera,
            'nombre_carrera': self.nombre_carrera,
        }
        return career_information


class Materia(models.Model):
    id_materia = models.CharField(max_length=200)
    #nivel_escolar = models.CharField(max_length=200)
    nombre_materia = models.CharField(max_length=200)
    # carrera

    def __str__(self):
        signature_information = {
            'id_materia': self.id_materia,
            'nombre_carrera': self.nombre_materia,
        }
        return signature_information

class Ciclo(models.Model):
    id_ciclo = models.CharField(max_length=200)
    fecha_inicio = models.DateField(auto_now=False, auto_now_add=False)
    fecha_final = models.DateField(auto_now=False, auto_now_add=False)

    def __str__(self):
        signature_information = {
            'id_ciclo': self.id_ciclo,
            'fecha_inicio': self.fecha_inicio,
            'fecha_final': self.fecha_final,
        }
        return signature_information
