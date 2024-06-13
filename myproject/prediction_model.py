# prediction_model.py
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib
from datetime import datetime, timedelta

# 모델과 스케일러 로드
model = load_model('saved_model.h5')
scaler = joblib.load('scaler.gz')

# 데이터 로드
krx_data = pd.read_csv('krx_data.csv')
kospi_data = pd.read_csv('kospi_data.csv')
kosdaq_data = pd.read_csv('kosdaq_data.csv')
gold_data = pd.read_csv('gold_data.csv', index_col='Date', parse_dates=True)
exchange_data = pd.read_csv('exchange_data.csv', index_col='date', parse_dates=True)

# 현재 날짜 기준으로 각 지수의 종가를 가져옴
krx_close = krx_data.groupby('지수명')['종가'].last()
kospi_close = kospi_data.groupby('지수명')['종가'].last()
kosdaq_close = kosdaq_data.groupby('지수명')['종가'].last()

# 추가 데이터를 병합
additional_data = {
    'Gold_Close': gold_data['Close'],
    'Exchange_Rate': exchange_data['basePrice']
}

# 각 지수명별 종가 추가
for idx in krx_close.index:
    additional_data[idx + '_KRX_Close'] = krx_close[idx]
for idx in kospi_close.index:
    additional_data[idx + '_KOSPI_Close'] = kospi_close[idx]
for idx in kosdaq_close.index:
    additional_data[idx + '_KOSDAQ_Close'] = kosdaq_close[idx]

# 추가 데이터를 데이터 프레임으로 변환
additional_df = pd.DataFrame(additional_data)

# 결측값 처리
additional_df.fillna(method='ffill', inplace=True)
additional_df.fillna(method='bfill', inplace=True)

# 데이터 스케일링
scaled_data = scaler.transform(additional_df)

# LSTM 모델을 위한 데이터 형식 변환
def create_dataset(dataset, look_back=1):
    X = []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), :]
        X.append(a)
    return np.array(X)

look_back = 30  # Look-back period를 늘려 더 많은 과거 데이터를 반영
X_data = create_dataset(scaled_data, look_back)

# 예측 데이터를 받아오는 함수
def get_prediction_data():
    # 미래 예측
    n_future = 365  # 1년 뒤까지 예측
    forecasted_data = []
    last_sequence = scaled_data[-look_back:]
    for _ in range(n_future):
        input_data = last_sequence[-look_back:].reshape((1, look_back, X_data.shape[2]))
        prediction = model.predict(input_data)
        forecasted_data.append(prediction[0, 0])
        prediction_expanded = np.zeros((1, X_data.shape[2]))
        prediction_expanded[0, 0] = prediction
        new_sequence = np.concatenate((last_sequence, prediction_expanded), axis=0)
        last_sequence = new_sequence[1:]

    # 스케일링 복원
    forecasted_data = np.array(forecasted_data).reshape(-1, 1)
    forecasted_data = scaler.inverse_transform(np.concatenate((forecasted_data, np.zeros((forecasted_data.shape[0], additional_df.shape[1] - 1))), axis=1))[:, 0]

    # 미래 날짜 생성
    last_date = additional_df.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, n_future + 1)]

    return {
        'dates': [date.strftime('%Y-%m-%d') for date in future_dates],
        'predictions': forecasted_data.tolist()
    }
