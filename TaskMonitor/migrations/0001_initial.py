# Generated by Django 2.1.2 on 2019-03-20 02:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='flight_task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.TextField(verbose_name='任务名称')),
                ('dept_city', models.TextField(verbose_name='始发地')),
                ('arr_city', models.TextField(verbose_name='到达地')),
                ('flight_date', models.DateField(verbose_name='航班日期')),
                ('frequency', models.TextField(verbose_name='查询频率')),
                ('enable_notification', models.BooleanField(verbose_name='是否提醒')),
                ('notification_type', models.IntegerField(verbose_name='提醒类型')),
                ('price', models.IntegerField(verbose_name='价格')),
                ('status', models.IntegerField(verbose_name='状态')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='goods_task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.TextField(verbose_name='任务名称')),
                ('goods_name', models.TextField(verbose_name='商品名称')),
                ('goods_type', models.IntegerField(verbose_name='商品类型')),
                ('frequency', models.TextField(verbose_name='查询频率')),
                ('enable_notification', models.BooleanField(verbose_name='是否提醒')),
                ('notification_type', models.IntegerField(verbose_name='提醒类型')),
                ('price', models.IntegerField(verbose_name='价格')),
                ('status', models.IntegerField(verbose_name='状态')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]