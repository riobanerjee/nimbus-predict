# src/data_ingest.py
import requests
import json
import sys
import os

def fetch_api_key():
    """
    Fetches the OpenWeatherMap API key from an environment variable.

    This function retrieves the API key from the environment variable 'OPENWEATHER_API_KEY'.
    If the environment variable is not set, it raises an exception.

    Returns:
        str: The OpenWeatherMap API key.

    Raises:
        Exception: If the API key is not found in the environment variables.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise Exception("API key not found. Please set the WEATHER_API_KEY environment variable.")
    return api_key


def fetch_weather(lat, lon):
    """
    Fetch weather data from the OpenWeatherMap API for a given location.

    This function retrieves weather data using the One Call API from OpenWeatherMap.
    It excludes minutely, hourly, and alert data, and returns the response in metric units.

    Args:
        lat (float): The latitude of the location for which to fetch weather data.
        lon (float): The longitude of the location for which to fetch weather data.

    Returns:
        dict: A dictionary containing the weather data returned by the API.

    Raises:
        Exception: If the API request fails, an exception is raised with the HTTP status code.
    """
    try:
        api_key = fetch_api_key()
    except Exception as e:
        raise Exception(f"Error fetching API key: {e}")
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python data_ingest.py <LAT> <LON>")
        sys.exit(1)
    lat = sys.argv[1]
    lon = sys.argv[2]
    data = fetch_weather(lat, lon)
    with open("../data/raw_data.json", "w") as outfile:
        json.dump(data, outfile, indent=4)
    print("Raw data saved to ../data/raw_data.json")
