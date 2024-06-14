import requests
import json
from pykrx import stock
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

now = datetime.now()
today = now.strftime("%Y-%m-%d")
yesterday = (now-relativedelta(days=1)).strftime("%Y-%m-%d")
before_five_year = (now - relativedelta(years=5)).strftime("%Y-%m-%d")

class MarketDataFetcher:
    def get_market_prices_for_ui(self):
        # 코스피 시가, 등락률
        yesterday_kospi_price = stock.get_index_price_change(yesterday, today, "KOSPI").head(1)
        yesterday_kospi_open_price = yesterday_kospi_price['시가'].values[0]
        yesterday_kospi_change_rate = yesterday_kospi_price['등락률'].values[0]

        # 코스닥 시가, 등락률
        yesterday_kosdaq_price = stock.get_index_price_change(yesterday, today, "KOSDAQ").head(1)
        yesterday_kosdaq_open_price = yesterday_kosdaq_price['시가'].values[0]
        yesterday_kosdaq_change_rate = yesterday_kosdaq_price['등락률'].values[0]
    
        # KRX 300 시가, 등락률
        yesterday_krx300_price = stock.get_index_price_change(yesterday, today, "KRX").head(1)
        yesterday_krx300_open_price = yesterday_krx300_price['시가'].values[0]
        yesterday_krx300_change_rate = yesterday_krx300_price['등락률'].values[0]

        # 코스피 시가, 등락률
        kospi_price = stock.get_index_price_change(before_five_year, today, "KOSPI").head(1)
        kospi_open_price = kospi_price['시가'].values[0]
        kospi_change_rate = kospi_price['등락률'].values[0]

        # 코스닥 시가, 등락률
        kosdaq_price = stock.get_index_price_change(before_five_year, today, "KOSDAQ").head(1)
        kosdaq_open_price = kosdaq_price['시가'].values[0]
        kosdaq_change_rate = kosdaq_price['등락률'].values[0]
    
        # KRX 300 시가, 등락률
        krx300_price = stock.get_index_price_change(before_five_year, today, "KRX").head(1)
        krx300_open_price = krx300_price['시가'].values[0]
        krx300_change_rate = krx300_price['등락률'].values[0]

        # 삼성전자
        samsung_electronics = stock.get_market_ohlcv(yesterday, today, "005930", adjusted=False).head(1)
        samsung_electronics_open_price = samsung_electronics['시가'].values[0]
        samsung_electronics_change_rate = samsung_electronics['등락률'].values[0]

        # sk 하이닉스
        sk_hynix  = stock.get_market_ohlcv(yesterday, today, "000660", adjusted=False).head(1)
        sk_hynix_open_price = sk_hynix['시가'].values[0]
        sk_hynix_change_rate = sk_hynix['등락률'].values[0]

        return {
            "yesterday_kospi_open_price": yesterday_kospi_open_price,
            "yesterday_kospi_change_rate": yesterday_kospi_change_rate,
            "yesterday_kosdaq_open_price": yesterday_kosdaq_open_price,
            "yesterday_kosdaq_change_rate": yesterday_kosdaq_change_rate,
            "yesterday_krx300_open_price": yesterday_krx300_open_price,
            "yesterday_krx300_change_rate": yesterday_krx300_change_rate,
            "kospi_open_price": kospi_open_price,
            "kospi_change_rate": kospi_change_rate,
            "kosdaq_open_price": kosdaq_open_price,
            "kosdaq_change_rate": kosdaq_change_rate,
            "krx300_open_price": krx300_open_price,
            "krx300_change_rate": krx300_change_rate,
            'samsung_electronics_open_price': samsung_electronics_open_price,
            'samsung_electronics_change_rate': samsung_electronics_change_rate,
            'sk_hynix_open_price': sk_hynix_open_price,
            'sk_hynix_change_rate': sk_hynix_change_rate,
        }

class ExchangeRateDataFetcher:
    def __init__(self, access_key):
        self.access_key = access_key

    def get_exchange_rate(self, currency):
        url = f"https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRW{currency}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_key}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            exchange_rate_data = response.json()
            if exchange_rate_data:
                base_price = exchange_rate_data[0]['basePrice']
                change_price = exchange_rate_data[0]['changePrice']
                change_status = exchange_rate_data[0]['change']
                
                if change_status == 'RISE':
                    change_status = '+'
                elif change_status == 'FALL':
                    change_status = '-'
                else:
                    change_status = ''
                
                return base_price, change_price, change_status
        return None, None, None

    def get_all_exchange_rates(self):
        currencies = ['USD', 'CNY', 'EUR', 'JPY']
        exchange_rates = {}
        
        for currency in currencies:
            base_price, change_price, change_status = self.get_exchange_rate(currency)
            if base_price is not None:
                exchange_rates[f'{currency.lower()}_basePrice'] = base_price
                exchange_rates[f'{currency.lower()}_changePrice'] = change_price
                exchange_rates[f'{currency.lower()}_changeStatus'] = change_status
        
        return exchange_rates

class GoldPriceFetcher:
    def get_gold_price(self):
        gold = yf.download('GC=F', start=before_five_year, end=datetime.now().strftime('%Y-%m-%d'), auto_adjust=True)
        gold_last = gold.iloc[-1]
        gold_open = gold_last['Open']
        gold_close = gold_last['Close']
        gold_high = gold_last['High']
        gold_low = gold_last['Low']
        return {
            "gold_open": gold_open,
            "gold_close": gold_close,
            "gold_high": gold_high,
            "gold_low": gold_low
        }

class StockNameConverter:
    def convert_name_to_code(self, stock_name):
        stock_list = stock.get_market_ticker_list(market="ALL")
        for stock_code in stock_list:
            stock_info = stock.get_market_ticker_name(stock_code)
            if stock_info == stock_name:
                return stock_code
        return None

class StockDataFetcher:
    def get_stock_data(self, stock_code):
        df = stock.get_market_ohlcv_by_date(before_five_year, today, stock_code)
        df = df.reset_index()
        labels = df['날짜'].astype(str).tolist()
        data = df['종가'].tolist()
        return labels, data
