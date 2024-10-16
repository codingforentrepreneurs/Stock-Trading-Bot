from django.db import models

from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.managers import TimescaleManager
# Create your models here.
class Company(models.Model):
    # public traded company 
    # id = models.BigIntegerField()
    name = models.CharField(max_length=120)
    ticker = models.CharField(max_length=10, unique=True, db_index=True)
    active = models.BooleanField(default=True)

    @property
    def symbol(self):
        return self.ticker
 

class StockQuote(models.Model):
    # id = models.BigIntgerField()
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="stock_prices",
    )
    open_price = models.DecimalField(max_digits=10, decimal_places=4)
    close_price = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    volume = models.BigIntegerField()

    # timestamp = models.DateTimeField(auto_now=False, auto_now_add=False)
    time = TimescaleDateTimeField(interval="1 minute")

    objects = models.Manager()
    timescale = TimescaleManager()

    class Meta:
        unique_together = [('company', 'time')]