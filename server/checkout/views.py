from django.views.generic.detail import DetailView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from faker import Faker
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.db import transaction

from product.models import Stock
from order.models import Order, OrderLine
from . import models


fake = Faker()


class CheckoutDetailView(DetailView):  # FormMixin,
    model = models.Checkout
    # form_class = forms.CheckoutProceedForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lines"] = models.CheckoutLine.objects.filter(checkout=self.object)
        return context

    def get_success_url(self):
        return reverse("order:order-list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.create_order_from_checkout(self.object)
        except Exception as e:
            return HttpResponseBadRequest(f"<h1>{ e }</h1>")
        return HttpResponseRedirect(reverse("order:order-list"))

    @transaction.atomic
    def create_order_from_checkout(self, checkout):
        order = Order.objects.create(
            user=self.request.user, tracking_code=fake.ean(length=13)
        )
        quantity = 0
        order_lines = []
        for checkout_line in checkout.lines.all().prefetch_related("product"):
            order_lines.append(
                OrderLine(
                    **{
                        "order": order,
                        "product": checkout_line.product,
                        "product_data": checkout_line.product.to_json(),
                        "quantity": checkout_line.quantity,
                        "unit_price_net_amount": (
                            checkout_line.quantity * checkout_line.product.price
                        ),
                    }
                )
            )
            quantity += checkout_line.quantity
            stock = get_object_or_404(Stock, product=checkout_line.product)
            stock.quantity -= checkout_line.quantity
            stock.save()
        OrderLine.objects.bulk_create(order_lines)
        # raise Exception("demo exception.")
        order.quantity = quantity
        order.save()
        checkout.lines.all().delete()
        checkout.delete()
