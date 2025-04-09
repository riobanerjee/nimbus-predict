import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data.collect import WeatherDataCollector
from src.models.predict import WeatherPredictor

class WeatherDashboard:
    """Streamlit dashboard for weather predictions."""
    
    def __init__(self):
        """Initialize the dashboard components."""
        self.collector = WeatherDataCollector()
        
        try:
            self.predictor = WeatherPredictor()
            self.model_loaded = True
        except FileNotFoundError:
            self.model_loaded = False
    
    def setup_page(self):
        """Set up Streamlit page configuration."""
        st.set_page_config(
            page_title="Weather Forecaster",
            page_icon="🌤️",
            layout="wide"
        )
        
        st.title("🌤️ Weather Forecaster")
        st.subheader("Predict weather for any location")
        
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
            current_weather_data = self.collector.get_current_weather(city, country)
            forecast_weather_data = self.collector.get_forecast(city, country)
            
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
    
    def display_current_weather(self, weather, raw_data):
        """Display current weather information."""
        st.header("Current Weather")
        
        col1, col2, col3 = st.columns(3)
        
        # Current temperature
        col1.metric(
            "Temperature", 
            f"{weather['temp']:.1f}°C", 
            f"Feels like: {weather['feels_like']:.1f}°C"
        )
        
        # Weather condition
        col2.metric(
            "Condition", 
            f"{weather['weather_main']}", 
            f"{weather['weather_description']}"
        )
        
        # Humidity
        col3.metric(
            "Humidity", 
            f"{weather['humidity']}%", 
            ""
        )
        
        # Display map
        st.subheader("Location")
        m = folium.Map(
            location=[weather['lat'], weather['lon']], 
            zoom_start=10
        )
        
        folium.Marker(
            [weather['lat'], weather['lon']],
            popup=f"{raw_data['name']}, {raw_data['sys']['country']}",
            tooltip=f"{raw_data['name']}",
            icon=folium.Icon(color="blue", icon="cloud")
        ).add_to(m)
        
        folium_static(m)
    
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
        
        # Submit button
        if st.sidebar.button("Get Weather Forecast"):
            try:
                # Get current weather
                weather, raw_data, forecast_data = self.get_weather_data(city, country)
                
                # Display current weather
                self.display_current_weather(weather, raw_data)
                
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
            "predicts future temperatures using a machine learning model."
        )

if __name__ == "__main__":
    dashboard = WeatherDashboard()
    dashboard.run()