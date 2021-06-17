from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.urls import reverse

from django_crud.utils import generate_unique_slug
from checkout.models import CheckoutLine


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
        is_staff=False,
        is_active=True,
        is_superuser=False,
    ):
        if not email:
            raise ValueError("Users must have an email")
        if not password:
            raise ValueError("Users must have a password")
        user_obj = self.model(
            email=self.normalize_email(email),
        )
        user_obj.set_password(password)  # change user password
        user_obj.is_superuser = is_superuser
        user_obj.is_staff = is_staff
        user_obj.is_active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, email, password=None):
        user = self.create_user(email, password=password, is_staff=True)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True,
        )
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=128, unique=True)
    full_name = models.CharField(max_length=250, blank=True)

    is_active = models.BooleanField(default=True)  # can login
    is_staff = models.BooleanField(default=False)  # staff user non superuser
    is_superuser = models.BooleanField(default=False)  # superuser

    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    USERNAME_FIELD = "email"  # username

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "username",
                    "email",
                ]
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = generate_unique_slug(self, self.email, "username")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.full_name:
            return self.full_name
        return self.username

    # def get_absolute_url(self):
    #     return reverse("accounts:profile", kwargs={"username": self.username})

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def total_checkout_line(self):
        return (
            CheckoutLine.objects.filter(checkout__user_id=self.id)
            .aggregate(models.Sum("quantity"))
            .get("quantity__sum")
        )

    @property
    def checkout_url(self):
        checkout = self.checkouts.first()
        if checkout:
            return reverse("checkout:checkout-detail", kwargs={"pk": checkout.id})
        return None


class Address(models.Model):
    full_name = models.CharField(max_length=255, blank=True)
    company_name = models.CharField(max_length=256, blank=True)
    street_address_1 = models.CharField(max_length=256, blank=True)
    street_address_2 = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    country = models.CharField(max_length=127)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self) -> str:
        return f"{self.full_name}, {self.phone} :: {self.postal_code}"
