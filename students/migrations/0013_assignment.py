# Generated by Django 5.1.4 on 2025-02-17 18:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0012_exam_avg_field1_exam_avg_field2_exam_avg_field3_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='날짜')),
                ('title', models.CharField(max_length=200, verbose_name='과제명')),
                ('description', models.TextField(blank=True, verbose_name='과제 내용')),
                ('completion_rate', models.FloatField(default=0.0, verbose_name='이행률')),
                ('class_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='students.classgroup', verbose_name='분반')),
            ],
            options={
                'verbose_name': '과제',
                'verbose_name_plural': '과제 목록',
            },
        ),
    ]
