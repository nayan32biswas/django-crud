from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from faker import Faker

from checkout.models import CheckoutLine, Checkout
from . import models
from . import forms

fake = Faker()


class ProductListView(ListView):

    model = models.Product
    paginate_by = 30  # if pagination is desired

    def get_queryset(self):
        object_list = self.model.objects.all()
        query = self.request.GET.get("q")
        if query:
            object_list = object_list.filter(Q(name__icontains=query) | Q(code=query))
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProductDetailView(FormMixin, DetailView):
    model = models.Product
    form_class = forms.OrderForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse("product:product-detail", kwargs={"slug": self.object.slug})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_URL)
        self.object = self.get_object()
        self.stock = get_object_or_404(models.Stock, product=self.object)
        form = self.get_form()
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            checkout = request.user.checkouts.first()
            if checkout is None:
                checkout = Checkout.objects.create(
                    user=request.user, tracking_code=fake.ean(length=13)
                )
            checkout_line = checkout.lines.filter(product=self.object).first()
            if checkout_line is not None:
                checkout_line.quantity += quantity
                if self.stock.quantity < checkout_line.quantity:
                    form.add_error("quantity", "insufficient stock!")
                    return super().form_invalid(form)
                checkout_line.save()
            else:
                checkout_line = CheckoutLine.objects.create(
                    checkout=checkout, product=self.object, quantity=quantity
                )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if self.stock.quantity < form.cleaned_data["quantity"]:
            form.add_error("quantity", "insufficient stock!")
            return super().form_invalid(form)
        return super().form_valid(form)
