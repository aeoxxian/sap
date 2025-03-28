# Generated by Django 5.1.4 on 2025-02-09 17:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_remove_examresult_field1_remove_examresult_field2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='examresult',
            name='field1',
            field=models.FloatField(blank=True, null=True, verbose_name='분야별 점수 - Field1'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field1_definition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exam_results_field1', to='students.fielddefinition', verbose_name='분야1 이름'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field2',
            field=models.FloatField(blank=True, null=True, verbose_name='분야별 점수 - Field2'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field2_definition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exam_results_field2', to='students.fielddefinition', verbose_name='분야2 이름'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field3',
            field=models.FloatField(blank=True, null=True, verbose_name='분야별 점수 - Field3'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field3_definition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exam_results_field3', to='students.fielddefinition', verbose_name='분야3 이름'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field4',
            field=models.FloatField(blank=True, null=True, verbose_name='분야별 점수 - Field4'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field4_definition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exam_results_field4', to='students.fielddefinition', verbose_name='분야4 이름'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field5',
            field=models.FloatField(blank=True, null=True, verbose_name='분야별 점수 - Field5'),
        ),
        migrations.AddField(
            model_name='examresult',
            name='field5_definition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='exam_results_field5', to='students.fielddefinition', verbose_name='분야5 이름'),
        ),
        migrations.DeleteModel(
            name='ExamFieldResult',
        ),
    ]
