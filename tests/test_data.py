import os
import sys
import pytest
import json
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.collect import WeatherDataCollector

class TestWeatherDataCollector:
    """Test cases for WeatherDataCollector class."""
    
    @patch('src.data.collect.requests.get')
    @patch('src.data.collect.os.getenv')
    def test_get_current_weather(self, mock_getenv, mock_get):
        # Mock API key
        mock_getenv.return_value = "fake_api_key"
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "coord": {"lon": -0.1257, "lat": 51.5085},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "main": {
                "temp": 20.5,
                "feels_like": 21.0,
                "temp_min": 19.5,
                "temp_max": 21.5,
                "pressure": 1012,
                "humidity": 65
            },
            "wind": {"speed": 3.1, "deg": 280},
            "clouds": {"all": 0},
            "dt": 1618317040,
            "sys": {"country": "GB", "sunrise": 1618287440, "sunset": 1618337745},
            "timezone": 3600,
            "id": 2643743,
            "name": "London",
        }
        mock_get.return_value = mock_response
        
        # Initialize collector
        collector = WeatherDataCollector()
        
        # Call method
        result = collector.get_current_weather("London", "GB")
        
        # Check result
        assert result is not None
        assert result["name"] == "London"
        assert result["sys"]["country"] == "GB"
        assert result["main"]["temp"] == 20.5
        
        # Check API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "weather" in args[0]
        assert kwargs["params"]["q"] == "London,GB"
        assert kwargs["params"]["appid"] == "fake_api_key"
    
    @patch('src.data.collect.requests.get')
    @patch('src.data.collect.os.getenv')
    def test_get_forecast(self, mock_getenv, mock_get):
        # Mock API key
        mock_getenv.return_value = "fake_api_key"
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "city": {
                "id": 2643743,
                "name": "London",
                "coord": {"lon": -0.1257, "lat": 51.5085},
                "country": "GB",
                "timezone": 3600
            },
            "list": [
                {
                    "dt": 1618326000,
                    "main": {
                        "temp": 19.5,
                        "feels_like": 19.0,
                        "temp_min": 18.5,
                        "temp_max": 20.5,
                        "pressure": 1010,
                        "humidity": 70
                    },
                    "weather": [{"main": "Clouds", "description": "scattered clouds"}],
                    "clouds": {"all": 40},
                    "wind": {"speed": 2.5, "deg": 270},
                    "dt_txt": "2021-04-13 18:00:00"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Initialize collector
        collector = WeatherDataCollector()
        
        # Call method
        result = collector.get_forecast("London", "GB")
        
        # Check result
        assert result is not None
        assert result["city"]["name"] == "London"
        assert result["city"]["country"] == "GB"
        assert len(result["list"]) == 1
        assert result["list"][0]["main"]["temp"] == 19.5
        
        # Check API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "forecast" in args[0]
        assert kwargs["params"]["q"] == "London,GB"
        assert kwargs["params"]["appid"] == "fake_api_key"
    
    @patch('src.data.collect.json.dump')
    @patch('builtins.open')
    @patch('src.data.collect.os.makedirs')
    def test_save_data(self, mock_makedirs, mock_open, mock_dump):
        # Mock API key
        os.environ["WEATHER_API_KEY"] = "fake_api_key"
        
        # Mock data
        data = {"name": "London", "main": {"temp": 20.5}}
        filename = "test.json"
        
        # Initialize collector
        collector = WeatherDataCollector()
        
        # Call method
        collector.save_data(data, filename)
        
        # Check method calls
        mock_makedirs.assert_called_once_with("data/raw", exist_ok=True)
        mock_open.assert_called_once()
        mock_dump.assert_called_once_with(data, mock_open().__enter__())