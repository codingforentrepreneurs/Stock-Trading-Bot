from django.apps import apps 


def batch_insert_stock_data(
        dataset, 
        company_obj=None, 
        batch_size=1000,
        verbose=False):
    StockQuote = apps.get_model('market', 'StockQuote')
    batch_size = 1000
    if company_obj is None:
        raise Exception(f"Batch failed. Company Object {company_obj} invalid")
    for i in range(0, len(dataset), batch_size):
        if verbose:
            print("Doing chunk", i)
        batch_chunk = dataset[i:i+batch_size]
        chunked_quotes = []
        for data in batch_chunk:
            chunked_quotes.append(
                StockQuote(company=company_obj, **data)
            )
        StockQuote.objects.bulk_create(chunked_quotes, ignore_conflicts=True)
        if verbose:
            print("finished chunk", i)
    return len(dataset)
    