from django.db import models


class EvaluationsAnswer(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    answer = models.CharField(max_length=255, blank=True, null=True)
    fk_question = models.ForeignKey(
        'EvaluationsQuestion', models.DO_NOTHING, db_column='fk_question')
    fk_exam = models.ForeignKey(
        'EvaluationsExam', models.DO_NOTHING, db_column='fk_exam')
    fk_student_signature = models.ForeignKey(
        'EvaluationsStudentSignature', models.DO_NOTHING, db_column='fk_student_signature')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_answer'


class EvaluationsCareer(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    description = models.CharField(max_length=255, blank=True, null=True)
    abbreviation = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=13, blank=True, null=True)
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_career'


class EvaluationsCoordinator(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    enrollment = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=13, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    last_name_2 = models.CharField(max_length=255, blank=True, null=True)
    inst_email = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_coordinator'


class EvaluationsDtlCoordinatorCareer(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    id = models.IntegerField(primary_key=True)
    fk_coordinator = models.ForeignKey(
        EvaluationsCoordinator, models.DO_NOTHING, db_column='fk_coordinator')
    fk_career = models.ForeignKey(
        EvaluationsCareer, models.DO_NOTHING, db_column='fk_career')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_dtl_coordinator_career'


class EvaluationsDtlQuestionExam(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    id = models.IntegerField(primary_key=True)
    fk_question = models.ForeignKey(
        'EvaluationsQuestion', models.DO_NOTHING, db_column='fk_question')
    fk_exam = models.ForeignKey(
        'EvaluationsExam', models.DO_NOTHING, db_column='fk_exam')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_dtl_question_exam'


class EvaluationsDtlTeacherCareer(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    fk_career = models.ForeignKey(
        EvaluationsCareer, models.DO_NOTHING, db_column='fk_career')
    fk_teacher = models.ForeignKey(
        'EvaluationsTeacher', models.DO_NOTHING, db_column='fk_teacher')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_dtl_teacher_career'


class EvaluationsExam(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=13, blank=True, null=True)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
    fk_period = models.ForeignKey(
        'EvaluationsPeriod', models.DO_NOTHING, db_column='fk_period')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_exam'


class EvaluationsPeriod(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    period = models.CharField(max_length=255, blank=True, null=True)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_period'


class EvaluationsQuestion(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    type = models.CharField(max_length=10)
    description = models.CharField(max_length=255, blank=True, null=True)
    optional = models.CharField(max_length=3, blank=True, null=True)
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_question'


class EvaluationsSignature(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    description = models.CharField(max_length=255, blank=True, null=True)
    fk_career = models.ForeignKey(
        EvaluationsCareer, models.DO_NOTHING, db_column='fk_career')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_signature'


class EvaluationsSignatureEvaluated(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    evaluated = models.CharField(max_length=3, blank=True, null=True)
    fk_exam = models.ForeignKey(
        EvaluationsExam, models.DO_NOTHING, db_column='fk_exam')
    fk_student_signature = models.ForeignKey(
        'EvaluationsStudentSignature', models.DO_NOTHING, db_column='fk_student_signature')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_signature_evaluated'


class EvaluationsSignatureQuestionResult(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    group = models.CharField(max_length=255)
    result = models.TextField(blank=True, null=True)
    total_evaluated = models.IntegerField()
    fk_question = models.ForeignKey(
        EvaluationsQuestion, models.DO_NOTHING, db_column='fk_question')
    fk_signature = models.ForeignKey(
        EvaluationsSignature, models.DO_NOTHING, db_column='fk_signature')
    fk_exam = models.ForeignKey(
        EvaluationsExam, models.DO_NOTHING, db_column='fk_exam')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_signature_question_result'


class EvaluationsSignatureResult(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    group = models.CharField(max_length=255)
    average = models.CharField(max_length=255)
    total_evaluated = models.IntegerField()
    fk_signature = models.ForeignKey(
        EvaluationsSignature, models.DO_NOTHING, db_column='fk_signature')
    fk_exam = models.ForeignKey(
        EvaluationsExam, models.DO_NOTHING, db_column='fk_exam')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_signature_result'


class EvaluationsStudent(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    enrollment = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    last_name_2 = models.CharField(max_length=255, blank=True, null=True)
    inst_email = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    fk_career = models.ForeignKey(
        EvaluationsCareer, models.DO_NOTHING, db_column='fk_career')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_student'


class EvaluationsStudentSignature(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    group = models.CharField(max_length=255)
    fk_student = models.ForeignKey(
        EvaluationsStudent, models.DO_NOTHING, db_column='fk_student')
    fk_signature = models.ForeignKey(
        EvaluationsSignature, models.DO_NOTHING, db_column='fk_signature')
    fk_period = models.ForeignKey(
        EvaluationsPeriod, models.DO_NOTHING, db_column='fk_period')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_student_signature'


class EvaluationsTeacher(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    enrollment = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    last_name_2 = models.CharField(max_length=255, blank=True, null=True)
    inst_email = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_teacher'


class EvaluationsTeacherSignature(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    group = models.CharField(max_length=255)
    fk_teacher = models.ForeignKey(
        EvaluationsTeacher, models.DO_NOTHING, db_column='fk_teacher')
    fk_signature = models.ForeignKey(
        EvaluationsSignature, models.DO_NOTHING, db_column='fk_signature')
    fk_period = models.ForeignKey(
        EvaluationsPeriod, models.DO_NOTHING, db_column='fk_period')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_teacher_signature'


class EvaluationsTeacherSignatureEvaluated(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    evaluated = models.CharField(max_length=3, blank=True, null=True)
    fk_exam = models.ForeignKey(
        EvaluationsExam, models.DO_NOTHING, db_column='fk_exam')
    fk_teacher_signature = models.ForeignKey(
        'EvaluationsTeacherSignature', models.DO_NOTHING, db_column='fk_teacher_signature')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_teacher_signature_evaluated'


class EvaluationsTeacherSignatureQuestionResult(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    group = models.CharField(max_length=255)
    result = models.TextField(blank=True, null=True)
    total_evaluated = models.IntegerField()
    fk_question = models.ForeignKey(
        EvaluationsQuestion, models.DO_NOTHING, db_column='fk_question')
    fk_teacher = models.ForeignKey(
        EvaluationsTeacher, models.DO_NOTHING, db_column='fk_teacher')
    fk_signature = models.ForeignKey(
        EvaluationsSignature, models.DO_NOTHING, db_column='fk_signature')
    fk_exam = models.ForeignKey(
        EvaluationsExam, models.DO_NOTHING, db_column='fk_exam')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_teacher_signature_question_result'


class EvaluationsTeacherSignatureResult(models.Model):
    # add it always at the top of each model
    objects = models.Manager()

    group = models.CharField(max_length=255)
    average = models.CharField(max_length=255)
    total_evaluated = models.IntegerField()
    fk_teacher = models.ForeignKey(
        EvaluationsTeacher, models.DO_NOTHING, db_column='fk_teacher')
    fk_signature = models.ForeignKey(
        EvaluationsSignature, models.DO_NOTHING, db_column='fk_signature')
    fk_exam = models.ForeignKey(
        EvaluationsExam, models.DO_NOTHING, db_column='fk_exam')
    status = models.CharField(max_length=8, default='ACTIVE')

    class Meta:
        managed = False
        db_table = 'evaluations_teacher_signature_result'
