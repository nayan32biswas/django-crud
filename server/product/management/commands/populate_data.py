import os
import random
from django.core.files import File
from django.core.management.base import BaseCommand
from ...models import Category, Product, ProductImage, Warehouse, Stock
from accounts.models import Address
from django_crud.utils import generate_unique_slug

from faker import Faker

fake = Faker()


def get_image():
    images = ["landscape__47.jpg", "portrait__23.jpg", "square__42.jpg"]
    image_name = random.choice(images)
    image_dir = "product/management/commands/images"
    img_path = os.path.join(image_dir, image_name)
    return File(open(img_path, "rb"), name=image_name)


class Command(BaseCommand):
    help = "Create 100 demo product"

    @staticmethod
    def create_category(total):
        if Category.objects.count() >= 50:
            return
        for _ in range(total):
            parent = None
            if random.choice([True, False]):
                parent = Category.objects.all().order_by("?").filter().first()
            name = fake.name()
            Category.objects.create(
                **{
                    "name": name,
                    "slug": generate_unique_slug(Category, name, slug_field="slug"),
                    "description": fake.paragraph(nb_sentences=10),
                    "parent": parent,
                    "background_image": get_image(),
                    "background_image_alt": fake.name(),
                }
            )

    @staticmethod
    def create_warehouse():
        if Warehouse.objects.count() >= 5:
            return
        for _ in range(5):
            address = Address.objects.create(
                **{
                    "full_name": fake.name(),
                    "company_name": fake.company(),
                    "street_address_1": fake.street_name(),
                    "street_address_2": fake.street_name(),
                    "city": fake.city(),
                    "country": fake.country(),
                    "postal_code": fake.postcode(),
                    "phone": fake.phone_number(),
                }
            )
            name = fake.name()
            _ = Warehouse.objects.create(
                **{
                    "name": name,
                    "slug": generate_unique_slug(Warehouse, name, slug_field="slug"),
                    "company_name": fake.company(),
                    "address": address,
                    "email": fake.free_email(),
                }
            )

    @staticmethod
    def create_product(total):
        for _ in range(total):
            name = fake.name()
            category = Category.objects.all().order_by("?").first()
            product = Product.objects.create(
                **{
                    "name": name,
                    "code": fake.ean(length=13),
                    "slug": generate_unique_slug(Product, name, slug_field="slug"),
                    "description": fake.paragraph(nb_sentences=10),
                    "default_image": get_image(),
                    "category": category,
                    "price": random.randint(10, 10000),
                    "is_published": True,
                    "charge_taxes": random.choice([True, False]),
                    # "updated_at": fake.name(),
                    # "created_at": fake.name(),
                }
            )
            _ = Stock.objects.create(
                product=product,
                warehouse=Warehouse.objects.order_by("?").first(),
                quantity=random.randint(0, 50),
            )
            for i in range(random.randint(3, 5)):
                ProductImage.objects.create(
                    order=i + 1, product=product, image=get_image(), alt=fake.name()
                )

    def handle(self, *args, **options):
        total_insert = 100
        self.create_warehouse()
        self.create_category(max(5, total_insert // 10))
        self.create_product(total_insert)
