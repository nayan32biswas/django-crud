from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now


class OrderStatus(models.TextChoices):
    UNFULFILLED = ("UNFULFILLED", "Un Fulfilled")
    PARTIALLY_FULFILLED = ("PARTIALLY_FULFILLED", "Partially Fulfilled")
    FULFILLED = ("FULFILLED", "Fulfilled")
    CANCELED = ("CANCELED", "Canceled")


class Order(models.Model):
    created = models.DateTimeField(default=now, editable=False)
    status = models.CharField(
        max_length=32, default=OrderStatus.UNFULFILLED, choices=OrderStatus.CHOICES
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="orders",
        on_delete=models.SET_NULL,
    )
    quantity = models.PositiveIntegerField(default=0)
    billing_address = models.ForeignKey(
        "accounts.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    shipping_address = models.ForeignKey(
        "accounts.Address",
        related_name="+",
        editable=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    tracking_code = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ("-pk",)


class OrderLine(models.Model):
    order = models.ForeignKey(
        Order, related_name="lines", editable=False, on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "product.Product",
        related_name="order_lines",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    product_data = models.JSONField(default=dict)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    unit_price_net_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
    )

    class Meta:
        ordering = ("pk",)
