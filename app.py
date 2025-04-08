import os
import sys
import streamlit as st

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the dashboard
from src.visualization.dashboard import WeatherDashboard

# Run the dashboard
if __name__ == "__main__":
    dashboard = WeatherDashboard()
    dashboard.run()