from django.core.management.base import BaseCommand
from ...models import Product


class Command(BaseCommand):
    help = "Create 100 demo product"

    @staticmethod
    def create_product(ws):
        data = {}
        Product.objects.create(**data)

    def handle(self, *args, **options):
        total = options["total"]
        self.create_product(total)
