from django.db.models import Q
from django.utils.encoding import smart_str
from django.db import connection
from models import EvaluationsStudent, EvaluationsExam, EvaluationsStudentSignature, EvaluationsSignatureEvaluated
import datetime


def get_evaluations(student):
    """returns a dictionary with the exams and students-signatures that the student have"""
    student_career_cycle = student.fk_career.type

    career_exams = EvaluationsExam.objects.filter(
        status__exact='ACTIVE', type__exact=student_career_cycle)
    student_signatures = EvaluationsStudentSignature.objects.filter(
        fk_student__exact=student.id, status="ACTIVE")

    evaluations = []
    for exam in career_exams:
        evaluations_exam = {'exam': exam}
        groups = []
        for detail_group in student_signatures:
            groups.append(detail_group)
        evaluations_exam['groups'] = groups
        evaluations.append(evaluations_exam)
    return evaluations

def get_evaluated_signatures(student, evaluations):
    """returns a dictionary with the exams and students-signatures that the student already evaluated"""
    evaluated = []
    for exam_dict in evaluations:
        eval_exam_groups = {'exam': exam_dict['exam']}

        evaluated_groups_id = EvaluationsSignatureEvaluated.objects.filter(fk_exam__exact=exam_dict['exam'],
                                                                            fk_student_signature__in=exam_dict['groups'],
                                                                            status__exact="ACTIVE").values_list('fk_student_signature', flat=True)

        evaluated_groups = []
        for group in exam_dict['groups']:
            if group.id in evaluated_groups_id:
                evaluated_groups.append(group)
        eval_exam_groups['groups'] = evaluated_groups

        evaluated.append(eval_exam_groups)
    return evaluated

def get_evaluations_and_evaluated(evaluations, evaluated_signatures):
    """Return a dictionary with the exams, students-signatures and evaluated students-signatures"""
    result = []
    for exam_dict in evaluations:
        exam_data = {'exam': exam_dict['exam'],
                        'groups': exam_dict['groups']}
        for exam_eval_dict in evaluated_signatures:
            if exam_eval_dict['exam'] == exam_dict['exam']:
                exam_data['evaluated_groups'] = exam_eval_dict['groups']
        result.append(exam_data)
    return result

def get_next_evaluation(student, evaluations, evaluated_signatures):
        """return the exam and student_signature that is the next to evaluate (havent evaluated) for the student"""
        next_evaluation = {}
        for exam_dict in evaluations:
            for exam_eval_dict in evaluated_signatures:
                for group in exam_dict['groups']:
                    if not group in exam_eval_dict['groups']:
                        next_evaluation['exam'] = exam_dict['exam']
                        next_evaluation['group'] = group
                        return next_evaluation

        return next_evaluation
