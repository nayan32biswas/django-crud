from django import forms

from . import models


class PostListForm(forms.ModelForm):
    class Meta:
        model = models.Product
        exclude = [
            "is_published",
            "charge_taxes",
            "updated_at",
            "created_at",
        ]


class OrderForm(forms.Form):
    quantity = forms.IntegerField()

    