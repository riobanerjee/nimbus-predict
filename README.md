# Weather Forecaster 🌤️

A machine learning-powered weather forecasting application that fetches real-time weather data, processes it using PySpark, trains a prediction model, and displays the results on an interactive dashboard.

## Hosted Application

The Weather Forecaster application is hosted on Streamlit Cloud. You can access it at:

[https://nimbus-predict.streamlit.app](https://nimbus-predict.streamlit.app)

## Project Overview

This project implements a complete data pipeline and web application for weather forecasting:

1. **Data Collection**: Fetch weather data from OpenWeatherMap API
2. **Data Processing**: Clean and transform data using PySpark
3. **Machine Learning**: Train models to predict future weather
4. **Visualization**: Display results on an interactive Streamlit dashboard
5. **Deployment**: Host the application on Google Cloud Platform

## Setup Instructions

### Prerequisites

- Python 3.9+
- Git
- Google Cloud Platform account (for deployment)
- OpenWeatherMap API key

### Local Development Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/weather-forecaster.git
cd weather-forecaster
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root with your OpenWeatherMap API key:

```
OPENWEATHER_API_KEY=your_api_key_here
```

### Running the Application

1. **Collect Weather Data**

```bash
python -m src.data.collect
```

2. **Process Data with PySpark**

```bash
python -m src.data.process
```

3. **Train Weather Prediction Model**

```bash
python -m src.models.train
```

4. **Run the Streamlit Dashboard**

```bash
streamlit run app.py
```


## Project Structure

- `src/data/`: Data collection and processing scripts
- `src/models/`: Machine learning model training and prediction
- `src/visualization/`: Dashboard and visualization components
- `tests/`: Unit tests for the application
- `notebooks/`: Jupyter notebooks for exploratory analysis
- `data/`: Raw and processed data storage
- `models/`: Trained model storage
- `.github/workflows/`: CI/CD configuration

## Deployment to GCP

TODO:
This project will be set up for automatic deployment to Google Cloud Platform App Engine using GitHub Actions.

Using GCP Cloud Run from the Console.
<!-- 
1. **Set up Google Cloud SDK locally**

```bash
gcloud init
gcloud auth application-default login
```

2. **Create a service account and download key**

Go to GCP Console > IAM & Admin > Service Accounts and create a new service account with App Engine Admin and Storage Admin roles. Download the key as JSON.

3. **Add GitHub Secrets**

In your GitHub repository, go to Settings > Secrets and add:
- `GCP_SA_KEY`: The content of your service account key JSON file
- `GCP_PROJECT_ID`: Your Google Cloud project ID

4. **Manual Deployment**

```bash
gcloud app deploy app.yaml
``` -->

## Testing

Run the test suite with:

```bash
pytest tests/
```

For test coverage report:

```bash
pytest --cov=src tests/
```

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.