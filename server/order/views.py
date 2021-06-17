from django.shortcuts import render
from django.urls import reverse

import qrcode
import qrcode.image.svg
from io import BytesIO


from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
from django.views.generic import View


from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
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


""" PDF """


def index(request):
    context = {}
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make("demo-data", image_factory=factory, box_size=20)
    stream = BytesIO()
    img.save(stream)
    context["svg"] = stream.getvalue().decode()
    return render(request, "order/index.html", context=context)


def generate_qrcode(request, url):
    factory = qrcode.image.svg.SvgImage
    img = qrcode.make("demo-data", image_factory=factory, box_size=20)
    stream = BytesIO()
    img.save(stream)
    return stream.getvalue().decode()


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    print(html)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None


from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        # template = get_template("invoice.html")
        url = reverse("order:order-detail", kwargs=kwargs)
        context = {
            "invoice_id": 123,
            "customer_name": "John Cooper",
            "amount": 1399.99,
            "today": "Today",
            "qrcode": generate_qrcode(request, url),
        }
        # html = template.render(context)
        # pdf = render_to_pdf("order/temp.html", context)

        # if pdf:
        #     response = HttpResponse(pdf, content_type="application/pdf")
        #     filename = f"Invoice_{url}.pdf"
        #     content = f"inline; filename={filename}"
        #     # download = request.GET.get("download")
        #     # if download:
        #     #     content = f"attachment; filename={filename}"
        #     response["Content-Disposition"] = content
        #     return response
        # return HttpResponse("Not found")

        html_string = render_to_string("order/temp.html", {"paragraphs": context})
        print(html_string)
        html = HTML(string=html_string)
        html.write_pdf(target="/tmp/mypdf.pdf")

        fs = FileSystemStorage("/tmp")
        with fs.open("mypdf.pdf") as pdf:
            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = 'inline; filename="mypdf.pdf"'
            return response
