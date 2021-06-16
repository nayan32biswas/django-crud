from django.contrib import admin

from . import models

admin.site.register(models.Checkout)
admin.site.register(models.CheckoutLine)
