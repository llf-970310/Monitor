# Generated by Django 2.1.2 on 2019-03-20 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TaskMonitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flight_task',
            name='airline_company',
            field=models.TextField(default='1', verbose_name='航空公司'),
        ),
    ]
