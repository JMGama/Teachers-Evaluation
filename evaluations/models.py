from django.db import models

# Create your models here.


class Alumno(models.Model):
    matricula = models.CharField(max_length=200)
    nombre = models.CharField(max_length=200)
    apellido_paterno = models.CharField(max_length=200)
    apellido_materno = models.CharField(max_length=200)
    telefono = models.BigIntegerField(default=0)
    correo = models.EmailField(max_length=200)
    password = models.CharField(('Contraseña'), max_length=128)

    def __str__(self):
        user_information = {
            'matricula': self.matricula,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'correo': self.correo,
        }
        return user_information
