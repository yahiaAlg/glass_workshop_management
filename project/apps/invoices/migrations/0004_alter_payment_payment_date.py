# Generated by Django 5.2.4 on 2025-07-04 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0003_alter_invoice_due_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_date',
            field=models.DateField(auto_now_add=True, verbose_name='Date de paiement'),
        ),
    ]
