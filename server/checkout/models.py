from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Checkout(models.Model):
    """A shopping checkout."""

    created = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="checkouts",
        on_delete=models.CASCADE,
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
        ordering = ("-last_change", "pk")

    def __str__(self) -> str:
        return str(self.user)


class CheckoutLine(models.Model):

    checkout = models.ForeignKey(
        Checkout, related_name="lines", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        "product.Product", related_name="+", on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f"{self.checkout} :: {self.product}"