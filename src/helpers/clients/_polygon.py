import pytz
import requests

from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlencode
from datetime import datetime
from decouple import config

POLOGYON_API_KEY = config("POLOGYON_API_KEY", default=None, cast=str)

def transform_polygon_result(result):
    unix_timestamp = result.get('t') / 1000.0
    utc_timestamp = datetime.fromtimestamp(unix_timestamp, tz=pytz.timezone('UTC'))
    return {
        'open_price': result['o'],
        'close_price': result['c'],
        'high_price': result['h'],
        'low_price': result['l'],
        'number_of_trades': result['n'],
        'volume': result['v'],
        'volume_weighted_average': result['vw'],
        'time': utc_timestamp,
    }


@dataclass
class PolygonAPIClient:
    ticker: str = "AAPL"
    multiplier: int = 5
    timespan:str = "minute"
    from_date:str = "2024-01-09"
    to_date:str = "2024-01-09"
    api_key:str = ""
    adjusted: bool = True 
    sort: Literal["asc", "desc"] = "asc"

    def get_api_key(self):
        return self.api_key or POLOGYON_API_KEY

    def get_headers(self):
        api_key = self.get_api_key()
        return {
            "Authorization": f"Bearer {api_key}"
        }

    def get_params(self):
        return {
            "adjusted": self.adjusted,
            "sort": self.sort
        }
    
    def generate_url(self, pass_auth=False):
        ticker = f"{self.ticker}".upper()
        path = f"/v2/aggs/ticker/{ticker}/range/{self.multiplier}/{self.timespan}/{self.from_date}/{self.to_date}"
        url = f"https://api.polygon.io{path}"
        params = self.get_params()
        encoded_params = urlencode(params)
        url = f"{url}?{encoded_params}"
        if pass_auth:
            api_key = self.get_api_key()
            url += f"&api_key={api_key}"
        return url

    def fetch_data(self):
        headers = self.get_headers()
        url = self.generate_url()
        response = requests.get(url, headers=headers)
        response.raise_for_status() # not 200/201
        return response.json()

    def get_stock_data(self):
        data = self.fetch_data()
        results = data.get('results') or None
        if results is None:
            raise Exception(f"Ticker {self.ticker} has no results")
        dataset = []
        for result in results:
            dataset.append(
                transform_polygon_result(result)
            )
        return dataset