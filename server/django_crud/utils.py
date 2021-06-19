import secrets
import random
from django.utils.text import slugify


def get_rand_str(N=None):
    N = random.randint(2, 3) if N is None else N
    return secrets.token_hex(N)


def generate_unique_slug(model, text, slug_field="slug"):
    proposed_slug = slugify(text, allow_unicode=True)
    exists = model.objects.filter(
        **{f"{slug_field}__startswith": proposed_slug}
    ).exists()
    if exists:
        proposed_slug = f"{proposed_slug}_{get_rand_str(4)}"
        exists = model.objects.filter(
            **{f"{slug_field}__startswith": proposed_slug}
        ).exists()
        if exists:
            return generate_unique_slug(model, text, slug_field=slug_field)
        else:
            return proposed_slug
    else:
        return proposed_slug
