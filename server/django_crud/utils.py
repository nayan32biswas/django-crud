import secrets
import random
import math
import re

from django.utils.html import strip_tags
from django.utils.text import slugify


def count_words(html_string):
    word_string = strip_tags(html_string)
    matching_words = re.findall(r"\w+", word_string)
    count = len(matching_words)  # joincfe.com/projects/
    return count


def get_read_time(html_string):
    count = count_words(html_string)
    read_time_min = math.ceil(count / 200.0)  # assuming 200wpm reading
    return int(read_time_min)


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
