from email import message
from django.http import HttpResponse
from django.shortcuts import redirect, render
from numpy import size
from . import models
from .models import Customer
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.paginator import Paginator
# Create your views here.


def index(request):
    products = models.Product.objects.all()
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
                cart = models.Cart()
                cart.sq=sqs[0]
                cart.user=request.user
                cart.save()
            else:
                list[0].quantity = list[0].quantity + 1
                list[0].save()
        elif sw == "comment":
            comment = request.POST['comment']
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

def register(request):
    # don't allow user to go back register page when already login
    if request.user.is_authenticated:
        return redirect('index')
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            list = Customer.objects.all()
            customer = list[len(list)-1]
            customer.gender = request.POST['gender']
            customer.city = request.POST['city']
            customer.country = request.POST['country']
            customer.save()
            return redirect('login')
    context = {'form':form}
    return render(request,'store/register.html',context)

def login(request):
    # don't allow user to go back login page when already login
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password = password)
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

def store(request, brandCategory, sizeCategory, priceCategory):
    if sizeCategory == "All" or sizeCategory == '[]':       
        sizeCategory = []
    if priceCategory == "All":
        priceCategory = ['0','10000']
    products = models.Product.objects.all()

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

    # page paginator
    product_paginator = Paginator(list,1)
    page_num = request.GET.get('page')
    
    pages = product_paginator.get_page(page_num)
    # end page paginator

    listMin = ['0','50','70','100','200','500','1000']
    listMax = ['50','70','100','200','500','1000','10000']

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
    total = 0
    for order in orders:
        total = total + order.total

    return render(request,'store/order_complete.html', {
        'phone': phone,
        'address': address,
        'customer': customer,
        'orders': orders,
        'total': total,
        'info': info
    })

