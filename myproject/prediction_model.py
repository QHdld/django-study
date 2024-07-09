import pandas as pd
import yfinance as yf
import warnings
from prophet import Prophet
import logging
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

def load_stock_data(stock_code, start_date, end_date):
    try:
        stock_data = yf.download(stock_code, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        logger.debug(f"Stock data loaded for {stock_code}: {stock_data.head()}")
    except Exception as e:
        logger.error(f"Error loading stock data for {stock_code}: {e}")
        raise ValueError(f"No data found for stock code: {stock_code}")
    
    if stock_data.empty:
        logger.error(f"No data found for stock code: {stock_code} in date range {start_date} to {end_date}")
        raise ValueError(f"No data found for stock code: {stock_code} in date range {start_date} to {end_date}")

    stock_data['y'] = stock_data['Close']
    stock_data['ds'] = stock_data.index
    return stock_data

def train_model(stock_data):
    model = Prophet()
    model.fit(stock_data)
    return model

def predict_stock_price(stock_code, start_date, end_date):
    stock_data = load_stock_data(stock_code, start_date, end_date)
    model = train_model(stock_data)
    
    # 예측 시작 날짜를 현재 날짜로 설정
    future = model.make_future_dataframe(periods=365)
    forecast = model.predict(future)
    logger.debug(f"Forecast data for {stock_code}: {forecast.tail()}")

    # 예측 데이터의 첫 번째 값을 실제 데이터의 마지막 값과 동일하게 조정
    if not stock_data.empty:
        last_actual_value = stock_data['y'].iloc[-1]
        forecast.loc[forecast['ds'] > stock_data['ds'].iloc[-1], 'yhat'] = forecast.loc[forecast['ds'] > stock_data['ds'].iloc[-1], 'yhat'].fillna(last_actual_value)

    return forecast[['ds', 'yhat']]

def get_prediction_data(stock_code, start_date, end_date):
    try:
        logger.debug(f"Fetching prediction data for stock code: {stock_code}, start_date: {start_date}, end_date: {end_date}")
        forecast = predict_stock_price(stock_code, start_date, end_date)
        dates = forecast['ds'].dt.strftime('%Y-%m-%d').tolist()
        predictions = forecast['yhat'].tolist()

        return {
            'dates': dates,
            'predictions': predictions
        }
    except Exception as e:
        logger.error(f"Error in get_prediction_data: {e}")
        raise
