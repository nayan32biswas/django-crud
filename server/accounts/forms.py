from django import forms
from django.db.models import Q
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
User = get_user_model()


class UserProfileForm(forms.Form):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
        ]


class UserLoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("email or password is not currect.")
            if not user.check_password(password):
                raise forms.ValidationError("email or password is not currect.")
            if not user.is_active:
                raise forms.ValidationError("This user is not longer active.")
        return super(UserLoginForm, self).clean(*args, **kwargs)

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(label='Email address')
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            # 'username',
            'email',
            'password',
            'confirm_password',
        ]

    def clean(self, *args, **kwargs):
        # username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        user = User.objects.filter(Q(email=email))
        if user.exists():
            raise forms.ValidationError("This email has already been registered")
        if password != confirm_password:
            raise forms.ValidationError("Password is not match")
        
        return super(UserRegisterForm, self).clean(*args, **kwargs)
