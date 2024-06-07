import requests
import json
from pykrx import stock
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

now = datetime.now()
today = now.strftime("%Y%m%d")
before_five_years = now - relativedelta(years=5)

class StockPriceFetcher:
    def get_stockprice(self):
        # 시장별 지수
        df_KRX = stock.get_index_ohlcv_by_date(before_five_years, today, "1001")  # KRX 종합지수
        df_KOSPI = stock.get_index_ohlcv_by_date(before_five_years, today, "1002")  # KOSPI 지수
        df_KOSDAQ = stock.get_index_ohlcv_by_date(before_five_years, today, "2001")  # KOSDAQ 지수

        # 데이터 저장
        df_KRX.to_csv('krx_data.csv')
        df_KOSPI.to_csv('kospi_data.csv')
        df_KOSDAQ.to_csv('kosdaq_data.csv')
        return df_KRX, df_KOSPI, df_KOSDAQ

class ExchangeRateFetcher:
    def __init__(self, access_key, currency):
        self.access_key = access_key
        self.currency = currency

    def get_DunamuAPI(self):
        url = f"https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRW{self.currency}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_key}'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            exchange_rate_data = response.json()
            df_exchange_rate = pd.DataFrame(exchange_rate_data)
            df_exchange_rate.to_csv('exchange_data.csv', index=False)
            return df_exchange_rate
        else:
            print('error')
            return None

class GoldPriceFetcher:
    def get_goldprice(self):
        gold = yf.download('GC=F', start=before_five_years, end=now, auto_adjust=True)
        gold.to_csv('gold_data.csv')
        return gold

if __name__ == '__main__':
    stock_fetcher = StockPriceFetcher()
    df_KRX, df_KOSPI, df_KOSDAQ = stock_fetcher.get_stockprice()

    access_key = 'your_access_key_here'  # 실제 액세스 키로 교체
    currency = 'JPY'
    exchange_fetcher = ExchangeRateFetcher(access_key, currency)
    df_exchange_rate = exchange_fetcher.get_DunamuAPI()

    gold_fetcher = GoldPriceFetcher()
    df_gold = gold_fetcher.get_goldprice()

    # 데이터 병합
    df_merged = df_KRX[['종가']].rename(columns={'종가': 'KRX_Close'})
    df_merged['KOSPI_Close'] = df_KOSPI['종가']
    df_merged['KOSDAQ_Close'] = df_KOSDAQ['종가']
    df_merged = df_merged.join(df_gold['Close'].rename('Gold_Close'), how='left')
    df_merged = df_merged.join(df_exchange_rate.set_index('date')['basePrice'].rename('Exchange_Rate'), how='left')

    df_merged.fillna(method='ffill', inplace=True)
    df_merged.fillna(method='bfill', inplace=True)

    df_merged.to_csv('merged_data.csv')
