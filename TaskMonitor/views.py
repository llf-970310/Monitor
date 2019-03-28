import codecs
import json
import math
import smtplib
import sys
import traceback
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText

import apscheduler
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render, redirect
from lxml import etree

from TaskMonitor.forms import RegisterForm
from .models import *

# 切换输出流编码为utf-8
if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 开启定时器
scheduler = BackgroundScheduler()
scheduler.start()


# region Class
class Flight:
    def __init__(self, a, b, c, d, e):
        self.flightNo = a
        self.departDateTime = b
        self.arrivalDateTime = c
        self.departAirport = d
        self.arrivalAirport = e
        self.product = []

    def add_product(self, product):
        self.product.append(product)

    def display(self):
        print(self.flightNo + " " + self.departAirport + "(" + self.departDateTime + ")" + " -> " +
              self.arrivalAirport + "(" + self.arrivalDateTime + ")")
        self.product.sort(key=lambda item: item.salePrice)
        for i in range(len(self.product)):
            print(str(i + 1) + " " + self.product[i].display())


class Product:
    def __init__(self, a, b, c):
        self.productName = a
        self.salePrice = b
        self.discount = c

    def display(self):
        return self.productName + " " + str(self.salePrice) + " " + str(self.discount)


# endregion


# region View
def register(request):
    # 只有当请求为 POST 时，才表示用户提交了注册信息
    if request.method == 'POST':
        # request.POST 是一个类字典数据结构，记录了用户提交的注册信息
        # 这里提交的就是用户名（username）、密码（password）、邮箱（email）
        # 用这些数据实例化一个用户注册表单
        form = RegisterForm(request.POST)

        # 验证数据的合法性
        if form.is_valid():
            # 如果提交数据合法，调用表单的 save 方法将用户数据保存到数据库
            form.save()

            # 注册成功，跳转回首页
            return redirect('/monitor')
    else:
        # 请求不是 POST，表明用户正在访问注册页面，展示一个空的注册表单给用户
        form = RegisterForm()

    # 渲染模板
    # 如果用户正在访问注册页面，则渲染的是一个空的注册表单
    # 如果用户通过表单提交注册信息，但是数据验证不合法，则渲染的是一个带有错误信息的表单
    return render(request, 'register.html', context={'form': form})


@login_required
def setting(request):
    scheduler.print_jobs()
    context = {'title': 'Setting'}
    return render(request, 'setting.html', context)


@login_required
def view_flight_task(request):
    flight_task_list = Flight_Task.objects.filter(user_id=request.user.id)

    # 分页
    paginator = Paginator(flight_task_list, 5)
    page = request.GET.get('page')
    flight_tasks = paginator.get_page(page)

    context = {'flight_task_list': flight_tasks, 'title': 'Monitor - Flight Task'}
    return render(request, 'flight_task.html', context)


@login_required
def view_goods_task(request):
    goods_task_list = Goods_Task.objects.filter(user_id=request.user.id)

    # 分页
    paginator = Paginator(goods_task_list, 5)
    page = request.GET.get('page')
    goods_tasks = paginator.get_page(page)

    context = {'goods_task_list': goods_tasks, 'title': 'Monitor - Goods Task'}
    return render(request, 'goods_task.html', context)


@login_required
def get_airline_preview(request):
    if request.method == "POST":
        try:
            id = request.POST.get("id")
            flight_task = Flight_Task.objects.get(id=id)
            result = get_flight_ceair(flight_task, 0)
        except Exception as e:
            result = {'success': False}
            traceback.print_exc()
        return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def get_ebook_preview(request):
    if request.method == "POST":
        try:
            id = request.POST.get("id")
            goods_task = Goods_Task.objects.get(id=id)
            price = get_kindle_ebook_price(goods_task.goods_name)
            if price is not None:
                result = {'success': True, 'price': price}
            else:
                result = {'success': False, 'msg': 'No Book'}
        except Exception as e:
            result = {'success': False, 'msg': 'Runtime Error'}
            traceback.print_exc()
        return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def start_schedule(request):
    try:
        id = request.POST.get("id")
        task_type = request.POST.get("task_type")
        if task_type == "1":  # flight
            flight_task = Flight_Task.objects.get(id=id)
            interval = flight_task.frequency.split(' ')
            if interval[1] == "Hour" or interval[1] == "Hours":
                scheduler.add_job(get_flight_ceair, 'interval', hours=int(interval[0]),
                                  args=[flight_task, 1], id="flight_" + id)
            elif interval[1] == "Day":
                scheduler.add_job(get_flight_ceair, 'interval', days=int(interval[0]),
                                  args=[flight_task, 1], id="flight_" + id)
            flight_task.status = 1
            flight_task.save()
        elif task_type == "2":  # ebook
            goods_task = Goods_Task.objects.get(id=id)
            interval = goods_task.frequency.split(' ')
            if interval[1] == "Hour" or interval[1] == "Hours":
                scheduler.add_job(get_kindle_ebook_price, 'interval', hours=int(interval[0]),
                                  args=[goods_task], id="ebook_" + id)
            elif interval[1] == "Day":
                scheduler.add_job(get_kindle_ebook_price, 'interval', days=int(interval[0]),
                                  args=[goods_task], id="ebook_" + id)
            goods_task.status = 1
            goods_task.save()

        result = {'success': True}
    except Exception as e:
        traceback.print_exc()
        result = {'success': False, 'msg': 'Runtime Error'}
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def stop_schedule(request):
    try:
        id = request.POST.get("id")
        task_type = request.POST.get("task_type")
        if task_type == "1":  # flight
            scheduler.remove_job("flight_" + id)
            flight_task = Flight_Task.objects.get(id=id)
            flight_task.status = 0
            flight_task.save()
        elif task_type == "2":  # ebook
            scheduler.remove_job("ebook_" + id)
            goods_task = Goods_Task.objects.get(id=id)
            goods_task.status = 0
            goods_task.save()

        result = {'success': True}
    except Exception as e:
        traceback.print_exc()
        result = {'success': False, 'msg': 'Runtime Error'}
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def add_goods_task(request):
    try:
        task_name = request.POST.get("task_name")
        type = request.POST.get("type")
        book_name = request.POST.get("book_name")
        interval = request.POST.get("interval")
        enable_notif = request.POST.get("enable_notif")
        notif_condition = request.POST.get("notif_condition")
        price = request.POST.get("price")

        if enable_notif == "false":
            price = None
            notification_type = None
            flag = False
        elif enable_notif == "true":
            flag = True

        if notif_condition == "Greater(>)":
            notification_type = 1
        elif notif_condition == "Less(<)":
            notification_type = 2
        elif notif_condition == "Number changed":
            notification_type = 3
            price = None

        task_item = Goods_Task(task_name=task_name, goods_name=book_name, goods_type=type, frequency=interval,
                               enable_notification=flag, notification_type=notification_type, price=price,
                               user=request.user)
        task_item.save()
        result = {'success': True}
    except:
        result = {'success': False}
        traceback.print_exc()
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def add_flight_task(request):
    try:
        task_name = request.POST.get("task_name")
        airline_company = request.POST.get("airline_company")
        dept = request.POST.get("from")
        arr = request.POST.get("to")
        flight_date = request.POST.get("date")
        interval = request.POST.get("interval")
        enable_notif = request.POST.get("enable_notif")
        notif_condition = request.POST.get("notif_condition")
        price = request.POST.get("price")

        if enable_notif == "false":
            price = None
            notification_type = None
            flag = False
        elif enable_notif == "true":
            flag = True

        if notif_condition == "Greater(>)":
            notification_type = 1
        elif notif_condition == "Less(<)":
            notification_type = 2
        elif notif_condition == "Number changed":
            notification_type = 3
            price = None

        task_item = Flight_Task(task_name=task_name, dept_city=dept, arr_city=arr, flight_date=flight_date,
                                airline_company=airline_company, frequency=interval, enable_notification=flag,
                                notification_type=notification_type, price=price, user=request.user)
        task_item.save()
        result = {'success': True}
    except:
        result = {'success': False}
        traceback.print_exc()
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def get_goods_task_info(request):
    task_id = request.POST.get("id")
    task = Goods_Task.objects.get(id=task_id)
    return HttpResponse(json.dumps(model_to_dict(task)), content_type="application/json")


@login_required
def edit_goods_task(request):
    try:
        id = request.POST.get("id")
        task_name = request.POST.get("task_name")
        type = request.POST.get("type")
        book_name = request.POST.get("book_name")
        interval = request.POST.get("interval")
        enable_notif = request.POST.get("enable_notif")
        notif_condition = request.POST.get("notif_condition")
        price = request.POST.get("price")

        if enable_notif == "false":
            price = None
            notification_type = None
            flag = False
        elif enable_notif == "true":
            flag = True

        if notif_condition == "Greater(>)":
            notification_type = 1
        elif notif_condition == "Less(<)":
            notification_type = 2
        elif notif_condition == "Number changed":
            notification_type = 3
            price = None

        task = Goods_Task.objects.get(id=id)
        task.task_name = task_name
        task.goods_type = type
        task.goods_name = book_name
        task.frequency = interval
        task.enable_notification = flag
        task.notification_type = notification_type
        task.price = price
        task.save()

        result = {'success': True}
    except:
        result = {'success': False}
        traceback.print_exc()
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def del_goods_task(request):
    try:
        task_id = request.POST.get("id")
        Goods_Task.objects.get(id=task_id).delete()
        result = {'success': True}
    except:
        result = {'success': False}
        traceback.print_exc()
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
def del_flight_task(request):
    try:
        task_id = request.POST.get("id")
        Flight_Task.objects.get(id=task_id).delete()
        result = {'success': True}
    except:
        result = {'success': False}
        traceback.print_exc()
    return HttpResponse(json.dumps(result), content_type="application/json")


# endregion


# region Common Func
def get_ua():
    with open("./static/UA_list.txt") as fileua:
        uas = fileua.readlines()
        import random
        cnt = random.randint(0, len(uas) - 1)
        return uas[cnt].replace("\n", "")


def get_header():
    header = {
        'Referer': 'https://www.amazon.cn/',
        'User-agent': get_ua(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accetp-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'en-US,en;q=0.8'
    }
    return header


# 发送邮件
def send_email(subject, words):
    sender = 'lf97310@163.com'
    password = 'Lf4697323'
    receiver = ['543589863@qq.com', 'lf97310@163.com']

    msg = MIMEText(words, 'plain', 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')  # 邮件标题
    msg['from'] = sender  # 发信人地址
    msg['to'] = ','.join(receiver)  # 收信人地址

    smtp = smtplib.SMTP_SSL('smtp.163.com', 465, timeout=120)
    # smtp.connect('smtp-mail.outlook.com', 587)
    smtp.ehlo()
    # smtp.starttls()
    smtp.login(sender, password)
    smtp.sendmail(sender, receiver, msg.as_string())  # 这行代码解决的下方554的错误
    smtp.quit()
    print("==================邮件发送成功!==================")
# endregion


# region Flight Func
# 获取机场代码
def get_airport_cd(text):
    dict = {"上海": "PVG", "北京": "NAY"}
    if text in dict:
        return dict[text]
    else:
        return get_city_cd(text)


# 获取城市代码
def get_city_cd(text):
    f = open('./static/cityJSONCN.js', encoding='utf-8')
    tmp = json.load(f)
    f.close()
    city_code = {value: key for key, value in tmp.items()}
    return city_code[text]


# 东航
def get_flight_ceair(task, is_auto_generate):
    result = {}

    # 获取城市代码
    dept_cd = get_city_cd(task.dept_city)
    arr_cd = get_city_cd(task.arr_city)

    # 获取机场代码
    dept = get_airport_cd(task.dept_city)
    arr = get_airport_cd(task.arr_city)

    # 设置爬虫参数
    url = "http://www.ceair.com/otabooking/flight-search!doFlightSearch.shtml"
    values = {'searchCond': '{"segmentList":[{"deptCdTxt":"DEPT-TXT","deptCd":"DEPT","deptNation":"CN",'
                            '"deptRegion":"CN","deptCityCode":"DEPT-CITYCODE","arrCd":"ARR","arrCdTxt":"ARR-TXT",'
                            '"arrNation":"CN","arrRegion":"CN","arrCityCode":"ARR-CITYCODE","deptDt":"DATE"}],'
                            '"tripType":"OW","adtCount":"1","chdCount":"0","infCount":"0","currency":"CNY",'
                            '"sortType":"a","sortExec":"a"}'}
    values['searchCond'] = values['searchCond'].replace('DEPT-TXT', task.dept_city)
    values['searchCond'] = values['searchCond'].replace('ARR-TXT', task.arr_city)
    values['searchCond'] = values['searchCond'].replace('DEPT-CITYCODE', dept_cd)
    values['searchCond'] = values['searchCond'].replace('ARR-CITYCODE', arr_cd)
    values['searchCond'] = values['searchCond'].replace('DEPT', dept)
    values['searchCond'] = values['searchCond'].replace('ARR', arr)
    values['searchCond'] = values['searchCond'].replace('DATE', str(task.flight_date))

    try:
        # 爬虫获取数据
        req = requests.post(url, data=values, headers=get_header())
        req.encoding = "utf-8"
        temp = req.text
        text = json.loads(temp)

        # 解析数据
        if 'flightInfo' not in text.keys():  # 获取失败（可能原因：日期错误，网页抓取错误）
            task.status = -1
            task.save()
            scheduler.remove_job("flight_" + str(task.id))
            result['success'] = False
            result['msg'] = "无法获取%s从%s到%s的机票信息" % (str(task.flight_date), task.dept_city, task.arr_city)
        else:
            # 添加所有航班信息
            flight_list = []
            for flight_info in text['flightInfo']:
                flight = Flight(flight_info['flightNo'], flight_info['departDateTime'], flight_info['arrivalDateTime'],
                                task.dept_city + flight_info['departAirport']['codeContext'],
                                task.arr_city + flight_info['arrivalAirport']['codeContext'])
                flight_list.append(flight)

            # 添加所有产品信息
            for i in text['searchProduct']:
                flight_index = i['productGroupIndex']
                product_item = Product(i['productName'], i['salePrice'], i['discount'])
                flight_list[int(flight_index)].add_product(product_item)

            # 打印价格信息
            # for flight in flight_list:
            #     flight.display()

            # 获取最低价
            lowest_price_economy, lowest_price_business, lowest_price_luxury = float('inf'), float('inf'), float('inf')
            lowest_flight_economy, lowest_flight_business, lowest_flight_luxury = None, None, None

            for flight in flight_list:
                for product in flight.product:
                    if "公务" in product.productName and product.salePrice < lowest_price_business:
                        lowest_price_business = product.salePrice
                        lowest_flight_business = flight
                    elif "头等" in product.productName and product.salePrice < lowest_price_luxury:
                        lowest_price_luxury = product.salePrice
                        lowest_flight_luxury = flight
                    elif product.salePrice < lowest_price_economy:
                        lowest_price_economy = product.salePrice
                        lowest_flight_economy = flight

            lowest_flight_economy_dict, lowest_flight_business_dict, lowest_flight_luxury_dict = None, None, None
            if lowest_flight_economy is not None:
                lowest_flight_economy_dict = lowest_flight_economy.__dict__
                lowest_flight_economy_dict.pop("product", "404")
            if lowest_flight_business is not None:
                lowest_flight_business_dict = lowest_flight_business.__dict__
                lowest_flight_business_dict.pop("product", "404")
            if lowest_flight_luxury is not None:
                lowest_flight_luxury_dict = lowest_flight_luxury.__dict__
                lowest_flight_luxury_dict.pop("product", "404")

            lowest_price_economy = lowest_price_economy if not math.isinf(lowest_price_economy) else None
            lowest_price_business = lowest_price_business if not math.isinf(lowest_price_business) else None
            lowest_price_luxury = lowest_price_luxury if not math.isinf(lowest_price_luxury) else None

            result['success'] = True
            result['lowest_price_economy'] = lowest_price_economy
            result['lowest_price_business'] = lowest_price_business
            result['lowest_price_luxury'] = lowest_price_luxury
            result['lowest_flight_economy'] = lowest_flight_economy_dict
            result['lowest_flight_business'] = lowest_flight_business_dict
            result['lowest_flight_luxury'] = lowest_flight_luxury_dict

            # 发送邮件提醒
            if is_auto_generate == 1 and task.enable_notification == 1 and lowest_flight_economy is not None:
                if task.notification_type == 2 and float(lowest_price_economy) < task.price:
                    subject = "机票监控价格提醒"
                    content = '航班信息为：\n' \
                              + lowest_flight_economy.flightNo + " " \
                              + lowest_flight_economy.departAirport \
                              + "(" + lowest_flight_economy.departDateTime + ")" + " -> " \
                              + lowest_flight_economy.arrivalAirport \
                              + "(" + lowest_flight_economy.arrivalDateTime + ")\n" \
                              + '最低价格为 ' + str(lowest_price_economy)
                    send_email(subject, content)

            # 历史价格插入数据库
            if is_auto_generate == 1:
                history_data = Flight_Task_History(task=task, query_date=datetime.now(),
                                                   economy_lowest_price=lowest_price_economy,
                                                   business_lowest_price=lowest_price_business,
                                                   luxury_lowest_price=lowest_price_luxury)
                history_data.save()
    except Exception as e:
        task.status = -1
        task.save()
        scheduler.remove_job("flight_" + str(task.id))
        result['success'] = False
        result['msg'] = "运行过程中发生错误，机票数据获取失败"
        traceback.print_exc()
    return result
# endregion


# region Goods Func
# Kindle 电子书
def get_kindle_ebook_price(task):
    try:
        # 查询电子书价格
        header = get_header()
        with requests.session() as s:
            req = s.get('https://www.amazon.cn/', headers=header)
            cookie = requests.utils.dict_from_cookiejar(req.cookies)

        # 旧版数据获取，因为网站数据是JS动态加载，所以有时会获取不到数据
        # url = "https://www.amazon.cn/s/ref=nb_sb_noss?__mk_zh_CN=亚马逊网站&url=search-alias%3Ddigital-text&field-keywords=" + task.goods_name
        # data = requests.get(url=url, cookies=cookie, headers=header)
        # data.encoding = 'utf-8'
        # s = etree.HTML(data.text)
        # price = s.xpath('//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/a/span[2]/text()')

        url = "https://www.amazon.cn/mn/search/ajax/ref=nb_sb_noss?__mk_zh_CN=亚马逊网站&" \
              "url=search-alias%3Ddigital-text&field-keywords=" + task.goods_name
        data = requests.get(url=url, cookies=cookie, headers=header)
        data.encoding = 'utf-8'
        data_arr = data.text.split('&&&')
        result_html = json.loads(data_arr[7])['centerMinus']['data']['value']
        result_tree = etree.HTML(result_html)
        price = result_tree.xpath('//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/a/span[2]/text()')

        # 将历史价格插入数据库
        if len(price) == 0:
            result = -1
            task.status = -1
            task.save()
            scheduler.remove_job("ebook_" + str(task.id))
        else:
            result = price[0][1:]
            history_data = Goods_Task_History(task=task, query_date=datetime.now(), price=result)
            history_data.save()

        # 发送邮件提醒
        if task.enable_notification == 1 and result != -1:
            if task.notification_type == 2 and float(result) < task.price:
                subject = "Kindle 电子书价格提醒"
                content = "电子书《" + task.goods_name + "》的价格为 ￥" + result
                send_email(subject, content)
    except Exception:
        task.status = -1
        task.save()
        scheduler.remove_job("ebook_" + str(task.id))
        traceback.print_exc()
# endregion
