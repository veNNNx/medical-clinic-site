# Generated by Django 4.1.1 on 2022-10-16 21:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_visit_hours_remove_visit_minutes'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='time',
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
    ]
