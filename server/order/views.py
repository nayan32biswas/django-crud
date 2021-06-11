from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
import qrcode
import qrcode.image.svg
from io import BytesIO


def index(request):
    context = {}
    if request.method == "POST":
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(
            request.POST.get("qr_text", ""), image_factory=factory, box_size=20
        )
        stream = BytesIO()
        img.save(stream)
        context["svg"] = stream.getvalue().decode()

    return render(request, "index.html", context=context)


"""

"""
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
from django.http import HttpResponse
from django.views.generic import View


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None


class GeneratePDF(View):
    def get(self, request, *args, **kwargs):
        # template = get_template("invoice.html")
        context = {
            "invoice_id": 123,
            "customer_name": "John Cooper",
            "amount": 1399.99,
            "today": "Today",
        }
        # html = template.render(context)
        pdf = render_to_pdf("invoice.html", context)
        if pdf:
            response = HttpResponse(pdf, content_type="application/pdf")
            filename = "Invoice_%s.pdf" % ("12341231")
            content = "inline; filename='%s'" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % (filename)
            response["Content-Disposition"] = content
            return response
        return HttpResponse("Not found")
