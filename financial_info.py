import requests
import json
from pykrx import stock
from pykrx import bond
import yfinance as yf
from time import sleep
from datetime import datetime
from dateutil.relativedelta import relativedelta

now = datetime.now()
today = now.strftime("%Y%m%d")
yesterday = now - relativedelta(days=1)
before_one_week = now - relativedelta(weeks=1)
before_one_month = now - relativedelta(months=1)

class StockPriceFetcher:
    def get_stockprice(self):
        # 시장별 지수
        df_KRX = stock.get_index_price_change(before_one_week, today, "KRX")
        df_KOSPI = stock.get_index_price_change(before_one_week, today, "KOSPI")
        df_KOSDAQ = stock.get_index_price_change(before_one_week, today, "KOSDAQ")

        # 주종목 별 지수
        df_00020 = stock.get_market_ohlcv(before_one_week, now, "000020")
        print(df_00020)
        print(df_KRX.head(1))
        print(df_KOSPI.head(1))
        print(df_KOSDAQ.head(1))
        return df_KOSDAQ, df_KOSPI, df_KRX

class ExchangeRateFetcher:
    def __init__(self, access_key, currency):
        self.access_key = access_key
        self.currency = currency

    def get_DunamuAPI(self):
        url = f"https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRW{currency}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_key}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            exchange_rate_data = response.json()
            exchange_rate_data_basePrice = exchange_rate_data[0]['basePrice']
            exchange_rate_data_currencyName = exchange_rate_data[0]['currencyName'] # 대상 통화명
            exchange_rate_data_highPrice = exchange_rate_data[0]['highPrice'] # 당일 최고 환율
            exchange_rate_data_lowPrice = exchange_rate_data[0]['lowPrice'] # 당일 최저 환율
            exchange_rate_data_change = exchange_rate_data[0]['change'] # 전일 대비 가격 변동 상태
            exchange_rate_data_changePrice = exchange_rate_data[0]['changePrice'] # 전일 대비 변동 가격

            print(f'{exchange_rate_data_currencyName}/KRW의 현재 환율: ', exchange_rate_data_basePrice)
            print('당일 최고/최저 환율: ', exchange_rate_data_highPrice, '/', exchange_rate_data_lowPrice)
            print('전일 대비 변동 가격: ', exchange_rate_data_change, exchange_rate_data_changePrice)
            return exchange_rate_data_basePrice, exchange_rate_data_currencyName, exchange_rate_data_highPrice, exchange_rate_data_lowPrice, exchange_rate_data_changePrice, exchange_rate_data_change
        else:
            print('error')
            return None

class GoldPriceFetcher:
    def get_goldprice(self):
        gold = yf.download('GC=F', before_one_week, now, auto_adjust=True)
        print(gold)
        return gold

if __name__ == '__main__':
    stock_rate = StockPriceFetcher()
    stock_rate.get_stockprice()

    access_key = 'nfiQF5JrJm7RKRpZfaqjyaLXdRccy7pQm2rI3BYf'
    # secret_key = 'KFG2dksaxNfNyWP2qY9hhvFtPgZhxsqm7mEvx3aO'
    currency = 'JPY'
    exchange_rate = ExchangeRateFetcher(access_key, currency)
    exchange_rate.get_DunamuAPI()

    gold_rate = GoldPriceFetcher()
    gold_rate.get_goldprice()