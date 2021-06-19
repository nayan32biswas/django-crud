import os
from io import BytesIO

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

import qrcode
import qrcode.image.svg
from weasyprint import HTML
from num2words import num2words

from . import models


class OrderListView(ListView):
    model = models.Order
    paginate_by = 30

    def get_queryset(self):
        # find order for authenticated user.
        return self.model.objects.filter(user=self.request.user)


class OrderDetailView(DetailView):
    model = models.Order
    paginate_by = 20

    def get_queryset(self):
        # find order for authenticated user.
        return self.model.objects.filter(user=self.request.user)


def generate_qrcode(request, url, order_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    HOST = settings.BROWSER_HOST
    qr.add_data(f"{HOST}{url}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000", back_color="#FFFFFF")
    img = img.get_image()
    img.thumbnail((400, 400))
    PIL_TYPE = "PNG"
    qr_image_content = BytesIO()
    img.save(qr_image_content, format=PIL_TYPE, quality=100)
    qr_image_content.seek(0)

    media_dir = "media/qrcodes"
    source_dir = f"staticfiles/{media_dir}"

    # Create dir if to exists.
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)

    file_name = f"{order_id}.{PIL_TYPE}"
    image_path = f"{source_dir}/{file_name}"
    url = f"{HOST}/{media_dir}/{file_name}"

    # Write qrcode image to file.
    with open(image_path, "wb") as f:
        f.write(qr_image_content.getbuffer())
    return url


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(models.Order, id=kwargs["pk"])

        source_dir = "staticfiles/media/pdf"
        # Create dir if not exists.
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
        filename = f"{order.id}.pdf"

        source_path = f"{source_dir}/{filename}"
        if not os.path.isfile(source_path):
            lines = []
            order_total_price = 0
            # store all order line info for this order.
            for idx, line in enumerate(order.lines.all().prefetch_related("product")):
                lines.append(
                    {
                        "sl_no": idx,
                        "name": line.product.name,
                        "price": int(line.product.price),
                        "quantity": line.quantity,
                        "total_price": int(line.unit_price_net_amount),
                    }
                )
                order_total_price += int(line.unit_price_net_amount)
            url = reverse("order:order-detail", kwargs=kwargs)
            context = {
                # serve qrcode image from file
                "qrcode_path": generate_qrcode(request, url, order.id),
                "lines": lines,
                "order_total_price": order_total_price,
                "total_in_word": num2words(order_total_price).capitalize(),
            }
            # render html file with qrcode image
            html_string = render_to_string("order/invoice.html", context).encode()
            html = HTML(string=html_string)
            # generate pdf file and same it to the directory.
            html.write_pdf(target=f"{source_dir}/{filename}")

        fs = FileSystemStorage(f"{source_dir}")
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type="application/pdf")
            content = f"inline; filename={filename}"
            if request.GET.get("download"):
                content = f"attachment; filename={filename}"
            response["Content-Disposition"] = content
            return response
