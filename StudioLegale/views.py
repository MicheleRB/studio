from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# from reportlab.platypus import Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from .models import Fatture
# from Studio import settings
# from reportlab.pdfbase.pdfmetrics import stringWidth
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import ParagraphStyle
# from reportlab.lib.enums import TA_RIGHT
from .draw_pdf import draw_footer, draw_description, draw_invoice_detail, draw_header, draw_invoice
from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum


def dashboard(request):
    total_by_year = Fatture.objects.all().values('anno_fattura').annotate(total=Sum('totale')).order_by('-anno_fattura')
    template = loader.get_template('studiolegale/base.html')
    context = {
        'total_by_year': total_by_year,
    }
    return HttpResponse(template.render(context, request))



def fattura_pdf(request, id_fattura):
    fattura = Fatture.objects.get(id_fattura=id_fattura)
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    file_name= '%s %s %s' % (fattura.cliente_id.ragione_sociale, fattura.numero_fattura, fattura.data_fattura.isoformat())
    response['Content-Disposition'] = 'filename="%s"' % file_name

    # Create the PDF object, using the response object as its "file."
    canvas = Canvas(response, pagesize=A4)
    canvas.translate(0, 29.7 * cm)
    canvas.setStrokeColorRGB(0.2, 0.2, 0.2)
    canvas.setFillColorRGB(0.2, 0.2, 0.2)
    canvas.setFont('Helvetica', 10)

    draw_header(canvas, fattura)
    draw_invoice_detail(canvas, fattura)
    draw_description(canvas, fattura)
    draw_invoice(canvas, fattura)
    draw_footer(canvas)

    #pdf.restoreState()
    # Close the PDF object cleanly, and we're done.
    canvas.showPage()
    canvas.save()
    return response
