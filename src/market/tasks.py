from datetime import timedelta

from django.apps import apps 
from django.utils import timezone

import helpers.clients as helper_clients

from .utils import batch_insert_stock_data
    

def sync_company_stock_quotes(company_id, days_ago = 32, date_format = "%Y-%m-%d", verbose=False):
    Company = apps.get_model("market", "Company")
    try:
        company_obj = Company.objects.get(id=company_id)
    except:
        company_obj = None
    if company_obj is None:
        raise Exception(f"Company Id {company_id} invalid")
    company_ticker = company_obj.ticker
    if company_ticker is None:
        raise Exception(f"{company_ticker} invalid")
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days_ago)
    to_date = end_date.strftime(date_format)
    from_date = start_date.strftime(date_format)
    client = helper_clients.PolygonAPIClient(
        ticker=company_ticker,
        from_date=from_date,
        to_date=to_date
    )
    dataset = client.get_stock_data()
    if verbose:
        print('dataset length', len(dataset))
    batch_insert_stock_data(dataset=dataset, company_obj=company_obj, verbose=verbose)
    
    


def sync_stock_data():
    Company = apps.get_model("market", "Company")
    companies = Company.objects.filter(active=True).values_list('id')
    for company_id in companies:
        sync_company_stock_quotes(company_id)