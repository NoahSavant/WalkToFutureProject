from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=200, null=False)
    price = models.FloatField(null=False)
    description = models.TextField()
    brand = models.CharField(max_length=150)
    image = models.ImageField(upload_to='images')
    status = models.CharField(max_length=50)
    slug = models.SlugField()

    def __str__(self):
        return self.name


class Size_Quantity(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.IntegerField()
    quantity = models.IntegerField()

    def __str__(self):
        return self.product.name +" - "+ str(self.size)

    def decre(self, num):
        if num > self.quantity:
            return
        self.quantity = self.quantity - num

    def incre(self, num):
        self.quantity = self.quantity + num


GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
)
COUNTRY_CHOICES = (
    ('vietNam','Việt Nam'),
    ('unitedStates', 'United States'),
    ('russia','russia'),
)
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default = 'female')
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, default='vietNam')

    def __str__(self):
        return self.user.username
        
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Customer.objects.create(user=instance)

class Cart(models.Model):
    sq = models.ForeignKey(Size_Quantity, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    def __str__(self):
        return self.sq.product.name +" - "+ self.user.username

    @property
    def total(self):
        return self.sq.product.price * self.quantity

    def plus(self):
        if self.sq.quantity - self.quantity == 0:
            return
        self.quantity = self.quantity + 1

    def minus(self):
        if self.quantity == 0:
            return
        self.quantity = self.quantity - 1

class Feedback(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.CharField(max_length=30)
    comment = models.TextField(max_length=300)

    def __str__(self):
        return str(self.product) + " - " + str(self.user)