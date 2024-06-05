# Generated by Django 5.0.6 on 2024-06-05 03:00

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DataStudentinfo",
            fields=[
                ("index", models.IntegerField(primary_key=True, serialize=False)),
                (
                    "student_id",
                    models.TextField(blank=True, db_column="student_ID", null=True),
                ),
                ("sex", models.TextField(blank=True, null=True)),
                ("age", models.IntegerField(blank=True, null=True)),
                ("major", models.TextField(blank=True, null=True)),
            ],
            options={
                "db_table": "Data_StudentInfo",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DataSubmitrecord",
            fields=[
                ("index", models.IntegerField(primary_key=True, serialize=False)),
                (
                    "class_field",
                    models.TextField(blank=True, db_column="class", null=True),
                ),
                ("time", models.IntegerField(blank=True, null=True)),
                ("state", models.TextField(blank=True, null=True)),
                ("score", models.IntegerField(blank=True, null=True)),
                (
                    "title_id",
                    models.TextField(blank=True, db_column="title_ID", null=True),
                ),
                ("method", models.TextField(blank=True, null=True)),
                ("memory", models.IntegerField(blank=True, null=True)),
                ("timeconsume", models.TextField(blank=True, null=True)),
                (
                    "student_id",
                    models.TextField(blank=True, db_column="student_ID", null=True),
                ),
            ],
            options={
                "db_table": "Data_SubmitRecord",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="DataTitleinfo",
            fields=[
                ("index", models.IntegerField(primary_key=True, serialize=False)),
                (
                    "title_id",
                    models.TextField(blank=True, db_column="title_ID", null=True),
                ),
                ("score", models.IntegerField(blank=True, null=True)),
                ("knowledge", models.TextField(blank=True, null=True)),
                ("sub_knowledge", models.TextField(blank=True, null=True)),
            ],
            options={
                "db_table": "Data_TitleInfo",
                "managed": False,
            },
        ),
    ]
