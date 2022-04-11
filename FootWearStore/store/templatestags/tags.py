from django import template
from store import models

register = template.Library()

@register.simple_tag
def countCart(request):
    products = []
    if request.user.is_authenticated:
        user = request.user
        products = models.Cart.objects.filter(user=user)
    return len(products)
