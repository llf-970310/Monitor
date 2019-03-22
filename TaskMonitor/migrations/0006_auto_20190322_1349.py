# Generated by Django 2.1.2 on 2019-03-22 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TaskMonitor', '0005_auto_20190322_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight_task_history',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TaskMonitor.Flight_Task'),
        ),
        migrations.AlterField(
            model_name='goods_task_history',
            name='price',
            field=models.FloatField(verbose_name='价格'),
        ),
        migrations.AlterField(
            model_name='goods_task_history',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TaskMonitor.Goods_Task'),
        ),
    ]
