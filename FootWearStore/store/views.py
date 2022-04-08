from email import message
from django.shortcuts import redirect, render
from . import models
from .models import Customer
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    products = models.Product.objects.all()
    return render(request, 'store/index.html', {
        'products' : products,
    })

def product_detail(request, slug):
    products = models.Product.objects.filter(slug=slug)
    pro_colors = []
    list_size = []
    for pro in products:
        if pro.color not in pro_colors:
            pro_colors.append(pro)
        if pro.size not in list_size:
            list_size.append(pro.size)

    return render(request, 'store/product-detail.html', {
        'products' : products,
        'pro_colors': pro_colors,
        'sizes': list_size,
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
    return render(request,'store/signin.html')

def logout(request):
    auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def cart(request):
    return render(request,'store/cart.html')

def store(request):
    return render(request,'store/store.html')

@login_required(login_url='login')
def place_order(request):
    return render(request,'store/place-order.html')

@login_required(login_url='login')
def order_complete(request):
    return render(request,'store/order_complete.html')
