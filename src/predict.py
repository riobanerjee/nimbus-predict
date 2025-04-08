# src/predict.py
import joblib
import sys

def load_model(model_path):
    return joblib.load(model_path)

def predict(model, humidity_value):
    """
    Generate a prediction using the provided model and humidity value.

    Args:
        model: A trained machine learning model with a `predict` method.
        humidity_value (float): The humidity value to be used as input for the prediction.

    Returns:
        float: The predicted value based on the input humidity value.
    """
    prediction = model.predict([[humidity_value]])
    return prediction[0]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python predict.py <humidity_value>")
        sys.exit(1)
    humidity_value = float(sys.argv[1])
    model = load_model("../model/model.pkl")
    result = predict(model, humidity_value)
    print(f"Predicted temperature: {result:.2f}°C")
