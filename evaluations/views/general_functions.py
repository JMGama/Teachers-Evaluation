from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.db.models import Q
from django.utils.encoding import smart_str
from evaluations.models import *


class GeneralFunctions(object):

    @classmethod
    def get_evaluated_signatures(self, student):
        """return a list of all the evaluations (groupid) already made by the student"""
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
        """returns a dictionary with the exams and groups(student-signature) that the student have"""
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
        """return the exam and group that is the next to evaluate (havent evaluated) for the student"""
        next_evaluation = {}
        for evaluation in evaluations:
            for group in evaluation['groups']:
                if not group.id in evaluated_signatures:
                    next_evaluation['exam'] = evaluation['exam']
                    next_evaluation['group'] = group
                    break
        return next_evaluation

    @classmethod
    def dumps(self, obj):
        for attr in dir(obj):
            if hasattr( obj, attr ):
                print( "obj.%s = %s" % (attr, getattr(obj, attr)))

    @classmethod
    def write_to_excel(self, students, career, writer):
        """creates the CSV with the student data that were past"""
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
        """return a dictionary with the average of the students evaluated and the total of 'yes' and 'no' in the results"""
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
        """return a dictionary with the students evaluated, not evaluated and the average result of the career"""
        career_students = EvaluationsStudents.objects.filter(
            idcareer=career.idcareer)
        data = {}
        data['exams'] = user_exams = EvaluationsExams.objects.filter(
            Q(idcareer__exact=career) | Q(idcareer__isnull=True) & Q(status__exact='ACTIVO'))
        data['students'] = self.get_evaluated_students(
            career_students)
        data['average_data'] = self. get_career_average(
            data['students']['evaluated'])

        return data

    @classmethod
    def get_career_teachers_signatures(self, career):
        """return a dictionary with all the teachers of the career and each teacher signatures that they give"""
        signatures = self.get_career_signatures(career)

        teachers_id = EvaluationsDetailGroupPeriodSignature.objects.filter(
            idsignature__in=signatures.values('id')).values('idteacher').distinct()
        teachers = EvaluationsTeachers.objects.filter(idperson__in=teachers_id)

        data = {}
        for teacher in teachers:
            teacher_signatures_id = EvaluationsDetailGroupPeriodSignature.objects.filter(
                idsignature__in=signatures.values('id'), idteacher__exact=teacher.idperson).values('idsignature')
            teacher_signatures = []

            for signature_id in teacher_signatures_id:
                teacher_signatures.append(EvaluationsSignatures.objects.get(
                    id__exact=signature_id['idsignature']))

            data[teacher] = teacher_signatures
        return data

    @classmethod
    def get_career_signatures(self, career):
        """return all the signatures currently open in the career"""
        signatures = []
        students_id = EvaluationsStudents.objects.filter(
            idcareer=career.idcareer).values('idperson')
        signatures_id = EvaluationsDetailStudentGroup.objects.filter(
            idstudent__in=students_id).values('idsignature').distinct()
        signatures = EvaluationsSignatures.objects.filter(id__in=signatures_id)

        return signatures

    @classmethod
    def get_teacher_signature_results(self, teacher, signature, exam):
        """Return the results of the evaluations to the teacher at the signature of the submitted test"""

        groups = EvaluationsDetailStudentSignatureExam.objects.filter(
            idsignature__exact=signature, idteacher__exact=teacher.idperson).values('id')
        questions_detail_exam = EvaluationsDetailExamQuestion.objects.filter(
            idexam__exact=exam.id)

        results = {}
        for question_exam in questions_detail_exam:
            question = question_exam.idquestion

            if question.optional == 'NO':
                yes_answers = EvaluationsAnswers.objects.filter(
                    iddetailquestion__exact=question_exam.id, answer='YES', idgroup__in=groups)
                no_answers = EvaluationsAnswers.objects.filter(
                    iddetailquestion__exact=question_exam.id, answer='NO', idgroup__in=groups)

                average = int(len(yes_answers) /(len(yes_answers) + len(no_answers)) * 100)

                results[question] = {'yes': len(yes_answers), 'no': len(no_answers), 'average': average}
            else:
                answer = EvaluationsAnswers.objects.filter(
                    iddetailquestion__exact=question_exam.id, idgroup__in=groups).exclude(answer__isnull=True)
                results[question] = {'answers': answer}

        return results
