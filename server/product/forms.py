from django import forms


class OrderForm(forms.Form):
    quantity = forms.IntegerField()
