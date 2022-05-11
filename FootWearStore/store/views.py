from email import message
from tkinter import messagebox
from xmlrpc.client import DateTime
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from numpy import size
from zmq import Message
from . import models
from .models import Customer
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.conf import settings
import random
from django.contrib.auth.models import User
# Create your views here.


def index(request):
    products = models.Product.objects.filter(status="Hot")
    return render(request, 'store/index.html', {
        'products' : products,
    })

def product_detail(request, slug):
    if request.user.is_authenticated and request.method == "POST":
        sw = request.POST['sw']
        product = models.Product.objects.get(slug=slug)
        if sw == "atc":
            size = request.POST['radio_size']
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
    size_quantity = models.Size_Quantity.objects.filter(product=product)
    feedbacks = models.Feedback.objects.filter(product=product)
    return render(request, 'store/product-detail.html', {
        'size_quantity': size_quantity,
        'first':size_quantity[0],
        'feedbacks': feedbacks,
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
    product_paginator = Paginator(list,1)
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
    context = {'list': list, 'total': total, }
    return render(request,'store/place-order.html', context)

@login_required(login_url='login')
def order_complete(request):
    phone = request.session['phone']
    address = request.session['address']
    customer = models.Customer.objects.get(user=request.user)
    info = {}
    info['order'] = request.user.id
    info['date'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
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
        'list': list
    })

