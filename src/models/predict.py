import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class WeatherPredictor:
    """Class to make weather predictions using trained model."""
    
    def __init__(self, model_path="models/weather_prediction_model.joblib"):
        """Initialize the predictor with a trained model."""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model = joblib.load(model_path)
        
        # Load model info if available
        info_path = "models/model_info.json"
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                self.model_info = json.load(f)
        else:
            self.model_info = {"model_name": "unknown"}
    
    def prepare_input_data(self, city, country, current_weather):
        """Prepare input data for prediction."""
        # Create a DataFrame with the required features
        input_data = pd.DataFrame({
            'city': [city],
            'country': [country],
            'temp': [current_weather['temp']],
            'feels_like': [current_weather['feels_like']],
            'humidity': [current_weather['humidity']],
            'pressure': [current_weather['pressure']],
            'wind_speed': [current_weather['wind_speed']],
            'clouds': [current_weather['clouds']],
            'weather_main': [current_weather['weather_main']],
            'hour': [datetime.now().hour],
            'day': [datetime.now().day],
            'month': [datetime.now().month]
        })
        
        return input_data
    
    def predict_next_day(self, city, country, current_weather):
        """Predict temperature for the next day."""
        # Prepare input data
        input_data = self.prepare_input_data(city, country, current_weather)
        
        # Make prediction
        prediction = self.model.predict(input_data)
        
        return prediction[0]
    
    def predict_next_days(self, city, country, current_weather, days=5):
        """Predict temperature for the next several days."""
        predictions = []
        dates = []
        
        # Copy current weather for modifications
        weather = current_weather.copy()
        today = datetime.now()
        
        for i in range(days):
            # Predict next day temperature
            next_temp = self.predict_next_day(city, country, weather)
            
            # Calculate prediction date
            prediction_date = today + timedelta(days=i+1)
            
            # Store prediction
            predictions.append(next_temp)
            dates.append(prediction_date.strftime('%Y-%m-%d'))
            
            # Update weather for next prediction
            # (we're using the predicted temperature for the next round)
            weather['temp'] = next_temp
        
        # Create prediction results
        results = {
            'city': city,
            'country': country,
            'model': self.model_info.get('model_name', 'unknown'),
            'dates': dates,
            'temperatures': predictions
        }
        
        return results
    
    def get_model_info(self):
        """Get information about the model."""
        return self.model_info

def sample_prediction():
    """Run a sample prediction."""
    try:
        predictor = WeatherPredictor()
        
        # Sample current weather data
        current_weather = {
            'temp': 20.5,
            'feels_like': 21.0,
            'humidity': 65,
            'pressure': 1012,
            'wind_speed': 5.2,
            'clouds': 40,
            'weather_main': 'Clouds'
        }
        
        # Make prediction
        prediction = predictor.predict_next_days('London', 'uk', current_weather, days=5)
        
        print("Weather prediction results:")
        print(f"City: {prediction['city']}, Country: {prediction['country']}")
        print(f"Model used: {prediction['model']}")
        
        for date, temp in zip(prediction['dates'], prediction['temperatures']):
            print(f"Date: {date}, Temperature: {temp:.1f}°C")
        
    except FileNotFoundError:
        print("Model file not found. Please train the model first.")
    except Exception as e:
        print(f"Error making prediction: {str(e)}")

if __name__ == "__main__":
    sample_prediction()