# Generated by Django 5.1.4 on 2025-02-09 17:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_fielddefinition_examfieldresult'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examresult',
            name='field1',
        ),
        migrations.RemoveField(
            model_name='examresult',
            name='field2',
        ),
        migrations.RemoveField(
            model_name='examresult',
            name='field3',
        ),
        migrations.RemoveField(
            model_name='examresult',
            name='field4',
        ),
        migrations.RemoveField(
            model_name='examresult',
            name='field5',
        ),
        migrations.RemoveField(
            model_name='examresult',
            name='report_link',
        ),
        migrations.AlterField(
            model_name='examfieldresult',
            name='score',
            field=models.FloatField(blank=True, null=True, verbose_name='점수'),
        ),
    ]
