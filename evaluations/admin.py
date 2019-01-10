# from django.contrib import admin

# from .models import *

# # Formulary specifications for the Django admin page.


# class EvaluationsDetailExamQuestionAdmin(admin.ModelAdmin):
#     list_display = ['id', 'idquestion', 'idexam']
#     exclude = ['updatedon', 'createdon']


# class EvaluationsQuestionsAdmin(admin.ModelAdmin):
#     list_display = ['id', 'description', 'type', 'status', 'optional',]
#     search_fields = ['id', 'description', 'type', 'status', 'optional',]
#     exclude = ['updatedon', 'createdon']


# class EvaluationsExamsAdmin(admin.ModelAdmin):
#     list_display = ['id', 'description', 'idcareer', 'status', ]
#     search_fields = ['id', 'description', 'status', ]
#     exclude = ['updatedon', 'createdon']


# class EvaluationsTeachersAdmin(admin.ModelAdmin):
#     list_display = ['idperson', 'enrollment', 'name', 'lastname',
#                     'lastname2', 'instemail', 'status', ]
#     search_fields = ['idperson', 'enrollment', 'name', 'lastname',
#                      'lastname2', 'instemail', 'status', ]
#     exclude = ['updatedon', 'createdon']


# class EvaluationsStudentsAdmin(admin.ModelAdmin):
#     def get_career_name(self, obj):
#         description = ParkingCareer.objects.get(
#             idcareergissa__exact=obj.idcareer).description
#         return description

#     list_display = ['idperson', 'enrollment', 'name', 'lastname',
#                     'lastname2', 'instemail', 'status', 'get_career_name']
#     search_fields = ['idperson', 'enrollment', 'name', 'lastname',
#                      'lastname2', 'instemail', 'status', ]
#     exclude = ['updatedon', 'createdon']


# class EvaluationsDetailGroupPeriodSignatureAdmin(admin.ModelAdmin):
#     list_display = ['id', 'idsignature', 'idteacher', 'idperiod', 'status', ]
#     search_fields = ['id', 'idsignature__name', 'idteacher__enrollment',
#                      'idteacher__name', 'idperiod__period', 'status']
#     raw_id_fields = ('idsignature', 'idteacher',)
#     exclude = ['updatedon', 'createdon']


# class EvaluationsDetailStudentGroupAdmin(admin.ModelAdmin):
#     def get_student_id(self, obj):
#         return obj.idstudent.enrollment

#     def get_student_name(self, obj):
#         return obj.idstudent.name + " " + obj.idstudent.lastname + " " + obj.idstudent.lastname2

#     def get_materia(self, obj):
#         return obj.idgroup.idsignature.name

#     get_student_id.short_description = 'Matricula'
#     get_student_name.short_description = 'Alumno'
#     get_materia.short_description = 'Materia'

#     list_display = ['id', 'idgroup', 'get_student_id',
#                     'get_student_name', 'get_materia', 'status',]
#     search_fields = ['idgroup', 'idstudent__enrollment', 'idstudent__name',
#                      'idstudent__lastname', 'idstudent__lastname2', 'idgroup__idsignature__name', 'status',]
#     raw_id_fields = ('idstudent',)
#     exclude = ['updatedon', 'createdon',]


# # Register your models here.
# admin.site.register(EvaluationsStudents, EvaluationsStudentsAdmin)
# admin.site.register(EvaluationsDetailGroupPeriodSignature,
#                     EvaluationsDetailGroupPeriodSignatureAdmin)
# admin.site.register(EvaluationsDetailStudentGroup,
#                     EvaluationsDetailStudentGroupAdmin)
# admin.site.register(EvaluationsTeachers, EvaluationsTeachersAdmin)
# admin.site.register(EvaluationsExams, EvaluationsExamsAdmin)
# admin.site.register(EvaluationsDetailExamQuestion,
#                     EvaluationsDetailExamQuestionAdmin)
# admin.site.register(EvaluationsQuestions, EvaluationsQuestionsAdmin)
# admin.site.register(EvaluationsSignatures)

# # Admin site changes
# admin.site.site_url = '/evaluations/'
# admin.site.site_header = 'Evaluations Administration'
