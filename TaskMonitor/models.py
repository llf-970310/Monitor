from django.conf import settings
from django.db import models


class Flight_Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task_name = models.TextField("任务名称")
    dept_city = models.TextField("始发地")
    arr_city = models.TextField("到达地")
    flight_date = models.DateField("航班日期")
    airline_company = models.TextField("航空公司")
    frequency = models.TextField("查询频率")
    enable_notification = models.BooleanField("是否提醒")
    # 1 Greater(>)  2 Less(<)  3 Number changed
    notification_type = models.IntegerField("提醒类型")
    price = models.IntegerField("价格")
    # 0 停止  1 运行  -1 错误
    status = models.IntegerField("状态")


class Goods_Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task_name = models.TextField("任务名称")
    goods_name = models.TextField("商品名称")
    # 1 Kindle  2 Taobao
    goods_type = models.IntegerField("商品类型")
    frequency = models.TextField("查询频率")
    enable_notification = models.BooleanField("是否提醒")
    notification_type = models.IntegerField("提醒类型", null=True)
    price = models.FloatField("价格", null=True)
    status = models.IntegerField("状态", default=0)


class Flight_Task_History(models.Model):
    task = models.ForeignKey('Flight_Task', on_delete=models.CASCADE)
    query_date = models.DateTimeField("查询时间")
    economy_lowest_price = models.IntegerField("经济舱最低价格")
    business_lowest_price = models.IntegerField("商务舱最低价格")
    luxury_lowest_price = models.IntegerField("头等舱最低价格")


class Goods_Task_History(models.Model):
    task = models.ForeignKey('Goods_Task', on_delete=models.CASCADE)
    query_date = models.DateTimeField("查询时间")
    price = models.FloatField("价格")
