from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name = 'index'),
    path('product/<slug:slug>/', views.product_detail, name='detail'),
    path('login/', views.login, name = 'login'),
    path('register/', views.register, name = "register"),
    path('cart/', views.cart, name = "cart"),
    path('store/', views.store, name = "store")
]