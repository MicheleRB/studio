from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.functions import ExtractYear
from django.db.models import Sum


class Percentuali(models.Model):
    descrizione = models.CharField("descrizione", max_length=100, null=True, blank=True)
    valore = models.FloatField("valore in forma decimale 20% (0.20) ", null=True, blank=True)

    def __str__(self):
        return self.descrizione

    class Meta:
        verbose_name = "Elenco Percentuale"
        verbose_name_plural = "Elenco Percentuali"

class StudioSettoreFattura1(models.Model):
    descrizione = models.CharField("descrizione",  max_length=250, null=True, blank=True)
    sigla = models.CharField("sigla", max_length=3, null=True, blank=True)

    def __str__(self):
        return "(%s)  %s" % (self.sigla, self.descrizione)

    class Meta:
        verbose_name = "Studio Settore tipologia atto"
        verbose_name_plural = "Studi Settore tipologia atto"

class StudioSettoreFattura2(models.Model):
    descrizione = models.CharField("descrizione",  max_length=250, null=True, blank=True)
    sigla = models.CharField("sigla", max_length=3, null=True, blank=True)

    def __str__(self):
        return "(%s)  %s" % (self.sigla, self.descrizione)

    class Meta:
        verbose_name = "Studio Settore aree spec"
        verbose_name_plural = "Studi Settore aree spec"

class StudioSettoreCliente(models.Model):
    descrizione = models.CharField("descrizione",  max_length=250, null=True, blank=True)
    sigla = models.CharField("sigla", max_length=3, null=True, blank=True)

    def __str__(self):
        return "(%s)  %s" % (self.sigla, self.descrizione)

    class Meta:
        verbose_name = "Studio Settore Cliente"
        verbose_name_plural = "Studi Settore Cliente"

class Clienti(models.Model):
    ragione_sociale = models.CharField("Ragione sociale", max_length=512)
    indirizzo = models.CharField("indirizzo", max_length=512)
    citta = models.CharField("citta", max_length=50)
    cap = models.CharField("cap", max_length=5)
    provincia = models.CharField("provincia", max_length=50)
    email = models.CharField("email", max_length=100, null=True, blank=True)
    telefono = models.CharField("telefono", max_length=20, null=True, blank=True)
    partita_iva = models.CharField("partita iva", max_length=14, null=True, blank=True)
    codice_fiscale = models.CharField("codice fiscale", max_length=16, null=True, blank=True)
    note = models.CharField("note", max_length=512, null=True, blank=True)
    studi_settore = models.ForeignKey(StudioSettoreCliente, related_name="+", verbose_name="studi settore", null=True, blank=True, on_delete=models.DO_NOTHING)
    persona_giuridica = models.BooleanField("persona giuridica", default=True)
    status = models.BooleanField("cliente attivo", default=True)

    def clean(self):
        if self.persona_giuridica and not self.partita_iva:
            raise ValidationError({'partita_iva': _('Manca Partita Iva per persona giuriduca')})
        if not self.persona_giuridica and not self.codice_fiscale:
            raise ValidationError({'codice_fiscale': _('Manca codice_fiscale')})

    @property
    def short_description(self):
        if self.persona_giuridica:
            desc = '%s (%s)' % (self.ragione_sociale, self.partita_iva)
        else:
            desc = '%s (%s)' % (self.ragione_sociale, self.codice_fiscale)
        return desc

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "ragione_sociale__icontains", "partita_iva__iexact", "codice_fiscale__iexact")

    @property
    def total_by_year(self):
        return self.fattura.values('anno_fattura').annotate(total=Sum('totale')).order_by('-anno_fattura')

    def __str__(self):
        return self.short_description


    def related_label(self):
        return self.short_description

    class Meta:
        ordering = ['ragione_sociale']
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"

class Fatture(models.Model):
    numero_fattura = models.PositiveIntegerField("numero fattura", unique_for_year='data_fattura', null=True, blank=True)
    descrizione = models.TextField("descrizione", null=True, blank=True)
    data_fattura = models.DateField("data fattura")
    imponibile = models.FloatField("imponibile", null=True, blank=True, default=0)
    perc_iva = models.ForeignKey(Percentuali, related_name="+", verbose_name="percentuale iva", default=4, on_delete=models.PROTECT)
    anticipazioni = models.FloatField("anticip.", null=True, blank=True, default=0)
    cpa = models.FloatField("tot c.p.a.", null=True, blank=True, default=0)
    perc_cpa = models.ForeignKey(Percentuali, related_name="+", verbose_name="percentuale cpa",  default=2, on_delete=models.PROTECT)
    iva = models.FloatField("tot iva", null=True, blank=True, default=0)
    subtotale = models.FloatField("subtotale", null=True, blank=True, default=0)
    ritenuta = models.FloatField("tot r.a.", null=True, default=0)
    perc_ritenuta = models.ForeignKey(Percentuali, related_name="+", verbose_name="percentuale ritenuta", default=3, on_delete=models.PROTECT)
    totale = models.FloatField("totale", null=True, blank=True, default=0)
    cliente_id = models.ForeignKey(Clienti, verbose_name='cliente', related_name="fattura", on_delete=models.PROTECT)
    id_fattura = models.CharField('fattura nu.', max_length=10, null=True, blank=True)
    anno_fattura = models.PositiveIntegerField('anno fattura', null=True, blank=True)
    studi_settore_1 = models.ForeignKey(StudioSettoreFattura1, related_name="+", verbose_name="studi settore tipologia atto", null=True,
                                      blank=True, on_delete=models.DO_NOTHING)
    studi_settore_2 = models.ForeignKey(StudioSettoreFattura2, related_name="+", verbose_name="studi settore aree specialistiche", null=True,
                                      blank=True, on_delete=models.DO_NOTHING)
    note = models.CharField("note", max_length=512, null=True, blank=True)




    def clean(self):
        if self.data_fattura and not self.id_fattura:
            last_fattura = Fatture.objects.filter(data_fattura__year=self.data_fattura.year).order_by('numero_fattura').last()
            if last_fattura:
                if self.data_fattura < last_fattura.data_fattura:
                    raise ValidationError({'data_fattura': _('La data deve essere maggior euguale a %s' % last_fattura.data_fattura.isoformat())})
        if not self.numero_fattura and self.data_fattura:
            last_id = Fatture.objects.filter(data_fattura__year=self.data_fattura.year).order_by('numero_fattura').last()
            if last_id:
                next_id = 1 + last_id.numero_fattura
            else:
                next_id = 1
            self.numero_fattura = next_id
        if self.numero_fattura and self.data_fattura:
            self.id_fattura = str(self.numero_fattura) + '-' + str(self.data_fattura.year)
            self.anno_fattura = self.data_fattura.year


    def __str__(self):
        return "%s (%s)" % (self.id_fattura, self.cliente_id)
    class Meta:
        ordering = ['-data_fattura', '-numero_fattura']
        verbose_name = "Fattura"
        verbose_name_plural = "Fatture"
