from django.contrib import admin
from .models import Fatture
from .models import Clienti
from .models import Percentuali
from .models import StudioSettoreCliente
from .models import StudioSettoreFattura1
from .models import StudioSettoreFattura2
from .views import fattura_pdf
from django.contrib import messages
from django.utils.html import format_html
from urllib.parse import quote as urlquote
# Register your models here.
from django.urls import reverse
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.utils.translation import gettext as _
import textwrap


class PercentualiAdmin(admin.ModelAdmin):
    model = Percentuali

class StudioSettoreClienteAdmin(admin.ModelAdmin):
    model = StudioSettoreCliente

class StudioSettoreFattura1Admin(admin.ModelAdmin):
    model = StudioSettoreFattura1

class StudioSettoreFattura2Admin(admin.ModelAdmin):
    model = StudioSettoreFattura2


class FattureAdmin(admin.ModelAdmin):

    def _total_(self, obj):

        imponibile = round(obj.imponibile, 2) if obj.imponibile else 0
        obj.imponibile = imponibile
        anticipazioni = round(obj.anticipazioni, 2) if obj.anticipazioni else 0
        obj.anticipazioni = anticipazioni
        cpa = round(imponibile * obj.perc_cpa.valore, 2)
        obj.cpa = cpa
        iva = round((imponibile + cpa) * obj.perc_iva.valore, 2)
        obj.iva = iva
        subtotale = round(imponibile + anticipazioni + cpa + iva, 2)
        obj.subtotale = subtotale
        ritenuta = 0
        if obj.cliente_id.persona_giuridica:
            ritenuta = round(imponibile * obj.perc_ritenuta.valore, 2)
        obj.ritenuta = ritenuta
        totale = round(subtotale - ritenuta, 2)
        obj.totale = totale
        return obj

    def _reverse_total_(self, obj):

        totale = obj.totale if obj.totale else 0
        anticipazioni = round(obj.anticipazioni, 2) if obj.anticipazioni else 0
        subtotal = round(totale - anticipazioni, 2)
        ritenuta = 0
        if obj.cliente_id.persona_giuridica:
            ritenuta = round((subtotal * obj.perc_ritenuta.valore) / (
                    ((1 + obj.perc_iva.valore) * (1 + obj.perc_cpa.valore)) - obj.perc_ritenuta.valore), 2)
        subtotale = subtotal + ritenuta
        iva = round(subtotale / (1 + obj.perc_iva.valore) * obj.perc_iva.valore, 2)
        cpa = round((subtotale - iva) / (1 + obj.perc_cpa.valore) * obj.perc_cpa.valore, 2)
        imponibile = round(subtotale - iva - cpa, 2)
        obj.imponibile = imponibile
        obj = self._total_(obj)
        return obj

    def response_post_save_change(self, request, obj):
        """This method is called by `self.changeform_view()` when the form
        was submitted successfully and should return an HttpResponse.
        """
        if '_calculate_total' in request.POST:

            # Get new total
            obj = self._total_(obj)
            obj.save()
            # And redirect
            messages.add_message(request, messages.INFO, 'il nuovo totale è %s' % obj.totale)
            return HttpResponseRedirect(request.path)

        elif '_calculate_reverse_total' in request.POST:

            # get new total
            obj = self._reverse_total_(obj)
            obj.save()
            # And redirect
            messages.add_message(request, messages.INFO, 'calcolo fatto il nuovo totale è %s' % obj.totale)
            return HttpResponseRedirect(request.path)
        elif '_save' in request.POST:
            post_url = reverse('admin:%s_%s_changelist' %
                               (self.model._meta.app_label, self.model._meta.model_name),
                               current_app=self.admin_site.name)
            return HttpResponseRedirect(post_url)
        else:
            return HttpResponseRedirect(request.path)

    def response_post_save_add(self, request, obj):
        """This method is called by `self.changeform_view()` when the form
        was submitted successfully and should return an HttpResponse.
        """
        if '_calculate_total' in request.POST:

            # Get new total
            obj = self._total_(obj)
            obj.save()
            # And redirect
            opts = obj._meta
            obj_url = reverse(
                'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                args=(obj.pk,),
                current_app=self.admin_site.name,
            )
            messages.add_message(request, messages.INFO, 'il nuovo totale è %s' % obj.totale)
            return HttpResponseRedirect(obj_url)

        elif '_calculate_reverse_total' in request.POST:

            # get new total
            obj = self._reverse_total_(obj)
            obj.save()
            # And redirect
            opts = obj._meta
            obj_url = reverse(
                'admin:%s_%s_change' % (opts.app_label, opts.model_name),
                args=(obj.pk,),
                current_app=self.admin_site.name,
            )
            messages.add_message(request, messages.INFO, 'calcolo fatto il nuovo totale è %s' % obj.totale)
            return HttpResponseRedirect(obj_url)
        elif '_save' in request.POST:
            post_url = reverse('admin:%s_%s_changelist' %
                               (self.model._meta.app_label, self.model._meta.model_name),
                               current_app=self.admin_site.name)
            return HttpResponseRedirect(post_url)
        else:
            return HttpResponseRedirect(request.path)



    list_display = ( 'id_fattura', 'cliente_id', 'get_persona_giuridica', 'data_fattura','get_shorten_description','imponibile', 'cpa', 'anticipazioni', 'iva', 'subtotale', 'ritenuta', 'totale', )
    fieldsets = (
        ('Testat Fattura', {
            'fields': (('cliente_id', ),
                       ('studi_settore_1', 'studi_settore_2'),
                       )
        }),
        ('Fattura', {
            'fields': (('numero_fattura', 'data_fattura', 'id_fattura'),
                       ('descrizione'),
                       ('imponibile', 'anticipazioni'),
                       ('cpa', 'perc_cpa'),
                       ('iva', 'perc_iva'),
                       ('ritenuta', 'perc_ritenuta'),
                       ('subtotale', 'totale'),
                       )
        }),
    )
    readonly_fields = ('id_fattura', 'numero_fattura', 'subtotale', 'iva', 'cpa', 'ritenuta')

    raw_id_fields = ('cliente_id',)
    search_fields = ('cliente_id__ragione_sociale', 'descrizione', 'cliente_id__codice_fiscale', 'cliente_id__partita_iva')
    autocomplete_lookup_fields = {
        'fk': ['cliente_id'],
    }
    list_filter = ('data_fattura', 'cliente_id')

    change_form_template = 'invoice/fatture/change_form.html'
    add_form_template = 'invoice/fatture/change_form.html'
    model = Fatture

    def get_persona_giuridica(self, obj):
        return obj.cliente_id.persona_giuridica

    get_persona_giuridica.boolean = True
    get_persona_giuridica.admin_order_field = 'pers.giur.'  # Allows column order sorting
    get_persona_giuridica.short_description = 'Pers.Giur.'

    def get_shorten_description(self, obj):
        return textwrap.shorten(obj.descrizione, width=120, placeholder="...")

    get_shorten_description.admin_order_field = 'descrizione corta'  # Allows column order sorting
    get_shorten_description.short_description = 'Descrizione corta'


class ClientiAdmin(admin.ModelAdmin):
    list_display = ('ragione_sociale', 'short_description', 'citta', 'note', 'persona_giuridica', 'status')
    list_filter = ('status', 'persona_giuridica')
    search_fields = ('ragione_sociale', 'codice_fiscale', 'partita_iva')
    readonly_fields = ('total_by_year', 'short_description')
    fieldsets = (
        ('Cliente', {
            'fields': (('ragione_sociale', 'email'),
                       ('citta', 'cap',),
                    ('indirizzo', 'provincia',),
                    ('partita_iva', 'persona_giuridica',),
                    ('codice_fiscale', 'telefono',),
                    ('studi_settore', 'status',),
                    ('note'),
                       )
        }),
    )
    model = Clienti

admin.site.register(Fatture, FattureAdmin)
admin.site.register(Clienti, ClientiAdmin)
admin.site.register(Percentuali, PercentualiAdmin)
admin.site.register(StudioSettoreCliente, StudioSettoreClienteAdmin)
admin.site.register(StudioSettoreFattura1, StudioSettoreFattura1Admin)
admin.site.register(StudioSettoreFattura2, StudioSettoreFattura2Admin)