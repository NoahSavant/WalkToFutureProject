from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name = 'index'),
    path('product/<slug:slug>/', views.product_detail, name='detail'),
    path('login/', views.login, name = 'login'),
    path('logout/',views.logout,name = 'logout'),
    path('register/', views.register, name = "register"),
    path('cart/', views.cart, name = "cart"),
    path('store/<str:brandCategory>/<str:sizeCategory>/<str:priceCategory>/<str:searchCategory>', views.store, name = "store"),
    path('place_order/', views.place_order, name = "place_order"),
    path('order_complete/', views.order_complete, name = "order_complete"),
    path('contact/', views.contact, name = "contact"),
    path('register_successfully/', views.register_successfully,name = "register_successfully"),
    path('verify/',views.verify, name ="verify"),
    path('profile/',views.profile, name ='profile' ),
    path('dashboard/',views.dashboard,name = 'dashboard'),
]