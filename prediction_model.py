import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
from datetime import datetime, timedelta
import joblib
import os

# 데이터 로드
data = pd.read_csv('merged_data.csv', index_col='날짜', parse_dates=True)

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
        Y.append(dataset[i + look_back, 0])  # 첫 번째 특성을 예측
    return np.array(X), np.array(Y)

look_back = 30  # Look-back period를 늘려 더 많은 과거 데이터를 반영
X_train, y_train = create_dataset(train_data, look_back)
X_test, y_test = create_dataset(test_data, look_back)

# LSTM 모델 입력 형태에 맞게 데이터 재구성
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], X_train.shape[2]))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], X_test.shape[2]))

# 학습 단계
def train_model():
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

    # 모델 저장
    model.save('stock_prediction_model.h5')
    joblib.dump(scaler, 'scaler.pkl')

# 예측 단계
def predict_future(stock_data_path):
    # 모델 및 스케일러 로드
    model = load_model('stock_prediction_model.h5')
    scaler = joblib.load('scaler.pkl')

    # 새로운 종목 데이터 로드 및 전처리
    if not os.path.exists(stock_data_path):
        raise FileNotFoundError(f"File not found: {stock_data_path}")
    
    stock_data = pd.read_csv(stock_data_path, index_col='날짜', parse_dates=True)

    # 데이터 스케일링
    if set(stock_data.columns) != set(scaler.feature_names_in_):
        missing_features = set(scaler.feature_names_in_) - set(stock_data.columns)
        for feature in missing_features:
            stock_data[feature] = 0  # 또는 적절한 값으로 채움
        stock_data = stock_data[scaler.feature_names_in_]

    scaled_data = scaler.transform(stock_data)

    # 예측을 위한 데이터 형식 변환
    def create_dataset(dataset, look_back=1):
        X = []
        for i in range(len(dataset) - look_back - 1):
            a = dataset[i:(i + look_back), :]
            X.append(a)
        return np.array(X)

    X_new = create_dataset(scaled_data, look_back)

    # 미래 예측
    def forecast(model, data, look_back, n_future):
        forecasted_data = []
        last_sequence = data[-look_back:]
        if last_sequence.shape[0] < look_back:
            print("Not enough data to make further predictions. Please collect more data.")
            return forecasted_data
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
    
    if len(future_predictions) == 0:
        print("No future predictions available. Not enough data.")
        return
    
    future_predictions_scaled = scaler.inverse_transform(
        np.concatenate((future_predictions.reshape(-1, 1), np.zeros((len(future_predictions), stock_data.shape[1] - 1))), axis=1)
    )[:, 0]

    # 미래 날짜 생성
    last_date = stock_data.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, len(future_predictions) + 1)]

    # 시각화
    plt.figure(figsize=(16, 8))
    plt.plot(stock_data.index, scaler.inverse_transform(scaled_data)[:, 0], label='Actual Stock Price')
    plt.plot(future_dates, future_predictions_scaled, label='Future Predict')
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.legend()
    plt.show()

# 메인 함수
if __name__ == "__main__":
    # 모델이 존재하지 않으면 학습
    if not os.path.exists('stock_prediction_model.h5'):
        train_model()

    # 새로운 종목 데이터 예측
    predict_future('merged_data.csv')  # 입력된 종목 데이터 파일 경로
