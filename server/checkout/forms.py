from django import forms


class CheckoutProceedForm(forms.Form):
    error = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
