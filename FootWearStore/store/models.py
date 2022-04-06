from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200, null=False)
    price = models.FloatField(null=False)
    description = models.TextField()
    brand = models.CharField(max_length=150)
    size = models.IntegerField()
    quantity = models.IntegerField()
    color = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images')
    slug = models.SlugField()

    def __str__(self):
        return self.name

