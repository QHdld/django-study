# financial_info_for_front.py

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

# views.py

import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from prediction_model import get_prediction_data
from financial_info_for_front import MarketDataFetcher, ExchangeRateDataFetcher, GoldPriceFetcher, StockDataFetcher, StockNameConverter
import pandas as pd

logger = logging.getLogger(__name__)

def market_data_view(request):
    market_fetcher = MarketDataFetcher()
    market_data = market_fetcher.get_market_prices_for_ui()

    exchange_fetcher = ExchangeRateDataFetcher()
    exchange_data = exchange_fetcher.get_all_exchange_rates()

    gold_fetcher = GoldPriceFetcher()
    gold_data = gold_fetcher.get_gold_price()

    context = {**market_data, **exchange_data, **gold_data}
    return render(request, 'myapp/market_data.html', context)

@csrf_exempt
def show_chart(request):
    if request.method == "POST":
        stock_names = request.POST.getlist('stock_names')
        date_range = request.POST.get('date_range')
        logger.debug(f"Received stock_names: {stock_names}, date_range: {date_range}")

        if not stock_names:
            return JsonResponse({'error': 'No stock names provided'}, status=400)
        
        converter = StockNameConverter()
        stock_codes = [converter.convert_name_to_code(stock_name) for stock_name in stock_names]
        
        if None in stock_codes:
            return JsonResponse({'error': 'Invalid stock name(s)'}, status=400)

        # 기간 범위에 따른 시작 날짜 계산
        end_date = pd.to_datetime('today')
        if date_range == '5y':
            start_date = end_date - pd.DateOffset(years=5)
        elif date_range == '3y':
            start_date = end_date - pd.DateOffset(years=3)
        elif date_range == '1y':
            start_date = end_date - pd.DateOffset(years=1)
        elif date_range == '6m':
            start_date = end_date - pd.DateOffset(months=6)
        else:
            return JsonResponse({'error': 'Invalid date range'}, status=400)

        data_fetcher = StockDataFetcher()
        all_data = []
        for stock_code in stock_codes:
            labels, data = data_fetcher.get_stock_data(stock_code, start_date, end_date)
            all_data.append({'stock_code': stock_code, 'labels': labels, 'data': data})

        return JsonResponse({'all_data': all_data})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_prediction_view(request):
    if request.method == "POST":
        try:
            stock_name = request.POST.get('stock_name')
            date_range = request.POST.get('date_range')
            logger.debug(f"Received stock_name: {stock_name}, date_range: {date_range}")

            if not stock_name:
                return JsonResponse({'error': 'No stock name provided'}, status=400)
            
            converter = StockNameConverter()
            stock_code = converter.convert_name_to_code(stock_name)
            
            if not stock_code:
                return JsonResponse({'error': 'Invalid stock name'}, status=400)

            # 기간 범위에 따른 시작 날짜 계산
            end_date = pd.to_datetime('today')
            if date_range == '5y':
                start_date = end_date - pd.DateOffset(years=5)
            elif date_range == '3y':
                start_date = end_date - pd.DateOffset(years=3)
            elif date_range == '1y':
                start_date = end_date - pd.DateOffset(years=1)
            elif date_range == '6m':
                start_date = end_date - pd.DateOffset(months=6)
            else:
                return JsonResponse({'error': 'Invalid date range'}, status=400)

            logger.debug(f"Fetching prediction data from {start_date} to {end_date}")
            prediction_data = get_prediction_data(stock_code, start_date, end_date)
            logger.debug(f"Prediction data: {prediction_data}")
            return JsonResponse(prediction_data)
        except Exception as e:
            logger.error(f"Error in get_prediction_view: {e}")
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
