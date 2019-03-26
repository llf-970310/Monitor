# Generated by Django 2.1.2 on 2019-03-26 17:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TaskMonitor', '0009_auto_20190322_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight_task',
            name='notification_type',
            field=models.IntegerField(null=True, verbose_name='提醒类型'),
        ),
        migrations.AlterField(
            model_name='flight_task',
            name='price',
            field=models.IntegerField(null=True, verbose_name='价格'),
        ),
        migrations.AlterField(
            model_name='flight_task',
            name='status',
            field=models.IntegerField(default=0, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='flight_task_history',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TaskMonitor.Flight_Task'),
        ),
        migrations.AlterField(
            model_name='goods_task_history',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TaskMonitor.Goods_Task'),
        ),
    ]
