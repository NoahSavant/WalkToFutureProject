from django import template
from store import models
from store.models import Cart

register = template.Library()

@register.simple_tag
def countCart(request):
    total = 0
    if request.user.is_authenticated:
        user = request.user
        orders = models.Cart.objects.filter(user=user)
        for order in orders:
            total = total + order.quantity
    return total
