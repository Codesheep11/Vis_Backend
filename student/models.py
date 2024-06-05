from django.db import models


class DataStudentinfo(models.Model):
    index = models.IntegerField(primary_key=True)
    student_id = models.TextField(db_column='student_ID', blank=True, null=True)  # Field name made lowercase.
    sex = models.TextField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    major = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Data_StudentInfo'


class DataSubmitrecord(models.Model):
    index = models.IntegerField(primary_key=True)
    class_field = models.TextField(db_column='class', blank=True,
                                   null=True)  # Field renamed because it was a Python reserved word.
    time = models.IntegerField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    title_id = models.TextField(db_column='title_ID', blank=True, null=True)  # Field name made lowercase.
    method = models.TextField(blank=True, null=True)
    memory = models.IntegerField(blank=True, null=True)
    timeconsume = models.TextField(blank=True, null=True)
    student_id = models.TextField(db_column='student_ID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Data_SubmitRecord'


class DataTitleinfo(models.Model):
    index = models.IntegerField(primary_key=True)
    title_id = models.TextField(db_column='title_ID', blank=True, null=True)  # Field name made lowercase.
    score = models.IntegerField(blank=True, null=True)
    knowledge = models.TextField(blank=True, null=True)
    sub_knowledge = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Data_TitleInfo'
