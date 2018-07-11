from django.contrib import admin

from .models import *
# Register your models here.

admin.site.register(EvaluationsSignatures)
admin.site.register(EvaluationsQuestions)


class InstitutionalTeachersAdmin(admin.ModelAdmin):
    list_display = ['idperson', 'enrollment', 'name', 'lastname',
                    'lastname2', 'instemail', 'status', ]
    search_fields = ['idperson', 'enrollment', 'name', 'lastname',
                     'lastname2', 'instemail', 'status', ]
    exclude = ['updatedon', 'createdon']


class InstitutionalStudentsAdmin(admin.ModelAdmin):
    def get_career_name(self, obj):
        description = ParkingCareer.objects.get(
            idcareergissa__exact=obj.idcareer).description
        return description

    list_display = ['idperson', 'enrollment', 'name', 'lastname',
                    'lastname2', 'instemail', 'status', 'get_career_name']
    search_fields = ['idperson', 'enrollment', 'name', 'lastname',
                     'lastname2', 'instemail', 'status', ]
    exclude = ['updatedon', 'createdon']


class EvaluationsGroupsAdmin(admin.ModelAdmin):
    list_display = ['id', 'idsignature', 'idteacher', 'idperiod', 'status', ]
    search_fields = ['id', 'idsignature__name', 'idteacher__enrollment',
                     'idteacher__name', 'idperiod__period', 'status']
    raw_id_fields = ('idsignature', 'idteacher',)
    exclude = ['updatedon', 'createdon']


class EvaluationsDetailStudentGroupAdmin(admin.ModelAdmin):
    def get_student_id(self, obj):
        return obj.idstudent.enrollment

    def get_student_name(self, obj):
        return obj.idstudent.name + " " + obj.idstudent.lastname + " " + obj.idstudent.lastname2

    def get_materia(self, obj):
        return obj.idgroup.idsignature.name

    get_student_id.short_description = 'Matricula'
    get_student_name.short_description = 'Alumno'
    get_materia.short_description = 'Materia'

    list_display = ['id', 'idgroup_id', 'get_student_id',
                    'get_student_name', 'get_materia', 'status', 'evaluated']
    search_fields = ['idgroup__id', 'idstudent__enrollment', 'idstudent__name',
                     'idstudent__lastname', 'idstudent__lastname2', 'idgroup__idsignature__name', 'status', 'evaluated']
    raw_id_fields = ('idstudent',)
    exclude = ['updatedon', 'createdon', 'evaluated']


admin.site.register(InstitutionalStudents, InstitutionalStudentsAdmin)
admin.site.register(EvaluationsGroups, EvaluationsGroupsAdmin)
admin.site.register(EvaluationsDetailStudentGroup,
                    EvaluationsDetailStudentGroupAdmin)
admin.site.register(InstitutionalTeachers, InstitutionalTeachersAdmin)
