# Generated by Django 2.0.2 on 2018-05-28 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('StudioLegale', '0001_initial'), ('StudioLegale', '0002_auto_20180522_0953'), ('StudioLegale', '0003_auto_20180527_1502'), ('StudioLegale', '0004_auto_20180527_1503'), ('StudioLegale', '0005_auto_20180527_1601')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Clienti',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ragione_sociale', models.CharField(max_length=512, verbose_name='Ragione sociale')),
                ('indirizzo', models.CharField(blank=True, max_length=512, null=True, verbose_name='indirizzo')),
                ('citta', models.CharField(blank=True, max_length=50, null=True, verbose_name='citta')),
                ('cap', models.CharField(blank=True, max_length=5, null=True, verbose_name='cap')),
                ('provincia', models.CharField(blank=True, max_length=50, null=True, verbose_name='provincia')),
                ('email', models.CharField(blank=True, max_length=100, null=True, verbose_name='email')),
                ('telefono', models.CharField(blank=True, max_length=20, null=True, verbose_name='telefono')),
                ('partita_iva', models.CharField(blank=True, max_length=14, null=True, verbose_name='partita iva')),
                ('codice_fiscale', models.CharField(blank=True, max_length=16, null=True, verbose_name='codice fiscale')),
                ('note', models.CharField(blank=True, max_length=512, null=True, verbose_name='note')),
                ('persona_giuridica', models.BooleanField(default=True, verbose_name='persona giuridica')),
                ('status', models.BooleanField(default=True, verbose_name='cliente attivo')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clienti',
            },
        ),
        migrations.CreateModel(
            name='Fatture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_fattura', models.PositiveIntegerField(blank=True, null=True, unique_for_year='data_fattura', verbose_name='numero fattura')),
                ('descrizione', models.TextField(blank=True, null=True, verbose_name='descrizione')),
                ('data_fattura', models.DateField(verbose_name='data fattura')),
                ('imponibile', models.FloatField(blank=True, default=0, null=True, verbose_name='imponibile')),
                ('anticipazioni', models.FloatField(blank=True, default=0, null=True, verbose_name='anticipazioni')),
                ('cpa', models.FloatField(blank=True, default=0, null=True, verbose_name='totale c.p.a.')),
                ('iva', models.FloatField(blank=True, default=0, null=True, verbose_name='totale iva')),
                ('subtotale', models.FloatField(blank=True, default=0, null=True, verbose_name='subtotale')),
                ('ritenuta', models.FloatField(default=0, null=True, verbose_name='totale ritenuta acconto')),
                ('totale', models.FloatField(blank=True, default=0, null=True, verbose_name='totale')),
                ('id_fattura', models.CharField(blank=True, max_length=10, null=True, verbose_name='identificativo fattura')),
                ('cliente_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='fattura', to='StudioLegale.Clienti', verbose_name='cliente')),
            ],
            options={
                'verbose_name': 'Fattura',
                'verbose_name_plural': 'Fatture',
            },
        ),
        migrations.CreateModel(
            name='Percentuali',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descrizione', models.CharField(blank=True, max_length=100, null=True, verbose_name='descrizione')),
                ('valore', models.FloatField(blank=True, null=True, verbose_name='valore in forma decimale 20% (0.20) ')),
            ],
            options={
                'verbose_name': 'Elenco Percentuale',
                'verbose_name_plural': 'Elenco Percentuali',
            },
        ),
        migrations.CreateModel(
            name='StudioSettoreCliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descrizione', models.CharField(blank=True, max_length=250, null=True, verbose_name='descrizione')),
                ('sigla', models.CharField(blank=True, max_length=3, null=True, verbose_name='sigla')),
            ],
            options={
                'verbose_name': 'Studio Settore Cliente',
                'verbose_name_plural': 'Studi Settore Cliente',
            },
        ),
        migrations.AddField(
            model_name='fatture',
            name='perc_cpa',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='StudioLegale.Percentuali', verbose_name='percentuale cpa'),
        ),
        migrations.AddField(
            model_name='fatture',
            name='perc_iva',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='StudioLegale.Percentuali', verbose_name='percentuale iva'),
        ),
        migrations.AddField(
            model_name='fatture',
            name='perc_ritenuta',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='StudioLegale.Percentuali', verbose_name='percentuale ritenuta'),
        ),
        migrations.AddField(
            model_name='clienti',
            name='studi_settore',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='StudioLegale.StudioSettoreCliente', verbose_name='studi settore'),
        ),
        migrations.AlterModelOptions(
            name='clienti',
            options={'ordering': ['ragione_sociale'], 'verbose_name': 'Cliente', 'verbose_name_plural': 'Clienti'},
        ),
        migrations.AlterModelOptions(
            name='fatture',
            options={'ordering': ['-data_fattura', '-numero_fattura'], 'verbose_name': 'Fattura', 'verbose_name_plural': 'Fatture'},
        ),
        migrations.AddField(
            model_name='fatture',
            name='anno_fattura',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='anno fattura'),
        ),
        migrations.AlterField(
            model_name='clienti',
            name='cap',
            field=models.CharField(max_length=5, verbose_name='cap'),
        ),
        migrations.AlterField(
            model_name='clienti',
            name='citta',
            field=models.CharField(max_length=50, verbose_name='citta'),
        ),
        migrations.AlterField(
            model_name='clienti',
            name='indirizzo',
            field=models.CharField(max_length=512, verbose_name='indirizzo'),
        ),
        migrations.AlterField(
            model_name='clienti',
            name='provincia',
            field=models.CharField(max_length=50, verbose_name='provincia'),
        ),
        migrations.CreateModel(
            name='StudioSettoreFattura1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descrizione', models.CharField(blank=True, max_length=250, null=True, verbose_name='descrizione')),
                ('sigla', models.CharField(blank=True, max_length=3, null=True, verbose_name='sigla')),
            ],
            options={
                'verbose_name': 'Studio Settore Fattura 2',
                'verbose_name_plural': 'Studi Settore Fattura 2',
            },
        ),
        migrations.CreateModel(
            name='StudioSettoreFattura2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descrizione', models.CharField(blank=True, max_length=250, null=True, verbose_name='descrizione')),
                ('sigla', models.CharField(blank=True, max_length=3, null=True, verbose_name='sigla')),
            ],
            options={
                'verbose_name': 'Studio Settore Fattura 1',
                'verbose_name_plural': 'Studi Settore Fattura 1',
            },
        ),
        migrations.AddField(
            model_name='fatture',
            name='studi_settore_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='StudioLegale.StudioSettoreFattura1', verbose_name='studi settore tipologia atto'),
        ),
        migrations.AddField(
            model_name='fatture',
            name='studi_settore_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='StudioLegale.StudioSettoreFattura2', verbose_name='studi settore aree specialistiche'),
        ),
        migrations.AddField(
            model_name='fatture',
            name='note',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='note'),
        ),
    ]
