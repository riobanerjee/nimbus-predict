import os
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

load_dotenv()

class WeatherDataCollector:
    """Class to collect weather data from OpenWeatherMap API."""
    
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Set OPENWEATHER_API_KEY in .env file")
        self.base_url = "https://api.openweathermap.org/data/2.5/"
        self.history_url = "https://history.openweathermap.org/data/2.5/"
        
    def get_current_weather(self, city, country_code=None):
        """Get current weather for a city."""
        query = city
        if country_code:
            query = f"{city},{country_code}"
            
        params = {
            "q": query,
            "appid": self.api_key,
            "units": "metric"  # Celsius
        }
        
        response = requests.get(f"{self.base_url}weather", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data: {response.status_code}")
            return None
    
    def get_historical_weather(self, lat, lon, days_back=5):
        """Get actual historical weather data for coordinates using History API."""
        data_points = []
        current_time = datetime.now()
        
        for i in range(days_back):
            # Calculate timestamp for each day we want to get data for
            day_offset = timedelta(days=i)
            target_date = current_time - day_offset
            target_timestamp = int(target_date.timestamp())
            
            # Using the actual historical data API
            params = {
                "lat": lat,
                "lon": lon,
                "dt": target_timestamp,  # Timestamp for the target date
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(f"{self.history_url}history/city", params=params)
            
            if response.status_code == 200:
                data = response.json()
                data_points.append(data)
                print(f"Retrieved historical data for {target_date.strftime('%Y-%m-%d')}")
            else:
                print(f"Error fetching historical data: {response.status_code}")
                print(f"Response: {response.text}")
                
            # Respect API rate limits
            time.sleep(1)
        
        return data_points
    
    def get_forecast(self, city, country_code=None):
        """Get 5-day weather forecast for a city."""
        query = city
        if country_code:
            query = f"{city},{country_code}"
            
        params = {
            "q": query,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = requests.get(f"{self.base_url}forecast", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching forecast: {response.status_code}")
            return None
    
    def save_data(self, data, filename):
        """Save data to JSON file."""
        os.makedirs("data/raw", exist_ok=True)
        with open(f"data/raw/{filename}", "w") as f:
            json.dump(data, f)
        print(f"Data saved to data/raw/{filename}")

def collect_sample_data():
    """Collect sample data for multiple cities."""
    collector = WeatherDataCollector()
    
    # List of cities to collect data for
    cities = [
        ("London", "uk"),
        ("Kolkata", "in"),
        ("New York", "us"),
        ("Tokyo", "jp"),
        ("Sydney", "au")
    ]
    
    # Create data directory if it doesn't exist
    os.makedirs("data/raw", exist_ok=True)
    
    for city, country in cities:
        print(f"Collecting data for {city}, {country}...")
        
        # Get current weather
        current = collector.get_current_weather(city, country)
        if current:
            filename = f"{city.lower()}_{country.lower()}_current_{datetime.now().strftime('%Y%m%d')}.json"
            collector.save_data(current, filename)
        
        # Get forecast data
        forecast = collector.get_forecast(city, country)
        if forecast:
            filename = f"{city.lower()}_{country.lower()}_forecast_{datetime.now().strftime('%Y%m%d')}.json"
            collector.save_data(forecast, filename)
        
        # Get coordinates for historical data
        if current:
            lat = current["coord"]["lat"]
            lon = current["coord"]["lon"]
            
            # Get historical data
            historical = collector.get_historical_weather(lat, lon)
            if historical:
                filename = f"{city.lower()}_{country.lower()}_historical_{datetime.now().strftime('%Y%m%d')}.json"
                collector.save_data(historical, filename)

                
        # Respect API rate limits
        time.sleep(2)

if __name__ == "__main__":
    collect_sample_data()