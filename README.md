# nimbus-predict
Nimbus-Predict is a hello-world project. It is a cloud-native end-to-end weather forecasting pipeline built with API data ingestion, PySpark ETL, machine learning, and Docker deployment on GCP.

# Weather Pipeline Project Documentation

## Project Overview

**Goal:**  
Build an end-to-end cloud-based pipeline that:
- Uses the OpenWeatherMap API to fetch weather data for a given location.
- Cleans and preprocesses the data using an ETL process with PySpark.
- Trains a simple machine learning model to predict future weather (e.g., predicting temperature based on humidity).
- Provides an API/dashboard that takes a location input and returns a prediction.
- Is containerized with Docker and deployed on Google Cloud Platform (GCP) using Cloud Run.
- Implements CI/CD and unit testing with GitHub Actions.
- Showcases the project on a live website.

**Stack & Technologies:**
- **Programming Language:** Python
- **Data Ingestion:** OpenWeatherMap API
- **ETL:** PySpark
- **Modeling:** scikit-learn (LinearRegression) and joblib for model persistence
- **Dashboard:** Streamlit
- **Containerization:** Docker
- **Deployment:** GCP Cloud Run (using free tier where possible)
- **CI/CD:** GitHub Actions
- **Testing:** Pytest for unit tests

---

## Directory Structure

```plaintext
/weather-pipeline
├── data/                
│   ├── raw_data.json         # Raw weather JSON fetched from OpenWeatherMap API
│   └── cleaned_data.csv      # Processed data from the ETL pipeline
├── model/
│   └── model.pkl             # Saved ML model
├── src/
│   ├── data_ingest.py        # Script to fetch weather data using OpenWeatherMap API
│   ├── etl_spark.py          # PySpark ETL script to clean and preprocess raw data
│   ├── train_model.py        # Script to train an ML model on the cleaned data
│   ├── predict.py            # Script to load the model and perform inference
│   └── app.py                # Streamlit dashboard for user input and prediction display
├── docker/
│   └── Dockerfile            # Dockerfile for containerizing the application
├── tests/
│   ├── test_data_ingest.py   # Unit tests for data ingestion
│   └── test_train_model.py   # Unit tests for model training and prediction
├── .github/
│   └── workflows/
│       └── main.yml          # GitHub Actions CI/CD workflow file
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation and instructions
