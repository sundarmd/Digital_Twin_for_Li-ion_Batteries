import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import psycopg2
import os
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def load_data():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    query = "SELECT voltage, current, temperature, capacity, timestamp FROM battery_data"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def preprocess_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    df['cumulated_time'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()
    return df

def create_sequences(X, y, time_steps=10):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        Xs.append(X.iloc[i:(i + time_steps)].values)
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)

def train_lstm_model(X, y):
    model = Sequential([
        LSTM(50, activation='relu', input_shape=(X.shape[1], X.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2, verbose=1)
    return model

def main():
    df = load_data()
    df = preprocess_data(df)

    features = ['voltage', 'current', 'temperature', 'cumulated_time']
    target = 'capacity'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Prepare data for LSTM
    time_steps = 10
    X_train_seq, y_train_seq = create_sequences(X_train, y_train, time_steps)
    X_test_seq, y_test_seq = create_sequences(X_test, y_test, time_steps)

    # Train LSTM model
    lstm_model = train_lstm_model(X_train_seq, y_train_seq)
    
    # Evaluate LSTM model
    lstm_predictions = lstm_model.predict(X_test_seq)
    lstm_mse = mean_squared_error(y_test_seq, lstm_predictions)
    print(f"LSTM Model MSE: {lstm_mse}")

    # Save LSTM model
    lstm_model.save('battery_health_lstm_model.h5')

    # Train RandomForest model (keeping the existing code)
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_mse = mean_squared_error(y_test, rf_model.predict(X_test))
    print(f"RandomForest Model MSE: {rf_mse}")
    joblib.dump(rf_model, 'battery_health_rf_model.joblib')

if __name__ == "__main__":
    main()