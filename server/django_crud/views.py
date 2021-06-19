from django.shortcuts import render

from product.models import Product


def home_view(request):
    context = {"products": Product.objects.published()[:20]}
    return render(request, "home.html", context)
