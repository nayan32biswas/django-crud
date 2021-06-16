from django.db import models
from django.conf import settings

from mptt.managers import TreeManager
from mptt.models import MPTTModel


class Category(MPTTModel):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    background_image = models.ImageField(
        upload_to="category-backgrounds", blank=True, null=True
    )
    background_image_alt = models.CharField(max_length=128, blank=True)

    objects = models.Manager()
    tree = TreeManager()

    def __str__(self) -> str:
        return f"{self.name}"


class ProductsQueryset(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Product(models.Model):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=24, unique=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    description = models.TextField(blank=True)
    default_image = models.ImageField(upload_to="products", blank=True)
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
    )
    is_published = models.BooleanField(default=False)
    charge_taxes = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    objects = ProductsQueryset.as_manager()

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    order = models.IntegerField(editable=False, db_index=True, null=True)
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products")
    alt = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ("order", "pk")

    def __str__(self) -> str:
        return f"{self.order} :: {self.product}"


class Warehouse(models.Model):
    # Ware house ignored
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True)
    company_name = models.CharField(blank=True, max_length=255)
    address = models.ForeignKey(
        "accounts.Address",
        on_delete=models.PROTECT,
    )
    email = models.EmailField(blank=True, default="")

    class Meta:
        ordering = ("-slug",)

    def __str__(self):
        return self.name


class Stock(models.Model):
    warehouse = models.ForeignKey(Warehouse, null=False, on_delete=models.CASCADE)
    product = models.ForeignKey(
        "product.Product", on_delete=models.CASCADE, related_name="stocks"
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [["warehouse", "product"]]

    def __str__(self) -> str:
        return f"{self.warehouse} :: {self.product} :: {self.quantity}"
