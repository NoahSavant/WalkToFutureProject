from django.shortcuts import redirect, render
from . import models
from django.contrib.auth.forms import UserCreationForm
from .forms import LoignForm
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
    form = LoignForm()
    if request.method == "POST":
        form = LoignForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context = {'form':form}
    return render(request,'store/register.html',context)

def cart(request):
    return render(request,'store/cart.html')
def store(request):
    return render(request,'store/store.html')
def login(request):
    return render(request,'store/signin.html')

def place_order(request):
    return render(request,'store/place-order.html')
def order_complete(request):
    return render(request,'store/order_complete.html')
