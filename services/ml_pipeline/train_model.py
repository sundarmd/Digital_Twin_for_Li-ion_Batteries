import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import psycopg2
import os
import sys
from sklearn.exceptions import NotFittedError
import numpy as np
from Digital_Twin_for_Li-ion_Batteries.config import *

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

def load_data():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        query = "SELECT voltage_measured, current_measured, temperature_measured, capacity FROM battery_data"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)

def validate_data(df):
    if df.empty:
        logger.error("No data available for training")
        return False
    
    required_columns = ['voltage_measured', 'current_measured', 'temperature_measured', 'capacity']
    if not all(col in df.columns for col in required_columns):
        logger.error(f"Missing required columns. Expected: {required_columns}")
        return False
    
    if df.isnull().values.any():
        logger.error("Dataset contains null values")
        return False
    
    return True

def preprocess_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    df['cumulated_time'] = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds()
    df['power_W'] = df['voltage_measured'] * abs(df['current_measured'])
    df['energy_Wh'] = df['power_W'] * (df['time'] / 3600)
    return df

def train_model(X, y):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    return mse

def save_model(model, filename):
    joblib.dump(model, filename)

def main():
    try:
        df = load_data()
        if not validate_data(df):
            logger.error("Data validation failed. Exiting.")
            return

        df = preprocess_data(df)

        X = df[['voltage_measured', 'current_measured', 'temperature_measured']]
        y = df['capacity']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = train_model(X_train, y_train)
        mse = evaluate_model(model, X_test, y_test)
        logger.info(f"Model MSE: {mse}")

        save_model(model, MODEL_PATH_RF)
    except NotFittedError:
        logger.error("Error: Model not fitted. Check if there's enough data for training.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()