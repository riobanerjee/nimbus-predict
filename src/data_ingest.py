# src/data_ingest.py
import requests
import json
import sys

def fetch_weather(api_key, lat, lon):
    """
    Fetch weather data from the OpenWeatherMap API for a given location.

    This function retrieves weather data using the One Call API from OpenWeatherMap.
    It excludes minutely, hourly, and alert data, and returns the response in metric units.

    Args:
        api_key (str): Your API key for accessing the OpenWeatherMap API.
        lat (float): The latitude of the location for which to fetch weather data.
        lon (float): The longitude of the location for which to fetch weather data.

    Returns:
        dict: A dictionary containing the weather data returned by the API.

    Raises:
        Exception: If the API request fails, an exception is raised with the HTTP status code.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/onecall"
        f"?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&appid={api_key}&units=metric"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python data_ingest.py <API_KEY> <LAT> <LON>")
        sys.exit(1)
    api_key = sys.argv[1]
    lat = sys.argv[2]
    lon = sys.argv[3]
    data = fetch_weather(api_key, lat, lon)
    with open("../data/raw_data.json", "w") as outfile:
        json.dump(data, outfile, indent=4)
    print("Raw data saved to ../data/raw_data.json")
