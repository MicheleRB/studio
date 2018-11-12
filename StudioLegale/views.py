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
from django.db.models import Max
import datetime

from django.shortcuts import render
from .models import Fatture


@login_required(login_url='admin/login')
def index(request):
    template = loader.get_template('studiolegale/index.html')
    context = {'title' : 'Report', 'redirect': 'Pagina iniziale', }
    return HttpResponse(template.render(context, request))

@login_required(login_url='admin/login')
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

@login_required(login_url='admin/login')
def report(request):
    data = {}
    qdata=[]
    year_ft = datetime.datetime.now().year
    fatture = Fatture.objects.filter(data_fattura__year=year_ft).order_by('-data_fattura')

    quarter = fatture.values('trimestre_fattura').annotate(Sum_iva=Sum('iva'),
                                                 Sum_totale=Sum('totale'),
                                                 LastDt=Max('data_fattura'),
                                                 ).order_by('-trimestre_fattura').distinct()
    for q in quarter:
        qdata.append(q)
    data[year_ft] = qdata

    year_ft = datetime.datetime.now().year -1
    fatture = Fatture.objects.filter(data_fattura__year=year_ft).order_by('-data_fattura')

    quarter1 = fatture.values('trimestre_fattura').annotate(Sum_iva=Sum('iva'),
                                                                   Sum_totale=Sum('totale'),
                                                                   LastDt=Max('data_fattura'),
                                                                   ).order_by('-trimestre_fattura').distinct()
    qdata = []
    for q in quarter1:
        qdata.append(q)
    data[year_ft] = qdata
    print(data)
    template = loader.get_template('studiolegale/index.html')
    context = {'title': 'Report', 'data': data, }
    return HttpResponse(template.render(context, request))



