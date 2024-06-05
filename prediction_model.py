import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
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

# 주식 데이터와 추가 데이터를 병합
additional_data = {
    'Stock_Close': stock_data['종가'],
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
additional_df = pd.DataFrame(additional_data, index=stock_data.index)

# 결측값 처리
additional_df.fillna(method='ffill', inplace=True)
additional_df.fillna(method='bfill', inplace=True)

# 데이터 스케일링
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(additional_df)

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

look_back = 30  # Look-back period를 늘려 더 많은 과거 데이터를 반영
X_train, y_train = create_dataset(train_data, look_back)
X_test, y_test = create_dataset(test_data, look_back)

# LSTM 모델 입력 형태에 맞게 데이터 재구성
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], X_train.shape[2]))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], X_test.shape[2]))

# 더 깊은 LSTM 모델 생성
model = Sequential()
model.add(LSTM(128, return_sequences=True, input_shape=(look_back, X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(128, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(64, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(64, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(50))
model.add(Dense(25))
model.add(Dense(1))

# 모델 컴파일
optimizer = Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='mean_squared_error')

# 모델 훈련
history = model.fit(X_train, y_train, batch_size=16, epochs=200, validation_split=0.1)

# 예측
train_predict = model.predict(X_train)
test_predict = model.predict(X_test)

# 원래 스케일로 변환
def inverse_transform(predictions, scaler, n_features):
    expanded_predictions = np.concatenate((predictions, np.zeros((predictions.shape[0], n_features-1))), axis=1)
    return scaler.inverse_transform(expanded_predictions)[:, 0]

train_predict = inverse_transform(train_predict, scaler, additional_df.shape[1])
test_predict = inverse_transform(test_predict, scaler, additional_df.shape[1])

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
future_predictions_scaled = inverse_transform(future_predictions.reshape(-1, 1), scaler, additional_df.shape[1])

# 미래 날짜 생성
last_date = additional_df.index[-1]
future_dates = [last_date + timedelta(days=i) for i in range(1, n_future + 1)]

# 시각화
plt.figure(figsize=(16, 8))
plt.plot(additional_df.index, scaler.inverse_transform(scaled_data)[:, 0], label='Actual Stock Price')
plt.plot(additional_df.index[look_back:len(train_predict) + look_back], train_predict, label='Train Predict')
plt.plot(additional_df.index[len(train_predict) + (look_back * 2) + 1:len(additional_df) - 1], test_predict, label='Test Predict')
plt.plot(future_dates, future_predictions_scaled, label='Future Predict')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.show()
