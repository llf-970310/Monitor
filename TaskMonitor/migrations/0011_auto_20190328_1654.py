# Generated by Django 2.1.2 on 2019-03-28 16:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TaskMonitor', '0010_auto_20190326_1713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight_task_history',
            name='business_lowest_price',
            field=models.IntegerField(null=True, verbose_name='商务舱最低价格'),
        ),
        migrations.AlterField(
            model_name='flight_task_history',
            name='economy_lowest_price',
            field=models.IntegerField(null=True, verbose_name='经济舱最低价格'),
        ),
        migrations.AlterField(
            model_name='flight_task_history',
            name='luxury_lowest_price',
            field=models.IntegerField(null=True, verbose_name='头等舱最低价格'),
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