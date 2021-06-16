from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin

from django.urls import reverse
from django.http import HttpResponseForbidden


from . import models
from . import forms


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
            return HttpResponseForbidden()
        self.object = self.get_object()
        self.stock = get_object_or_404(models.Stock, product=self.object)
        form = self.get_form()
        if form.is_valid():
            print(form.cleaned_data)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if self.stock.quantity < form.cleaned_data["quantity"]:
            form.add_error("quantity", "insufficient stock!")
            return super().form_invalid(form)
        return super().form_valid(form)
