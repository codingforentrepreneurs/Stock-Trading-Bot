# Generated by Django 5.1.2 on 2024-10-15 20:58

import django.db.models.deletion
import timescale.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("market", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name="StockQuote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("open_price", models.DecimalField(decimal_places=4, max_digits=10)),
                ("close_price", models.DecimalField(decimal_places=4, max_digits=10)),
                ("high", models.DecimalField(decimal_places=4, max_digits=10)),
                ("low", models.DecimalField(decimal_places=4, max_digits=10)),
                ("volume", models.BigIntegerField()),
                (
                    "time",
                    timescale.db.models.fields.TimescaleDateTimeField(
                        interval="1 minute"
                    ),
                ),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_prices",
                        to="market.company",
                    ),
                ),
            ],
        ),
    ]
