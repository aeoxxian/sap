# Generated by Django 5.1.4 on 2025-02-09 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_remove_examresult_score_examresult_exam_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='examresult',
            name='report_link',
            field=models.URLField(blank=True, null=True, verbose_name='보고서 링크'),
        ),
    ]
