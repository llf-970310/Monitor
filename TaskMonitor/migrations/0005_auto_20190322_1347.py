# Generated by Django 2.1.2 on 2019-03-22 05:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TaskMonitor', '0004_flight_task_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goods_Task_History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_date', models.DateTimeField(verbose_name='查询时间')),
                ('price', models.IntegerField(verbose_name='价格')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TaskMonitor.Goods_Task')),
            ],
        ),
        migrations.AlterField(
            model_name='flight_task_history',
            name='query_date',
            field=models.DateTimeField(verbose_name='查询时间'),
        ),
        migrations.AlterField(
            model_name='flight_task_history',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TaskMonitor.Flight_Task'),
        ),
    ]