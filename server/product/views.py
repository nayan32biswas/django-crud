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
    paginate_by = 30  # Pagination to display limited order for each page.

    def get_queryset(self):
        object_list = self.model.objects.all()
        query = self.request.GET.get("q")
        if query:
            # Search product based on product name or product code
            object_list = object_list.filter(Q(name__icontains=query) | Q(code=query))
        return object_list

    def get_context_data(self, **kwargs):
        # Write code to add extra data in the context and pass to the template.
        context = super().get_context_data(**kwargs)
        return context


class ProductDetailView(FormMixin, DetailView):
    model = models.Product
    form_class = forms.OrderForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        # After successfull post method, user will redirect to this url(product details)
        return reverse("product:product-detail", kwargs={"slug": self.object.slug})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(settings.LOGIN_URL)
        self.object = self.get_object()
        self.stock = get_object_or_404(models.Stock, product=self.object)
        form = self.get_form()
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            # User should maximum one checkout at a time. And it can be temporary.
            checkout = request.user.checkouts.first()

            if checkout is None:
                # Create checkout it does not exists any. We can also do it with get_or_create with user field.
                checkout = Checkout.objects.create(
                    user=request.user, tracking_code=fake.ean(length=13)
                )
            # If product exists in cert then get it.
            checkout_line = checkout.lines.filter(product=self.object).first()
            if checkout_line is not None:
                # add or remove quantity dependint on
                checkout_line.quantity = max(checkout_line.quantity + quantity, 0)
                # Increment quantity or delete this checkout line if quantity == zero.
                if checkout_line.quantity == 0:
                    checkout_line.delete()
                else:
                    if self.stock.quantity < checkout_line.quantity:
                        # if checkout line exists with this product then add it with
                        form.add_error("quantity", "insufficient stock!")
                        return super().form_invalid(form)
                    checkout_line.save()
            else:
                # Create new checkout line
                checkout_line = CheckoutLine.objects.create(
                    checkout=checkout, product=self.object, quantity=quantity
                )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # Initailly validate is it valid quantity or not.
        if self.stock.quantity < form.cleaned_data["quantity"]:
            form.add_error("quantity", "insufficient stock!")
            return super().form_invalid(form)
        return super().form_valid(form)
