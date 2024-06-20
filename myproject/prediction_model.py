import pandas as pd
import FinanceDataReader as fdr
import warnings
from prophet import Prophet
import logging
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

def load_stock_data(stock_code):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - pd.DateOffset(years=5)).strftime('%Y-%m-%d')
    
    try:
        stock_data = fdr.DataReader(stock_code, start_date, end_date)
        logger.debug(f"Stock data loaded for {stock_code}: {stock_data.head()}")
    except Exception as e:
        logger.error(f"Error loading stock data for {stock_code}: {e}")
        raise ValueError(f"No data found for stock code: {stock_code}")
    
    if stock_data.empty:
        logger.error(f"No data found for stock code: {stock_code}")
        raise ValueError(f"No data found for stock code: {stock_code}")

    stock_data['y'] = stock_data['Close']
    stock_data['ds'] = stock_data.index
    return stock_data

def train_model(stock_data):
    model = Prophet()
    model.fit(stock_data)
    return model

def predict_stock_price(stock_code):
    stock_data = load_stock_data(stock_code)
    model = train_model(stock_data)
    
    # 예측 시작 날짜를 현재 날짜로 설정
    future = model.make_future_dataframe(periods=365)
    forecast = model.predict(future)
    logger.debug(f"Forecast data for {stock_code}: {forecast.tail()}")

    return forecast[['ds', 'yhat']]

def get_prediction_data(stock_code):
    try:
        logger.debug(f"Fetching prediction data for stock code: {stock_code}")
        forecast = predict_stock_price(stock_code)
        dates = forecast['ds'].dt.strftime('%Y-%m-%d').tolist()
        predictions = forecast['yhat'].tolist()

        return {
            'dates': dates,
            'predictions': predictions
        }
    except Exception as e:
        logger.error(f"Error in get_prediction_data: {e}")
        raise
