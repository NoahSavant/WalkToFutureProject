from email import message
import math
from tkinter import messagebox
from xmlrpc.client import DateTime
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from numpy import size
from pytz import UTC, utc
from zmq import Message
from . import models
from .models import Customer
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.conf import settings
import random
from django.contrib.auth.models import User
from dateutil.relativedelta import relativedelta
# Create your views here.


def index(request):
    products = getTopProduct(8)
    return render(request, 'store/index.html', {
        'products' : products,
    })

def product_detail(request, slug):
    outOfStock = False
    if request.user.is_authenticated and request.method == "POST":
        sw = request.POST['sw']
        product = models.Product.objects.get(slug=slug)
        if sw == "atc":
            size = request.POST['radio_size']
            if size != "false":
                sqs = models.Size_Quantity.objects.filter(product=product, size=size)
                list = models.Cart.objects.filter(sq=sqs[0], user=request.user)
                if len(list) == 0:
                    new_cart = models.Cart()
                    new_cart.sq = sqs[0]
                    new_cart.user = request.user
                    new_cart.save()
                else:
                    list[0].quantity = list[0].quantity + 1
                    list[0].save()
            else:
                outOfStock = True
        elif sw == "comment":
            comment = request.POST['comment']
            comment = comment.strip(" ")
            if comment != "":
                fb = models.Feedback()
                fb.product = product
                fb.user = request.user
                fb.comment = comment
                fb.time = datetime.now().strftime("%m/%d/%Y")
                fb.save()
    product = models.Product.objects.get(slug=slug)
    size_quantity = models.Size_Quantity.objects.filter(product=product).order_by('size')
    feedbacks = models.Feedback.objects.filter(product=product)
    return render(request, 'store/product-detail.html', {
        'size_quantity': size_quantity,
        'feedbacks': feedbacks,
        'outOfStock':outOfStock
    })

def register_successfully(request):
    return render(request,'store/RegisterSuccessfully.html')

def register(request):
    # don't allow user to go back register page when already login
    if request.user.is_authenticated:
        return redirect('index')
    form = RegisterForm()
    exists = False
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if User.objects.filter(email=request.POST.get('email')).exists() or User.objects.filter(username=request.POST.get('username')).exists() :
            exists = True
        if form.is_valid() and not exists:
            a = []
            for i in range(4):
                a.append(str(random.randint(0,9)))

            pin = ''.join(a)

            emailUser = request.POST.get('email')
            first_nameUser = request.POST.get('first_name')
            subject = 'This is your confirm PIN'
            body = 'Your verification code is: '+ pin
            from_email = settings.EMAIL_HOST_USER
            to_list = [emailUser]
            email = EmailMessage(
                subject,
                body,
                from_email,
                to_list
            )
            email.fail_silently=False
            email.send()
           
            form.save()
            list = Customer.objects.all()
            customer = list[len(list)-1]
            customer.gender = request.POST['gender']
            customer.city = request.POST['city']
            customer.country = request.POST['country']
            customer.save()
            request.session['pin'] = pin
            request.session['emailUser']= emailUser
            request.session['username']=  request.POST.get('username')

            return redirect('verify')
    context = {'form':form,
              'exist':exists}
    return render(request,'store/register.html',context)

def login(request):
    # don't allow user to go back login page when already login
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth_login(request,user)
            if request.user.has_perm('Staff status'):
                return redirect('http://127.0.0.1:8000/admin/')
            return redirect('index')
        else:
            return render(request, 'store/signin.html', {'error': True})
    return render(request,'store/signin.html', {'error': False})

def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        if request.method == "POST":
            id = request.POST.get("id")
            type = request.POST.get("type")
            remove = request.POST.get("remove")
            result = models.Cart.objects.filter(id=id)
            if len(result) > 0:
                order = result[0]
                if remove == 'True':
                    order.delete()
                else:
                    if type == "plus":
                        order.plus()
                    elif type == "minus":
                        order.minus()
                    if order.quantity == 0:
                        order.delete()
                    else:
                        order.save()
        orders = models.Cart.objects.filter(user=customer)
        total = 0
        for item in orders:
            total = total + item.total
    else:
        return redirect('login')
    context = {'orders':orders, 'total': total}
    return render(request,'store/cart.html',context)

def getNumber(str):
    emp_lis = ''
    for z in str:
        if z.isdigit():
            emp_lis = emp_lis + z
   
    return int(emp_lis)

def store(request, brandCategory, sizeCategory, priceCategory,searchCategory):
    if searchCategory == 'All':
        searchCategory = ''
    if sizeCategory == "All" or sizeCategory == '[]':       
        sizeCategory = []
    if priceCategory == "All":
        priceCategory = ['0','10000']
    products = models.Product.objects.filter(name__contains=searchCategory)

    # Get objects by brand catetory
    if brandCategory == "All":
        _list = products
    else:
        _list = models.Product.objects.filter(brand= brandCategory)
    # end get objects by brand catetory

    # get distinct brand and size 
    sizeQuantity = models.Size_Quantity.objects.all()
    brand = ["All"]
    size = []

    for pro in products:
        if pro.brand not in brand:
            brand.append(pro.brand)

    for pro in sizeQuantity:
        if str(pro.size) not in size:
            size.append(str(pro.size))
    # end get distinct brand and size 

    if request.method=="POST":
        sizeCategory = request.POST.getlist('sizeCategory')
        min = request.POST.get('min')
        max = request.POST.get('max')
        priceCategory = [min,max]

    # filter by size
    if len(sizeCategory) > 0:
        list = []
        for item in sizeQuantity:
            if str(item.size) in sizeCategory and item.product not in list and item.product in _list:   
                list.append(item.product)
    else:
        list = _list
    #end filter by size

    #filter by price
    if priceCategory == [None, None]:
        priceCategory = ['0', '10000']
    _min = getNumber(str(priceCategory).split(',')[0])
    _max = getNumber(str(priceCategory).split(',')[1])
    priceCategory = [str(_min),str(_max)]
    priceList = []
    
    for item in list:
        if item.price >= _min and item.price <= _max:
            priceList.append(item)    
    list = priceList
    #end filter by price

    # sort size   
    size.sort()

    if request.method == 'POST':
        flag = request.POST.get('flag')
        if flag == 'true':
            searchCategory = request.POST.get('search')
            list = models.Product.objects.filter(name__contains=searchCategory)

    # page paginator
    product_paginator = Paginator(list,6)
    page_num = request.GET.get('page')
    
    pages = product_paginator.get_page(page_num)
    # end page paginator

    listMin = ['0','50','70','100','200','500','1000']
    listMax = ['50','70','100','200','500','1000','10000']
    if searchCategory == "":
        searchCategory = 'All'
    context = {
        'product': products,
        'page':pages,    
        'itemFound': len(list),
        'brand': brand,
        'size': size,
        'listBrandCategory': brandCategory,
        'listSizeCategory': sizeCategory,
        'listPriceCategory':priceCategory,
        'listMin':listMin,
        'listMax':listMax,
        'search': searchCategory
    }
    return render(request,'store/store.html',context)

@login_required(login_url='login')
def place_order(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            request.session['phone'] = request.POST.get('phone')
            request.session['address'] = request.POST.get('address')
            return redirect("order_complete")
        list = models.Cart.objects.filter(user= request.user)
        total = 0
        for item in list:
            total = total + item.total
    context = {'review_list': list, 'total': total, }
    return render(request,'store/place-order.html', context)

@login_required(login_url='login')
def order_complete(request):
    phone = request.session['phone']
    address = request.session['address']
    customer = models.Customer.objects.get(user=request.user)
    info = {}
    info['order'] = request.user.id
    info['date'] = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    orders = models.Cart.objects.filter(user=request.user)
    odersNew = orders
    total = 0
    time =  datetime.now()
    for order in orders:
        total = total + order.total
        bill = models.Bill()
        bill.sq = order.sq
        bill.user = request.user
        bill.checkout_date = time
        bill.quantity = order.quantity
        bill.save()
        sq = models.Size_Quantity.objects.get(product=order.sq.product, size = order.sq.size)
        sq.quantity = sq.quantity - order.quantity
        sq.save() 

        product = models.Product.objects.get(id = order.sq.product.id)
        product.sold =  product.sold + order.quantity
        product.save()
        order.delete()

    return render(request,'store/order_complete.html', {
        'phone': phone,
        'address': address,
        'customer': customer,
        'orders': odersNew,
        'total': total,
        'info': info
    })

def verify(request):
    error = False
    count = 0
    if request.method == 'POST':
        try :
            count = int(request.POST.get('count'))
        except TypeError:
            print("typeError")
            return render(request,'store/verify.html',
            {
                'error':error,
                'count':count
            })
        pin = request.POST.get('pin')
        if pin == request.session['pin']:
            subject = 'REGISTER SUCCESSFULLY'
            body = render_to_string('store/RegisterSuccessfully.html')
            from_email = settings.EMAIL_HOST_USER
            to_list = [request.session["emailUser"]]
            email = EmailMessage(
                subject,
                body,
                from_email,
                to_list
            )
            email.fail_silently=False
            email.content_subtype = 'html'
            email.send()
            return render(request,'store/RegisterSuccessfully.html')
        else:
            count = count + 1
            error = True
            if count == 4:
                user = User.objects.get(username = request.session['username'])
                user.delete()
                return redirect('register')
    return render(request,'store/verify.html',{
        'error':error,
        'count':count
        })

def contact(request):
    success = False
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        subject = request.POST.get('subject')
        body = 'From email: '+ email + '\nName: '+ name+ '\nMessage: ' + request.POST.get('message')
        from_email = settings.EMAIL_HOST_USER
        to_list = ['walktofuturecontact@gmail.com']
        email = EmailMessage(
            subject,
            body,
            from_email,
            to_list
        )
        email.fail_silently=False
        email.send()
        success = True

    return render(request,'store/contact.html',{'success':success})

@login_required(login_url='login')
def profile(request):
    edit = False
    cus = models.Customer.objects.get(user=request.user)
    if request.method == 'POST':
        type = request.POST.get('type')
        if type == 'edit':
            edit = True
        else:
            request.user.first_name = request.POST.get('first_name')
            request.user.last_name = request.POST.get('last_name')
            request.user.save()
            cus.city = request.POST.get('city')
            cus.country = request.POST.get('country')
            cus.gender = request.POST.get('gender')
            cus.save()
            edit = False
    country = ['Việt Nam', 'United States', 'Russia']
    bills = models.Bill.objects.filter(user=request.user)
    date = []
    list = []
    bill = []
    total = 0
    for item in bills:
        if item.checkout_date not in date:
            if len(bill) != 0:
                list.append({'bills': bill,'total': total})
            date.append(item.checkout_date)
            bill = [item]
            total = item.total
        else:
            bill.append(item)
            total = total + item.total

    list.append({'bills': bill,'total': total})
    list = list[::-1]
    list = list[:3]
    return render(request,'store/profile.html', {
        'cus': cus,
        'country': country,
        'edit': edit,
        'bill_list': list
    })

def getTopProduct(top):
    return models.Product.objects.all().order_by('-sold')[:top]

@login_required(login_url='login')
def dashboard(request):

    user = request.user
    products = getTopProduct(10)
    avg = 0.0

    for item in products:
        avg = avg + item.sold
    avg = avg / 10

    size_quantity = models.Size_Quantity.objects.all()
    sq= []
    for pro in products:
        if len(sq)<3:
            pro.statitic =  pro.sold / avg 
            pro.save()
            size_quantity = models.Size_Quantity.objects.filter(product = pro)
            sq.append(size_quantity[0])
        else:
            break
    order = []
    totalProduct = 0 # for customer
    adminState = False
    if request.user.has_perm('Staff status'):
        bill = models.Bill.objects.all()
        adminState = True
    else:
        bill = models.Bill.objects.filter(user = user)
        order1 = models.Bill.objects.filter(user = user).order_by('-checkout_date')[0]
        order =  models.Bill.objects.filter(user = user, checkout_date = order1.checkout_date)
        print(order)
        for b in bill:
            totalProduct = totalProduct + b.quantity
    today = datetime.now()
    # get date last week
    thisWeek = [
       0, #Mo
       0, #Tu
       0, #We
       0, #Th
       0, #Fr
       0, #Sa
       0, #Su
    ]
    lastWeek = [
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    thisYear = [
        0, #jan
        0, #feb
        0, #march
        0, #april
        0, #May
        0, #june
        0, #junly
        0, #August
        0, #September
        0, #october
        0, #november
        0, #december
            
    ]
    lastYear = [
        0, #jan
        0, #feb
        0, #march
        0, #april
        0, #May
        0, #june
        0, #junly
        0, #August
        0, #September
        0, #october
        0, #november
        0, #december
    ]



    #this week
    for b in bill:
        b.checkout_date = b.checkout_date.replace(tzinfo=None) 
        if  b.checkout_date <= (today - timedelta(days=0)) and  b.checkout_date >= (today - timedelta(days=today.weekday()+1)):
            for i in range(0,today.weekday()+1):
                time = today-timedelta(days=i)
                if b.checkout_date.date() == time.date():
                   thisWeek[today.weekday()-i]+=b.quantity

   # last week   
    for b in bill:
        b.checkout_date = b.checkout_date.replace(tzinfo=None) 
        if  b.checkout_date <= (today - timedelta(days=today.weekday()+1)) and  b.checkout_date >= (today - timedelta(days=today.weekday()+8)):
            for i in range(today.weekday()+1,today.weekday()+8):
                time = today-timedelta(days=i)
                if b.checkout_date.date() == time.date():
                   lastWeek[today.weekday()-i]+=b.quantity

    #total this week sold product
    totalSalesWeek = 0
    for i in thisWeek:
        totalSalesWeek = totalSalesWeek + i

    #totla last week sold product

    totalSalesLastWeek = 0
    for i in lastWeek:
        totalSalesLastWeek = totalSalesLastWeek + i

    #stonk product this week
    if totalSalesLastWeek != 0:
        thisWeekStonk = (totalSalesWeek / totalSalesLastWeek)*100
    else:
        thisWeekStonk = 0

    totalSales = totalSalesWeek 
    if (totalSalesWeek / totalSalesLastWeek) >= 1 or thisWeekStonk == 0:
        stonkUp = True 
    else:
        stonkUp = False 

    #total this year profits
    totalProfitsYear = 0

    #total last year profits
    totalProfitsLastYear = 0

    #total this month profit 
    totalProfitMonth = 0

    #total last month profit 
    totalProfitLastMonth = 0

    #total profit
    totalProfit = 0

    billThisMonth = []
    billLastMonth = []

    # sales

    #this year
    for b in bill:
        b.checkout_date = b.checkout_date.replace(tzinfo=None) 
        if b.checkout_date <= (today - relativedelta(years=0)) and b.checkout_date >=  datetime(date.today().year, 1, 1):
            totalProfitsYear = totalProfitsYear + b.total
            for i in range(1,12):
                if b.checkout_date >= datetime(date.today().year, i, 1) and b.checkout_date < datetime(date.today().year, i+1, 1):
                    if i == date.today().month:
                        billThisMonth.append(b)
                    elif i ==(date.today().month - 1 ):
                        billLastMonth.append(b)
                    thisYear[i-1]+=b.total

    #last year
    for b in bill:
        b.checkout_date = b.checkout_date.replace(tzinfo=None) 
        if b.checkout_date >= datetime(date.today().year-1, 1, 1) and  b.checkout_date <= datetime(date.today().year-1, 12, 31):
            totalProfitsLastYear =totalProfitsLastYear + b.total
            for i in range(1,12):
                if b.checkout_date >= datetime(date.today().year-1, i, 1) and b.checkout_date < datetime(date.today().year-1, i+1, 1):
                    lastYear[i-1]+=b.total

    totalYearProfit =  totalProfitsYear
    #stonk profit this year

    if totalProfitsLastYear != 0:
        thisYearStonk = totalYearProfit / totalProfitsLastYear
    else:
        thisYearStonk = 0
    
    #total profit month
    for i in billThisMonth:
        totalProfitMonth = totalProfitMonth + i.total

    #total profit last month
    for i in billLastMonth:
        totalProfitLastMonth = totalProfitLastMonth + i.total
    
    #stonk profit this month
    if totalProfitLastMonth !=0:
        thisMonthStonk = (totalProfitMonth / totalProfitLastMonth)*100
    else:
        thisMonthStonk = 0


    if (totalProfitMonth / totalProfitLastMonth) >= 1 or thisMonthStonk == 0:
        profitStonkUp = True 
    else:
        profitStonkUp = False 


    monthLabel2 = ['AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    monthLabel1 = ['JAN','FEB','MAC','APR','MAY','JUN','JUL']
    if today.month >= 6:
        thisYear1 = thisYear[7:13]
        lastYear1 = lastYear1[7:13]
        monthLabel = monthLabel2
    else:
        thisYear1=thisYear[:7]
        lastYear1 = lastYear[:7]
        monthLabel = monthLabel1

    cus = models.Customer.objects.all()

    thisYear1 = [round(num, 2) for num in thisYear1]
    lastYear1 = [round(num, 2) for num in lastYear1]

    context = {'sizeQuantity':sq,
                'thisWeek':thisWeek,
                'lastWeek':lastWeek,
                'thisYear':thisYear1,
                'lastYear':lastYear1,
                'monthLabel':monthLabel,
                'totalWeek':totalSales,
                'thisWeekStonk': thisWeekStonk,
                'stonkUp':stonkUp,
                'totalProfit':totalYearProfit,
                'thisMonthStonk':thisMonthStonk,
                'profitStonkUp':profitStonkUp,
                'customerCount':cus.count(),
                'adminState':adminState,
                'order':order,
                'totalProduct':totalProduct
                }

    
    return render(request,'store/dashboard.html',context)
