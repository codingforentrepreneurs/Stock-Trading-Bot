from django.contrib import admin

# Register your models here.
from .models import StockQuote, Company

admin.site.register(Company)

class StockQuoteAdmin(admin.ModelAdmin):
    list_display = ['company__ticker', 'close_price', 'time']
    list_filter = ['company__ticker', 'time']

    # class Meta:
    #     model = StockQuote

admin.site.register(StockQuote, StockQuoteAdmin)