# src/train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib

def load_data(path):
    df = pd.read_csv(path)
    return df

def train_model(df):
    """
    Trains a linear regression model to predict temperature based on humidity.

    Args:
        df (pandas.DataFrame): A DataFrame containing the input features and target variable.
            - The DataFrame must include the following columns:
                - 'humidity': Feature used for training the model.
                - 'temp': Target variable to predict.

    Returns:
        sklearn.linear_model.LinearRegression: The trained linear regression model.

    Prints:
        str: The R^2 score of the model on the training set.
    """
    X = df[['humidity']]
    y = df['temp']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    print(f"Model trained, R^2 on training set: {model.score(X_train, y_train):.2f}")
    return model

if __name__ == "__main__":
    data_path = "../data/cleaned_data.csv"
    df = load_data(data_path)
    model = train_model(df)
    joblib.dump(model, "../model/model.pkl")
    print("Trained model saved to ../model/model.pkl")
