import codecs
import json
import smtplib
import sys
import traceback
from email.header import Header
from email.mime.text import MIMEText

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from lxml import etree

from TaskMonitor.forms import RegisterForm
from .models import Flight_Task, Goods_Task

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
        print(self.flightNo + " " + self.departAirport + "(" +self.departDateTime + ")" + " -> " +
              self.arrivalAirport + "(" + self.arrivalDateTime + ")")
        self.product.sort(key=lambda item: item.salePrice)
        for i in range(len(self.product)):
            print(str(i+1) + " " + self.product[i].display())


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
            # return redirect('/clipping')
    else:
        # 请求不是 POST，表明用户正在访问注册页面，展示一个空的注册表单给用户
        form = RegisterForm()

    # 渲染模板
    # 如果用户正在访问注册页面，则渲染的是一个空的注册表单
    # 如果用户通过表单提交注册信息，但是数据验证不合法，则渲染的是一个带有错误信息的表单
    return render(request, 'register.html', context={'form': form})


@login_required
def view_flight_task(request):
    flight_task_list = Flight_Task.objects.all()

    # 分页
    paginator = Paginator(flight_task_list, 5)
    page = request.GET.get('page')
    flight_tasks = paginator.get_page(page)

    context = {'flight_task_list': flight_tasks, 'title': 'Monitor'}
    return render(request, 'flight_task.html', context)


@login_required
def view_goods_task(request):
    goods_task_list = Goods_Task.objects.all()

    # 分页
    paginator = Paginator(goods_task_list, 5)
    page = request.GET.get('page')
    goods_tasks = paginator.get_page(page)

    context = {'goods_task_list': goods_tasks, 'title': 'Goods Task'}
    return render(request, 'goods_task.html', context)


@login_required
def get_airline_preview(request):
    if request.method == "POST":
        try:
            id = request.POST.get("id")
            flight_task = Flight_Task.objects.get(id=id)
            result = get_flight_ceair(flight_task.dept_city, flight_task.arr_city, str(flight_task.flight_date))
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
            pass
        elif task_type == "2":  # ebook
            goods_task = Goods_Task.objects.get(id=id)
            scheduler.add_job(get_kindle_ebook_price, 'interval', seconds=30,
                              args=[goods_task.goods_name], id="ebook_" + id)
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
            pass
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


def get_ua():
    with open("./static/UA_list.txt") as fileua:
        uas = fileua.readlines()
        import random
        cnt = random.randint(0,len(uas)-1)
        return uas[cnt].replace("\n","")


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
def send_email(flight, price):
    sender = 'lf97310@163.com'
    password = 'Lf4697323'
    receiver = ['543589863@qq.com', 'lf97310@163.com']
    subject = '机票低价提醒'
    words = '航班信息为：\n' \
            + flight.flightNo + " " + flight.departAirport + "(" +flight.departDateTime + ")" + " -> " \
            + flight.arrivalAirport + "(" + flight.arrivalDateTime + ")\n" \
            + '最低价格为 ' + str(price)

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


# 东航
def get_flight_ceair(dept_text, arr_text, date):
    result = {}

    # 获取城市代码
    dept_cd = get_city_cd(dept_text)
    arr_cd = get_city_cd(arr_text)

    # 获取机场代码
    dept = get_airport_cd(dept_text)
    arr = get_airport_cd(arr_text)

    # 设置爬虫参数
    url = "http://www.ceair.com/otabooking/flight-search!doFlightSearch.shtml"
    values = {'searchCond': '{"segmentList":[{"deptCdTxt":"DEPT-TXT","deptCd":"DEPT","deptNation":"CN",'
                            '"deptRegion":"CN","deptCityCode":"DEPT-CITYCODE","arrCd":"ARR","arrCdTxt":"ARR-TXT",'
                            '"arrNation":"CN","arrRegion":"CN","arrCityCode":"ARR-CITYCODE","deptDt":"DATE"}],'
                            '"tripType":"OW","adtCount":"1","chdCount":"0","infCount":"0","currency":"CNY",'
                            '"sortType":"a","sortExec":"a"}'}
    values['searchCond'] = values['searchCond'].replace('DEPT-TXT', dept_text)
    values['searchCond'] = values['searchCond'].replace('ARR-TXT', arr_text)
    values['searchCond'] = values['searchCond'].replace('DEPT-CITYCODE', dept_cd)
    values['searchCond'] = values['searchCond'].replace('ARR-CITYCODE', arr_cd)
    values['searchCond'] = values['searchCond'].replace('DEPT', dept)
    values['searchCond'] = values['searchCond'].replace('ARR', arr)
    values['searchCond'] = values['searchCond'].replace('DATE', date)

    try:
        # 爬虫获取数据
        req = requests.post(url, data=values, headers=get_header())
        req.encoding = "utf-8"
        temp = req.text
        text = json.loads(temp)

        # 解析数据
        if 'flightInfo' not in text.keys():
            print("==================无法获取%s从%s到%s的机票信息==================" % (date, dept_text, arr_text))
            result['success'] = False
        else:
            print('==================获取机票数据成功==================')

            # 添加所有航班信息
            flight_list = []
            for flight_info in text['flightInfo']:
                flight = Flight(flight_info['flightNo'], flight_info['departDateTime'], flight_info['arrivalDateTime'],
                                dept_text + flight_info['departAirport']['codeContext'],
                                arr_text + flight_info['arrivalAirport']['codeContext'])
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
            lowest_price_economy = 1234567
            lowest_price_business = 1234567
            lowest_price_luxury = 1234567
            lowest_flight_economy = None
            lowest_flight_business = None
            lowest_flight_luxury = None

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

            lowest_flight_economy_dict = lowest_flight_economy.__dict__
            lowest_flight_economy_dict.pop("product")
            lowest_flight_business_dict = lowest_flight_business.__dict__
            lowest_flight_business_dict.pop("product")
            lowest_flight_luxury_dict = lowest_flight_luxury.__dict__
            lowest_flight_luxury_dict.pop("product")

            result['success'] = True
            result['lowest_price_economy'] = lowest_price_economy
            result['lowest_price_business'] = lowest_price_business
            result['lowest_price_luxury'] = lowest_price_luxury
            result['lowest_flight_economy'] = lowest_flight_economy_dict
            result['lowest_flight_business'] = lowest_flight_business_dict
            result['lowest_flight_luxury'] = lowest_flight_luxury_dict
    except Exception as e:
        result['success'] = False
        print("==================获取机票数据失败！==================")
        traceback.print_exc()
    return result


# Kindle 电子书
def get_kindle_ebook_price(book_name):
    header = get_header()
    with requests.session() as s:
        req = s.get('https://www.amazon.cn/', headers=header)
        cookie = requests.utils.dict_from_cookiejar(req.cookies)
    url = "https://www.amazon.cn/s/ref=nb_sb_noss?__mk_zh_CN=亚马逊网站&url=search-alias%3Ddigital-text&field-keywords=" + book_name
    data = requests.get(url=url, cookies=cookie, headers=header)
    data.encoding = 'utf-8'
    s = etree.HTML(data.text)
    price = s.xpath('//*[@id="result_0"]/div/div/div/div[2]/div[2]/div[1]/div[2]/a/span[2]/text()')
    if len(price) == 0:
        return None
    return price[0][1:]

# endregion
