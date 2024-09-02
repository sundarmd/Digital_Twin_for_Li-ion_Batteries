import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import psycopg2
import os

def load_data():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    query = "SELECT voltage, current, temperature, capacity FROM battery_data"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def preprocess_data(df):
    # Add any necessary preprocessing steps here
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
    df = load_data()
    df = preprocess_data(df)

    X = df[['voltage', 'current', 'temperature']]
    y = df['capacity']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = train_model(X_train, y_train)
    mse = evaluate_model(model, X_test, y_test)
    print(f"Model MSE: {mse}")

    save_model(model, 'battery_health_model.joblib')

if __name__ == "__main__":
    main()