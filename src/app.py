# src/app.py
"""
This module defines a Streamlit-based web application for weather prediction.

The application allows users to input a humidity value and predicts the corresponding temperature
using a pre-trained machine learning model. It demonstrates an end-to-end pipeline from data ingestion
to prediction.

Functions:
    - load_model: Loads the pre-trained model from a specified file path.
    - predict: Uses the loaded model to make predictions based on the input humidity value.

Streamlit Components:
    - st.title: Displays the title of the application.
    - st.write: Displays descriptive text and additional information.
    - st.number_input: Accepts user input for humidity as a numeric value.
    - st.button: Triggers the prediction process when clicked.
    - st.success: Displays the predicted temperature on successful prediction.
    - st.error: Displays an error message if an exception occurs during prediction.

Usage:
    Run this script in a Streamlit environment to launch the web application.
    Ensure the model file is available at the specified path before running the application.
"""
import streamlit as st
from predict import load_model, predict

st.title("Weather Prediction Dashboard")
st.write("Enter the humidity value to predict the temperature (example model).")

humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.1)

if st.button("Predict Temperature"):
    try:
        model = load_model("../model/model.pkl")
        prediction = predict(model, humidity)
        st.success(f"Predicted Temperature: {prediction:.2f}°C")
    except Exception as e:
        st.error(f"Error: {e}")

st.write("This is a demo application showing an end-to-end pipeline from data ingestion to prediction.")
