import requests
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

now = datetime.now()
today = now.strftime("%Y-%m-%d")
weekday = now.weekday()

if weekday == 5:
    yesterday = (now - timedelta(days=2)).strftime("%Y-%m-%d")
    today = (now - timedelta(days=2)).strftime("%Y-%m-%d")
elif weekday == 6:
    yesterday = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    today = (now - timedelta(days=3)).strftime("%Y-%m-%d")
else:
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

before_five_year = (now - timedelta(days=5*365)).strftime("%Y-%m-%d")

class MarketDataFetcher:
    def get_market_prices_for_ui(self):
        def get_stock_data(stock_code):
            stock = yf.download(stock_code, before_five_year, today)
            return stock

        def get_value_or_message(data, key, message='주말입니다'):
            if not data.empty and key in data.columns:
                return data[key].values[0]
            return message

        # 삼성전자
        samsung_electronics = get_stock_data("005930.KS")
        samsung_electronics_open_price = get_value_or_message(samsung_electronics, 'Open')
        samsung_electronics_change_rate = float(get_value_or_message(samsung_electronics, 'Close')) - float(get_value_or_message(samsung_electronics, 'Open'))

        # SK 하이닉스
        sk_hynix = get_stock_data("000660.KS")
        sk_hynix_open_price = get_value_or_message(sk_hynix, 'Open')
        sk_hynix_change_rate = float(get_value_or_message(sk_hynix, 'Close')) - float(get_value_or_message(sk_hynix, 'Open'))

        # KOSPI
        kospi = get_stock_data("^KS11")
        kospi_open_price = get_value_or_message(kospi, 'Open')
        kospi_change_rate = float(get_value_or_message(kospi, 'Close')) - float(get_value_or_message(kospi, 'Open'))

        # KOSDAQ
        kosdaq = get_stock_data("^KQ11")
        kosdaq_open_price = get_value_or_message(kosdaq, 'Open')
        kosdaq_change_rate = float(get_value_or_message(kosdaq, 'Close')) - float(get_value_or_message(kosdaq, 'Open'))

        # KRX 300
        krx300 = get_stock_data("AAPL")
        krx300_open_price = get_value_or_message(krx300, 'Open')
        krx300_change_rate = float(get_value_or_message(krx300, 'Close')) - float(get_value_or_message(krx300, 'Open'))

        return {
            "yesterday_kospi_open_price": kospi_open_price,
            "yesterday_kospi_change_rate": kospi_change_rate,
            "yesterday_kosdaq_open_price": kosdaq_open_price,
            "yesterday_kosdaq_change_rate": kosdaq_change_rate,
            "yesterday_krx300_open_price": krx300_open_price,
            "yesterday_krx300_change_rate": krx300_change_rate,
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
    def get_exchange_data(self, stock_code):
        stock = yf.download(stock_code, start=before_five_year, end=today)
        return stock

    def get_value(self, data, key, message='주말입니다'):
        if not data.empty and key in data.columns:
            return data[key].iloc[0]  # 첫 번째 값을 반환
        return message

    def get_exchange_rate(self):
        # USD
        usd = self.get_exchange_data("USDKRW=X")
        usd_open_price = float(self.get_value(usd, 'Open'))
        usd_close_price = float(self.get_value(usd, 'Close'))
        usd_change_rate = usd_close_price - usd_open_price

        # JPY
        jpy = self.get_exchange_data("JPYKRW=X")
        jpy_open_price = float(self.get_value(jpy, 'Open'))
        jpy_close_price = float(self.get_value(jpy, 'Close'))
        jpy_change_rate = jpy_close_price - jpy_open_price

        # CNY
        # cny = self.get_exchange_data("CNYKRW=X")
        cny_open_price = 189.64
        # cny_close_price = float(self.get_value(cny, 'Close'))
        cny_change_rate = 0.37

        # EUR
        eur = self.get_exchange_data("EURKRW=X")
        eur_open_price = float(self.get_value(eur, 'Open'))
        eur_close_price = float(self.get_value(eur, 'Close'))
        eur_change_rate = eur_close_price - eur_open_price

        return {
            "usd_basePrice": usd_open_price,
            "usd_changePrice": usd_change_rate,
            "jpy_basePrice": jpy_open_price,
            "jpy_changePrice": jpy_change_rate,
            "cny_basePrice": cny_open_price,
            "cny_changePrice": cny_change_rate,
            "eur_basePrice": eur_open_price,
            "eur_changePrice": eur_change_rate
        }

    def get_all_exchange_rates(self):
        exchange_rates = self.get_exchange_rate()
        return exchange_rates

class GoldPriceFetcher:
    def get_gold_price(self):
        gold = yf.download('GC=F', start=before_five_year, end=today, auto_adjust=True)
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
    def __init__(self):
        self.stock_list = {
            "삼성전자": "005930.KS",
            "SK하이닉스": "000660.KS",
            "현대차": "005380.KS",
            "LG화학": "051910.KS",
            "NAVER": "035420.KS",
            "CJ": "001040.KS",
        }

    def convert_name_to_code(self, stock_name):
        return self.stock_list.get(stock_name, None)

class StockDataFetcher:
    def get_stock_data(self, stock_code, start_date, end_date):
        df = yf.download(stock_code, start=start_date, end=end_date)
        df = df.reset_index()
        labels = df['Date'].astype(str).tolist()
        data = df['Close'].tolist()
        return labels, data
