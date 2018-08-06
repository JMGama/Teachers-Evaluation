from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q
from django.utils.encoding import smart_str
from evaluations.models import *


class GeneralFunctions(object):

    @classmethod
    def get_evaluated_signatures(self, student):
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=student.idcareer) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__exact=student.idperson, status="ACTIVO")
        evaluated_signatures = EvaluationsDetailStudentSignatureExam.objects.filter(
            idstudent__exact=student)

        exam_group_evaluated = []
        for exam in user_exams:
            for group in user_groups:
                if group.idstudent.idcareer == exam.idcareer or exam.idcareer == None:
                    for evaluated_signature in evaluated_signatures:
                        if evaluated_signature.idgroup == group.id and evaluated_signature.idperiod == group.idperiod and evaluated_signature.idexam.id == exam.id:
                            exam_group_evaluated.append(group.id)
        return exam_group_evaluated

    @classmethod
    def get_evaluations(self, student):
        user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=student.idcareer) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        user_groups = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__exact=student.idperson, status="ACTIVO")

        evaluations = []
        for exam in user_exams:
            evaluations_exam = {'exam': exam}
            groups = []
            for detail_group in user_groups:
                if detail_group.idstudent.idcareer == exam.idcareer or exam.idcareer == None:
                    groups.append(detail_group)
            evaluations_exam['groups'] = groups
            evaluations.append(evaluations_exam)
        return evaluations

    @classmethod
    def get_next_evaluation(self, student, evaluations, evaluated_signatures):
        next_evaluation = {}
        for evaluation in evaluations:
            for group in evaluation['groups']:
                if not group.id in evaluated_signatures:
                    next_evaluation['exam'] = evaluation['exam']
                    next_evaluation['group'] = group
                    break
        return next_evaluation

    @classmethod
    def write_to_excel(self, students, career, writer):
        writer.writerow([
            smart_str(u"Matricula"),
            smart_str(u"Nombre"),
            smart_str(u"Correo"),
        ])

        for student in students:
            writer.writerow([
                smart_str(student.enrollment),
                smart_str(str(student.name) + " " +
                          str(student.lastname) + " " + str(student.lastname2)),
                smart_str(student.instemail),
            ])

    @classmethod
    def get_careers_data(self, coordinator):
        """Return a dictionary of all the coordinator careers with their evaluations results"""
        coordinator_careers = EvaluationsDetailCoordinatorCareer.objects.filter(
            idcoordinator__exact=coordinator.idperson)
        careers = {}
        for coord_career in coordinator_careers:
            career_students = EvaluationsStudents.objects.filter(
                idcareer=coord_career.idcareer.idcareer)

            careers[coord_career.idcareer] = self.get_evaluated_students(
                career_students)
            careers[coord_career.idcareer]['average_data'] = self. get_career_average(
                careers[coord_career.idcareer]['evaluated'])
        return careers

    @classmethod
    def get_evaluated_students(self, career_students):
        """Return all the students already evaluated and all that haven't evaluate."""
        students = {}
        eval_students = []
        not_eval_students = []

        for student in career_students:
            evaluations = self.get_evaluations(student)
            evaluated = self.get_evaluated_signatures(student)
            not_evaluated = []

            for evaluation in evaluations:
                for group in evaluation['groups']:
                    if not group.id in evaluated:
                        not_evaluated.append(group.id)
                        break

            if not not_evaluated:
                eval_students.append(student)
            else:
                not_eval_students.append(student)

        students['evaluated'] = eval_students
        students['not_evaluated'] = not_eval_students
        return students

    @classmethod
    def get_career_average(self, evaluated_students):
        answers_yes = 0
        answers_no = 0
        data = {}
        for student in evaluated_students:
            # Only consider non optional questions for the average
            questions = EvaluationsDetailExamQuestion.objects.filter()
            for question in questions:
                if question.idquestion.optional == 'NO':
                    answers = EvaluationsAnswers.objects.filter(
                        idstudent__exact=student.idperson, iddetailquestion__exact=question.id)
                    for answer in answers:
                        if answer.answer == 'YES':
                            answers_yes = answers_yes + 1
                        else:
                            answers_no = answers_no + 1
        data['average'] = answers_yes / (answers_yes + answers_no) * 100
        data['yes'] = answers_yes
        data['no'] = answers_no
        return data

    @classmethod
    def get_career_data(self, career):
        career_students = EvaluationsStudents.objects.filter(
            idcareer=career.idcareer)
        data = {}
        data['students'] = self.get_evaluated_students(
            career_students)
        data['average_data'] = self. get_career_average(
            data['students']['evaluated'])

        return data
