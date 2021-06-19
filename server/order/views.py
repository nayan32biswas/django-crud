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

from . import models


class OrderListView(ListView):
    model = models.Order
    paginate_by = 30

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class OrderDetailView(DetailView):
    model = models.Order
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


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
    img.thumbnail((200, 200))
    PIL_TYPE = "PNG"
    qr_image_content = BytesIO()
    img.save(qr_image_content, format=PIL_TYPE, quality=100)
    qr_image_content.seek(0)

    media_dir = "media/qrcodes"
    source_dir = f"staticfiles/{media_dir}"

    if not os.path.exists(source_dir):
        os.makedirs(source_dir)

    file_name = f"{order_id}.{PIL_TYPE}"
    image_path = f"{source_dir}/{file_name}"
    url = f"{HOST}/{media_dir}/{file_name}"

    with open(image_path, "wb") as f:
        f.write(qr_image_content.getbuffer())
    return url


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        order = get_object_or_404(models.Order, id=kwargs["pk"])

        source_dir = "staticfiles/media/pdf"
        if not os.path.exists(source_dir):
            os.makedirs(source_dir)
        filename = f"{order.id}.pdf"

        source_path = f"{source_dir}/{filename}"

        if not os.path.isfile(source_path):
            url = reverse("order:order-detail", kwargs=kwargs)
            context = {
                "qrcode_path": generate_qrcode(request, url, order.id),
            }
            print(context)
            html_string = render_to_string("order/invoice.html", context).encode()
            html = HTML(string=html_string)
            html.write_pdf(target=f"{source_dir}/{filename}")

        fs = FileSystemStorage(f"{source_dir}")
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type="application/pdf")
            content = f"inline; filename={filename}"
            if request.GET.get("download"):
                content = f"attachment; filename={filename}"
            response["Content-Disposition"] = content
            return response
