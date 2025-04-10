import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import HeatMap
from branca.colormap import linear
import sys
import os
import branca.colormap as cm
import time
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data.collect import WeatherDataCollector
from src.data.collect import AirPollutionGridCollector
from src.models.predict import WeatherPredictor

class WeatherDashboard:
    """Streamlit dashboard for weather predictions."""
    
    def __init__(self):
        """Initialize the dashboard components."""
        self.weather_collector = WeatherDataCollector()
        self.pollution_collector = AirPollutionGridCollector()

        
        try:
            self.predictor = WeatherPredictor()
            self.model_loaded = True
        except FileNotFoundError:
            self.model_loaded = False
    
    def setup_page(self):
        """Set up Streamlit page configuration."""
        st.set_page_config(
            page_title="Weather & Air Quality",
            page_icon="🌤️",
            layout="wide"
        )
        
        st.title("🌤️ Weather & Air Pollution Dashboard")
        st.subheader("Weather and air pollution visualization")
        
        if not self.model_loaded:
            st.error("⚠️ Model not loaded. Please train the model first.")
            st.stop()
    
    def location_input(self):
        """Create location input form."""
        st.sidebar.header("📍 Location")
        
        # Add sample locations for quick selection
        sample_locations = [
            "London, UK",
            "Kolkata, IN",
            "New York, US",
            "Tokyo, JP",
            "Sydney, AU",
        ]
        
        selected_location = st.sidebar.selectbox(
            "Select a location:", 
            sample_locations
        )
        
        if selected_location == "Enter Location":
            col1, col2 = st.sidebar.columns(2)
            city = col1.text_input("City:", "London")
            country = col2.text_input("Country Code:", "uk")
        else:
            city, country = selected_location.split(", ")
            
        return city, country
    
    def get_weather_data(self, city, country):
        """Get current weather data for selected location."""
        with st.spinner("Fetching current weather data..."):
            current_weather_data = self.weather_collector.get_current_weather(city, country)
            forecast_weather_data = self.weather_collector.get_forecast(city, country)
            
        if current_weather_data is None:
            st.error(f"Failed to get weather data for {city}, {country}")
            st.stop()
            
        # Extract required data
        weather = {
            'temp': current_weather_data['main']['temp'],
            'feels_like': current_weather_data['main']['feels_like'],
            'humidity': current_weather_data['main']['humidity'],
            'pressure': current_weather_data['main']['pressure'],
            'wind_speed': current_weather_data['wind']['speed'],
            'clouds': current_weather_data['clouds']['all'],
            'weather_main': current_weather_data['weather'][0]['main'],
            'weather_description': current_weather_data['weather'][0]['description'],
            'lat': current_weather_data['coord']['lat'],
            'lon': current_weather_data['coord']['lon']
        }
        
        return weather, current_weather_data, forecast_weather_data
    
    def get_pollution_data(self, lat, lon):
        """Get current air pollution data for coordinates."""
        with st.spinner("Fetching air pollution data..."):
            data_old = self.pollution_collector.get_current_pollution(lat, lon)
            
        if data_old is None:
            st.warning(f"Failed to get air pollution data for coordinates: {lat}, {lon}")
            return None
        data = data_old['list'][0]
            
        pollution = {
            'data_type': 'pollution',
            # 'timestamp': pd.to_datetime(data['dt'], unit='s'),
            'aqi': data['main']['aqi'],
            'pm10': data['components'].get('pm10', 0),
            'pm2_5': data['components'].get('pm2_5', 0),
            'no2': data['components'].get('no2', 0),
            'o3': data['components'].get('o3', 0),
            'co': data['components'].get('co', 0),
        }
        return pollution
    
    def display_current_weather(self, weather, pollution):
        """Display current weather information."""
        st.header("Current Weather")
        
        col1, col2, col3 = st.columns(3)
        
        # Current temperature
        col1.metric(
            label = "Temperature",
            value = f"{weather['temp']:.1f}°C",
            delta = f"{weather['temp'] - weather['feels_like']:.1f}°C",
        )
        
        # Weather condition
        col2.metric(
            "Condition", 
            f"{weather['weather_main']}", 
            f"{weather['weather_description']}",
            delta_color="off"
        )
        
        # Humidity
        col3.metric(
            "Humidity", 
            f"{weather['humidity']}%", 
            ""
        )

        lat, lon = weather['lat'], weather['lon']
        # Create map centered at location
        m = folium.Map(location=[lat, lon], zoom_start=10)
        
        # Define colors for AQI levels
        aqi_colors = {
            1: "green",
            2: "lightgreen",
            3: "yellow",
            4: "orange",
            5: "red"
        }
        
        aqi_descriptions = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        
        # Get AQI and color
        aqi = pollution["aqi"]
        color = aqi_colors.get(aqi, "gray")
        description = aqi_descriptions.get(aqi, "Unknown")
        
        # Create a circle marker with AQI information
        folium.CircleMarker(
            location=[lat, lon],
            radius=30,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            tooltip=folium.Tooltip(f"""
            <b>AQI:</b> {aqi} - {description}<br>
            <b>PM10:</b> {pollution['pm10']:.1f} μg/m³<br>
            <b>CO:</b> {pollution['co']:.1f} μg/m³<br>
            """, sticky=True)
        ).add_to(m)
        
        # Add a regular marker for the location
        location_name = weather.get('location_name', 'Location')
        folium.Marker(
            [lat, lon],
            popup=location_name,
            tooltip=folium.Tooltip(location_name),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
        # Add colormap legend for AQI
        colormap = cm.LinearColormap(
            ['green', 'lightgreen', 'yellow', 'orange', 'red'],
            vmin=1, vmax=5,
            caption='Air Quality Index (AQI)'
        )
        colormap.add_to(m)
        
        # Display map
        folium_static(m)
        
        # Add a note about AQI
        st.info("""
        **Air Quality Index (AQI) Scale:**
        - 1 (Green): Good - Little or no risk
        - 2 (Light Green): Fair - Acceptable quality
        - 3 (Yellow): Moderate - May be a concern for sensitive people
        - 4 (Orange): Poor - May cause effects for general population
        - 5 (Red): Very Poor - Health warnings of emergency conditions
        """)
        
        # # Display map
        # st.subheader("Location")
        # m = folium.Map(
        #     location=[weather['lat'], weather['lon']], 
        #     zoom_start=10
        # )
        
        # folium.Marker(
        #     [weather['lat'], weather['lon']],
        #     popup=f"{raw_data['name']}, {raw_data['sys']['country']}",
        #     tooltip=f"{raw_data['name']}",
        #     icon=folium.Icon(color="blue", icon="cloud")
        # ).add_to(m)
        
        # folium_static(m)
    

    def make_prediction(self, city, country, weather):
        """Make weather predictions for the location."""
        with st.spinner("Making predictions..."):
            prediction = self.predictor.predict_next_days(city, country, weather, days=5)
            
        return prediction
    
    def display_prediction(self, prediction, forecast):
        """Display weather prediction results."""
        st.header("Weather Forecast")

        n_days = len(prediction['dates'])
        forecast_temps = []
        for i in range(n_days):
            forecast_temps.append(forecast['list'][i]['main']['temp'])
        
        # Create prediction dataframe
        df = pd.DataFrame({
            'Date': prediction['dates'],
            'Temperature': prediction['temperatures'],
            'Forecast OWM': forecast_temps
        })
        
        # Display prediction as a table
        st.subheader("Predicted Temperatures")
        st.table(df)
        
        # Plot prediction
        fig = px.line(
            df, 
            x='Date', 
            y=['Temperature', 'Forecast OWM'],
            markers=True,
            title=f"Temperature Forecast for {prediction['city']}, {prediction['country']}"
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            yaxis=dict(range=[min(prediction['temperatures'])-5, max(prediction['temperatures'])+5])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display model info
        st.subheader("Model Information")
        st.write(f"Model used: {prediction['model']}")
    
    def run(self):
        """Run the dashboard application."""
        # Setup page
        self.setup_page()
        
        # Get location input
        city, country = self.location_input()

        
        # Select pollutant to display
        # pollutant_options = {
        #     'Air Quality Index': 'aqi',
        #     'PM10': 'pm10',
        #     'Carbon Monoxide (CO)': 'co',
        # }
        
        # selected_pollutant_name = st.sidebar.selectbox(
        #     "Select Pollutant to Display:",
        #     list(pollutant_options.keys()),
        #     index=0
        # )
        
        # selected_pollutant = pollutant_options[selected_pollutant_name]
        
        # Submit button
        if st.sidebar.button("Get Weather Forecast"):
            try:
                # Get current weather
                weather, raw_data, forecast_data = self.get_weather_data(city, country)
                pollution = self.get_pollution_data(weather['lat'], weather['lon'])
                
                # Get the location name
                location_name = f"{raw_data['name']}, {raw_data['sys']['country']}"
                
                weather['location_name'] = location_name
                # pollution['selected_pollutant'] = selected_pollutant
                # Display current weather
                self.display_current_weather(weather, pollution)
                
                # Make prediction
                prediction = self.make_prediction(city, country, weather)
                
                # Display prediction    
                self.display_prediction(prediction, forecast_data)

                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        
        # Additional dashboard features
        st.sidebar.subheader("About")
        st.sidebar.info(
            "This application fetches current weather data and "
            "predicts future temperatures using a machine learning model. "
            "It also visualizes air pollution data on a map. "
            "The data is collected from OpenWeatherMap API."
        )

if __name__ == "__main__":
    dashboard = WeatherDashboard()
    dashboard.run()