import os
import sys
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.predict import WeatherPredictor

class TestWeatherPredictor:
    """Test cases for WeatherPredictor class."""
    
    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.os.path.exists')
    def test_init(self, mock_exists, mock_load):
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock model
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        
        # Initialize predictor
        predictor = WeatherPredictor()
        
        # Check initialization
        assert predictor.model == mock_model
        mock_exists.assert_called_once_with("models/weather_prediction_model.joblib")
        mock_load.assert_called_once_with("models/weather_prediction_model.joblib")
    
    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.os.path.exists')
    def test_prepare_input_data(self, mock_exists, mock_load):
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock model
        mock_model = MagicMock()
        mock_load.return_value = mock_model
        
        # Initialize predictor
        predictor = WeatherPredictor()
        
        # Test data
        city = "London"
        country = "uk"
        current_weather = {
            'temp': 20.5,
            'feels_like': 21.0,
            'humidity': 65,
            'pressure': 1012,
            'wind_speed': 5.2,
            'clouds': 40,
            'weather_main': 'Clouds'
        }
        
        # Call method
        result = predictor.prepare_input_data(city, country, current_weather)
        
        # Check result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result['city'].iloc[0] == city
        assert result['country'].iloc[0] == country
        assert result['temp'].iloc[0] == current_weather['temp']
        assert result['humidity'].iloc[0] == current_weather['humidity']
    
    @patch('src.models.predict.joblib.load')
    @patch('src.models.predict.os.path.exists')
    def test_predict_next_day(self, mock_exists, mock_load):
        # Mock file existence
        mock_exists.return_value = True
        
        # Mock model with predict method
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([21.5])
        mock_load.return_value = mock_model
        
        # Initialize predictor
        predictor = WeatherPredictor()
        
        # Test data
        city = "London"
        country = "uk"
        current_weather = {
            'temp': 20.5,
            'feels_like': 21.0,
            'humidity': 65,
            'pressure': 1012,
            'wind_speed': 5.2,
            'clouds': 40,
            'weather_main': 'Clouds'
        }
        
        # Call method
        result = predictor.predict_next_day(city, country, current_weather)
        
        # Check result
        assert result == 21.5
        mock_model.predict.assert_called_once()