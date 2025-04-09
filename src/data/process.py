import os
import json
import glob
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, from_unixtime, hour, dayofmonth, month, year
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, ArrayType

class WeatherDataProcessor:
    """Class to process weather data using PySpark."""
    
    def __init__(self):
        # Initialize Spark session
        self.spark = SparkSession.builder \
            .appName("WeatherDataProcessing") \
            .config("spark.driver.memory", "2g") \
            .master("local[*]") \
            .getOrCreate()
    
    def read_json_files(self, directory):
        """Read all JSON files from a directory into a DataFrame."""
        json_files = glob.glob(f"{directory}/*.json")
        
        # Create an empty list to store individual dataframes
        dataframes = []
        
        for file_path in json_files:
            # Extract city and data type from filename
            filename = os.path.basename(file_path)
            parts = filename.split("_")
            city = parts[0]
            country = parts[1]
            data_type = parts[2]
            
            # Read JSON file into DataFrame
            if "current" in data_type:
                df = self._process_current_weather(file_path, city, country)
            elif "forecast" in data_type:
                df = self._process_forecast(file_path, city, country)
            elif "historical" in data_type:
                df = self._process_historical(file_path, city, country)
            elif "pollution" in data_type:
                df = self._process_pollution(file_path, city, country)
            else:
                continue
                
            if df is not None:
                dataframes.append(df)
        
        # Combine all dataframes
        if dataframes:
            return self.spark.createDataFrame(pd.concat(dataframes))
        return None
    
    def _process_current_weather(self, file_path, city, country):
        """Process current weather data."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not data:
            return None
            
        # Extract relevant fields
        row = {
            'city': city,
            'country': country,
            'data_type': 'current',
            'timestamp': pd.to_datetime(data['dt'], unit='s'),
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'temp_min': data['main']['temp_min'],
            'temp_max': data['main']['temp_max'],
            'pressure': data['main']['pressure'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'wind_deg': data['wind'].get('deg', 0),
            'clouds': data['clouds']['all'],
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
        }
        
        # Create DataFrame
        return pd.DataFrame([row])
    
    def _process_forecast(self, file_path, city, country):
        """Process forecast weather data."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not data or 'list' not in data:
            return None
            
        rows = []
        for forecast in data['list']:
            row = {
                'city': city,
                'country': country,
                'data_type': 'forecast',
                'timestamp': pd.to_datetime(forecast['dt'], unit='s'),
                'temp': forecast['main']['temp'],
                'feels_like': forecast['main']['feels_like'],
                'temp_min': forecast['main']['temp_min'],
                'temp_max': forecast['main']['temp_max'],
                'pressure': forecast['main']['pressure'],
                'humidity': forecast['main']['humidity'],
                'wind_speed': forecast['wind']['speed'],
                'wind_deg': forecast['wind'].get('deg', 0),
                'clouds': forecast['clouds']['all'],
                'weather_main': forecast['weather'][0]['main'],
                'weather_description': forecast['weather'][0]['description'],
            }
            rows.append(row)
        
        # Create DataFrame
        return pd.DataFrame(rows)
    
    def _process_historical(self, file_path, city, country):
        """Process historical weather data."""
        with open(file_path, 'r') as f:
            data_list = json.load(f)
        
        if not data_list:
            return None
            
        rows = []
        for data_elem in data_list:
            if 'list' not in data_elem:
                continue
            
            data = data_elem['list'][0]
            row = {
                'city': city,
                'country': country,
                'data_type': 'historical',
                'timestamp': pd.to_datetime(data['dt'], unit='s'),
                'temp': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'temp_min': data['main']['temp_min'],
                'temp_max': data['main']['temp_max'],
                'pressure': data['main']['pressure'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind'].get('deg', 0),
                'clouds': data['clouds']['all'],
                'weather_main': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
            }
            rows.append(row)
        
        # Create DataFrame
        return pd.DataFrame(rows)
    
    def _process_pollution(self, file_path, city, country):
        """Process air pollution data."""
        with open(file_path, 'r') as f:
            data_old = json.load(f)
        
        if not data_old:
            return None
        data = data_old['list'][0]
        
        row = {
            'city': city,
            'country': country,
            'data_type': 'pollution',
            'timestamp': pd.to_datetime(data['dt'], unit='s'),
            'aqi': data['main']['aqi'],
            'pm10': data['components'].get('pm10', 0),
            'pm2_5': data['components'].get('pm2_5', 0),
            'no2': data['components'].get('no2', 0),
            'o3': data['components'].get('o3', 0),
            'co': data['components'].get('co', 0),
        }

        return pd.DataFrame([row])
        
    
    def feature_engineering(self, df):
        """Create additional features for ML model."""
        # Convert timestamp to Spark datetime
        df = df.withColumn("date", from_unixtime(col("timestamp").cast("long")))
        
        # Extract time-based features
        df = df.withColumn("hour", hour("date"))
        df = df.withColumn("day", dayofmonth("date"))
        df = df.withColumn("month", month("date"))
        df = df.withColumn("year", year("date"))
        
        # Calculate dew point (approximation)
        # df = df.withColumn("dew_point", 
        #                   col("temp") - ((100 - col("humidity")) / 5))
        
        # Weather category encoding (one-hot encoding would be done during ML prep)
        
        return df
    
    def save_processed_data(self, df, output_path="data/processed/weather_data.parquet"):
        """Save processed data to parquet format."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.write.mode("overwrite").parquet(output_path)
        print(f"Processed data saved to {output_path}")
    
    def process_all_data(self):
        """Process all raw data and save processed dataset."""
        # Read all JSON files
        df = self.read_json_files("data/raw")
        
        if df is None:
            print("No data found to process!")
            return
        
        # Perform feature engineering
        df = self.feature_engineering(df)
        
        # Save processed data
        self.save_processed_data(df)
        
        return df

if __name__ == "__main__":
    processor = WeatherDataProcessor()
    processor.process_all_data()