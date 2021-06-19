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


class CheckoutDetailView(DetailView):
    model = models.Checkout

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add checkout lines along with checkout data.
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
        """
        This function will follow atomic operation.
        Execute them all or none of them
        """
        order = Order.objects.create(
            user=self.request.user, tracking_code=fake.ean(length=13)
        )
        quantity = 0
        order_lines = []
        # Here I prefetch-related product it will reduct database query.
        for checkout_line in checkout.lines.all().prefetch_related("product"):
            order_lines.append(
                OrderLine(
                    **{
                        "order": order,
                        "product": checkout_line.product,
                        # Storing product basic info as json field. What if product was delete or price updated.
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
            if stock.quantity < checkout_line.quantity:
                """
                Finally check stock was valid or not.
                Becouse multiple user can add product to there cert.
                """
                raise Exception(
                    f"Invalid stock quantity for product: {checkout_line.product.name} :: {checkout_line.product.code}"
                )
            stock.quantity -= checkout_line.quantity
            stock.save()
        # Bulk create will improve insertion time.
        OrderLine.objects.bulk_create(order_lines)
        order.quantity = quantity
        order.save()
        # Delete checkout and checkout line, since it's saved to order and order line.
        checkout.lines.all().delete()
        checkout.delete()
