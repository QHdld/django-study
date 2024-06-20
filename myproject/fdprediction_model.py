import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import FinanceDataReader as fdr
import seaborn as sns
import warnings
import os
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

warnings.filterwarnings('ignore')

# 시계열 데이터 예측 시작
# 종목 데이터
STOCK_CODE = '005930'

stock = fdr.DataReader(STOCK_CODE)
stock.tail()
stock.index
stock = fdr.DataReader(STOCK_CODE, '2020')

# facebook prophet
stock['y'] = stock['Close']
stock['ds'] = stock.index

# prophet 객체 선언 및 학습
m = Prophet()
m.fit(stock)

future = m.make_future_dataframe(periods=365)
future.tail()

forecast = m.predict(future)
forecast.tail()

# 위에서 yhat열이 예측한 값임
m = Prophet()
forecast = m.fit(stock).predict(future)
fig = m.plot(forecast)

forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].iloc[-40:-20]
