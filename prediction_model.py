import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, LSTM
from datetime import datetime, timedelta

# 데이터 로드
stock_data = pd.read_csv('stock_data.csv', index_col='날짜', parse_dates=True)
krx_data = pd.read_csv('krx_data.csv')
kospi_data = pd.read_csv('kospi_data.csv')
kosdaq_data = pd.read_csv('kosdaq_data.csv')
gold_data = pd.read_csv('gold_data.csv', index_col='Date', parse_dates=True)
exchange_data = pd.read_csv('exchange_data.csv', index_col='date', parse_dates=True)

# 현재 날짜 기준으로 각 지수의 종가를 가져옴
krx_close = krx_data.groupby('지수명')['종가'].last()
kospi_close = kospi_data.groupby('지수명')['종가'].last()
kosdaq_close = kosdaq_data.groupby('지수명')['종가'].last()

# 데이터를 합칠 DataFrame 생성
data = pd.DataFrame(index=stock_data.index)

# 주식 데이터 추가
data['Stock_Close'] = stock_data['종가']

# 각 지수명별 종가 추가
additional_data = {}
for idx in krx_close.index:
    additional_data[idx + '_KRX_Close'] = krx_close[idx]

for idx in kospi_close.index:
    additional_data[idx + '_KOSPI_Close'] = kospi_close[idx]

for idx in kosdaq_close.index:
    additional_data[idx + '_KOSDAQ_Close'] = kosdaq_close[idx]

# 금 값 및 환율 추가
additional_data['Gold_Close'] = gold_data['Close']
additional_data['Exchange_Rate'] = exchange_data['basePrice']

# 추가할 데이터를 데이터 프레임으로 변환하고 기존 데이터와 병합
additional_df = pd.DataFrame(additional_data, index=[data.index[-1]])
data = pd.concat([data, additional_df], axis=1)

# 결측값 처리
data.fillna(method='ffill', inplace=True)
data.fillna(method='bfill', inplace=True)

# 데이터 스케일링
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# 훈련 데이터와 테스트 데이터 분할
train_size = int(len(scaled_data) * 0.8)
train_data, test_data = scaled_data[:train_size], scaled_data[train_size:]

# LSTM 모델을 위한 데이터 형식 변환
def create_dataset(dataset, look_back=1):
    X, Y = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), :]
        X.append(a)
        Y.append(dataset[i + look_back, 0])  # 주식 가격 예측
    return np.array(X), np.array(Y)

look_back = 10
X_train, y_train = create_dataset(train_data, look_back)
X_test, y_test = create_dataset(test_data, look_back)

# LSTM 모델 입력 형태에 맞게 데이터 재구성
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], X_train.shape[2]))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], X_test.shape[2]))

# 더 깊은 LSTM 모델 생성
model = Sequential()
model.add(LSTM(100, return_sequences=True, input_shape=(look_back, X_train.shape[2])))
model.add(LSTM(100, return_sequences=True))
model.add(LSTM(50))
model.add(Dense(25))
model.add(Dense(1))

# 모델 컴파일
model.compile(optimizer='adam', loss='mean_squared_error')

# 모델 훈련
model.fit(X_train, y_train, batch_size=1, epochs=50)

# 예측
train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

# 원래 스케일로 변환
train_predict = scaler.inverse_transform(np.concatenate((train_predict, np.zeros((train_predict.shape[0], data.shape[1]-1))), axis=1))[:, 0]
test_predict = scaler.inverse_transform(np.concatenate((test_predict, np.zeros((test_predict.shape[0], data.shape[1]-1))), axis=1))[:, 0]

# 미래 예측
def forecast(model, data, look_back, n_future):
    forecasted_data = []
    last_sequence = data[-look_back:]
    for _ in range(n_future):
        input_data = last_sequence[-look_back:].reshape((1, look_back, data.shape[1]))
        prediction = model.predict(input_data)
        forecasted_data.append(prediction[0, 0])
        prediction_expanded = np.zeros((1, data.shape[1]))
        prediction_expanded[0, 0] = prediction
        new_sequence = np.concatenate((last_sequence, prediction_expanded), axis=0)
        last_sequence = new_sequence[1:]
    return np.array(forecasted_data)

n_future = 365  # 1년 뒤까지 예측
future_predictions = forecast(model, scaled_data, look_back, n_future)

# 미래 예측 값을 원래 스케일로 변환
future_predictions_scaled = scaler.inverse_transform(np.concatenate((future_predictions.reshape(-1, 1), np.zeros((n_future, data.shape[1]-1))), axis=1))[:, 0]

# 미래 날짜 생성
last_date = data.index[-1]
future_dates = [last_date + timedelta(days=i) for i in range(1, n_future + 1)]

# 시각화
plt.figure(figsize=(16, 8))
plt.plot(data.index, scaler.inverse_transform(scaled_data)[:, 0], label='Actual Stock Price')
plt.plot(data.index[look_back:len(train_predict) + look_back], train_predict, label='Train Predict')
plt.plot(data.index[len(train_predict) + (look_back * 2) + 1:len(data) - 1], test_predict, label='Test Predict')
plt.plot(future_dates, future_predictions_scaled, label='Future Predict')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.show()
