from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.platypus import Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from .models import Fatture
from Studio import settings
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT


def format_currency(amount):
    return u"%s %.2f" % ('€', amount)

def format_percentage(amount):
    return u"%s %.d%%" % ('€', amount * 100)



def draw_header(canvas, invoice):
    """ Draws the invoice header """

    canvas.setLineWidth(2)
    canvas.line(2 * cm, -4 * cm, 19 * cm, -4 * cm)
    """ Draws the business address """
    business_details = settings.BUSINESS_DETAIL
    business_data = []
    for line in business_details:
        business_data.append([line])

    table = Table(business_data, colWidths=[17 * cm], rowHeights=[15, 17, 11, 11, 11, 11, 11])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('FONTSIZE', (0, 1), (0, -1), 6),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), (0.95, 0.95,0.95)),
    ])
    tw, th, = table.wrapOn(canvas, 2 * cm, 19 * cm)
    table.drawOn(canvas, 2 * cm, -4 * cm)



def draw_invoice_detail(canvas, invoice):
    invoice_detail = [[
        u'Fattura numero %s' % (invoice.id_fattura),
        '',
        u'Bergamo, li %s' % invoice.data_fattura.isoformat(),
                    ],
        []
    ]

    table = Table(invoice_detail, colWidths=[3.5 * cm, 10 * cm, 3.5 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (0, 0), 0.5, (0.7, 0.7, 0.7)),
        ('LINEBELOW', (2, 0), (2, 0), 0.5, (0.7, 0.7, 0.7)),
    ])
    tw, th, = table.wrapOn(canvas, 2 * cm, 19 * cm)
    table.drawOn(canvas, 2 * cm, -5.5 * cm)

    if invoice.cliente_id.persona_giuridica:
        vat = 'Partita iva : %s' % invoice.cliente_id.partita_iva
    else:
        vat = 'Codice fiscale : %s' % invoice.cliente_id.codice_fiscale
    customer_detail_list = (
        u'Spett.le',
        invoice.cliente_id.ragione_sociale,
        invoice.cliente_id.indirizzo,
        invoice.cliente_id.cap + ' ' + invoice.cliente_id.citta + ' ' + invoice.cliente_id.provincia,
        vat)
    customer_detail=[]
    for i in customer_detail_list:
        customer_detail.append([i])
    table = Table(customer_detail, colWidths=[6 * cm], rowHeights=[12, 12, 12, 12, 12])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ])
    tw, th, = table.wrapOn(canvas, 2 * cm, 19 * cm)
    table.drawOn(canvas, 13.7 * cm, -8 * cm)

def draw_description(canvas, invoice):
    body_desc = [['Descrizione attività']]
    description = invoice.descrizione.splitlines()
    for i in description:
        if len(i) > 137:
            if i.index(' ', 110, 137):
                ind = i.index(' ', 110, 137)
                desc = i[:ind]+'\n'+i[ind:]
        else:
           desc = i
        body_desc.append([desc])
    table = Table(body_desc, colWidths=[17 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Oblique'),
        ('GRID', (0, 0), (-1, -1), 1, (0.7, 0.7, 0.7)),
        ('BACKGROUND', (0, 0), (0, 0), (0.9, 0.9, 0.9)),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
   #     ('LINEBELOW', (-1, -1), (-1, -1), 0.5, (0.1, 0.1, 0.1 )),
    ])
    tw, th, = table.wrapOn(canvas, 2 * cm, 19.7 * cm)
    table.drawOn(canvas, 2 * cm, -12 * cm)


def draw_invoice(canvas, invoice):

    data =[]
    invoice_detail =(
        [u'Imponibile:', format_currency(invoice.imponibile)],
        [u'Anticipazioni escluse iva \nex art.15 d.p.r. 633/72:',
                            format_currency(invoice.anticipazioni)],
        [u'C.p.a. al %s:' % format_percentage(invoice.perc_cpa.valore),
                            format_currency(invoice.cpa)],
        [u'Iva al %s:' % format_percentage(invoice.perc_iva.valore),
                            format_currency(invoice.iva)],
        [u'Totale:', format_currency(invoice.subtotale)] if invoice.cliente_id.persona_giuridica else [],
        [u'Ritenuta acconto al %s:' % format_percentage(invoice.perc_ritenuta.valore),
         format_currency(invoice.ritenuta)] if invoice.cliente_id.persona_giuridica else [],
        [],
        [u'Totale fattura:', format_currency(invoice.totale)],
    )
    for i in invoice_detail:
        data.append(i)
    table = Table(data, colWidths=[4.5 * cm, 4 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
        ('LINEBELOW', (0, 0), (-1, -3), 1, (0.7, 0.7, 0.7)) if invoice.cliente_id.persona_giuridica else (
        'LINEBELOW', (0, 0), (-1, -5), 1, (0.7, 0.7, 0.7)),
       # row description
       # ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        # row value
        #('ALIGN', (1, 0), (1, -1), 'RIGHT'),
       # ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('BACKGROUND', (-1, -3), (-1, -3), (0.9, 0.9, 0.9) if invoice.cliente_id.persona_giuridica else (1, 1, 1)),
        ('FONT', (-1, -3), (-1, -3), 'Helvetica-Bold'),
        ('GRID', (1, -1), (-1, -1), 1.5, (0.1, 0.1, 0.1)),
        ('BACKGROUND', (-1, -1), (-1, -1), (0.9, 0.9, 0.9)),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),

    ])
    tw, th, = table.wrapOn(canvas, 2 * cm, 19 * cm)
    table.drawOn(canvas, 10.5 * cm, -25 * cm)

def draw_footer(canvas):
    business_details = settings.BUSINESS_DETAIL
    business_data = []
    footer = ''
    for line in business_details:
        footer += '%s ' % line
    business_data.append([footer])

    table = Table(business_data, colWidths=[17 * cm])
    table.setStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Oblique'),
        ('FONTSIZE', (0, 0), (-1, -1), 5),
        ('TEXTCOLOR', (0, 0), (-1, -1), (0.7, 0.7, 0.7)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
       # ('BACKGROUND', (0, 0), (-1, -1), (0.9, 0.9, 0.9)),
    ])
    tw, th, = table.wrapOn(canvas, 2 * cm, 19 * cm)
    table.drawOn(canvas, 2 * cm, -29.5 * cm)