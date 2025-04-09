import os
import pandas as pd
import numpy as np
from pyspark.sql import SparkSession
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

class WeatherModelTrainer:
    """Class to train weather prediction models."""
    
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("WeatherModelTraining") \
            .config("spark.driver.memory", "2g") \
            .master("local[*]") \
            .getOrCreate()
        
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
    
    def load_data(self, data_path="data/processed/weather_data.parquet"):
        """Load processed weather data."""
        # Check if file exists
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        # Load data from parquet file using Spark
        spark_df = self.spark.read.parquet(data_path)
        
        # Convert to pandas for scikit-learn compatibility
        df = spark_df.toPandas()
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for model training."""
        # Drop any rows with missing values
        df = df.dropna()
        
        # Define features and target
        # Target: temperature for the next day
        # We'll simulate this by grouping by city and shifting the temperature
        df = df.sort_values(by=['city', 'timestamp'])
        df['next_day_temp'] = df.groupby('city')['temp'].shift(-1)
        df = df.dropna()  # Drop rows without next day temp
        
        # Split data into training (current and historical) and testing (forecast)
        train_df = df[(df['data_type'] == 'current') | (df['data_type'] == 'historical')]
        test_df = df[df['data_type'] == 'forecast']
        
        # Define features
        feature_cols = [
            'temp', 'feels_like', 'humidity', 'pressure', 
            'wind_speed', 'clouds', 'hour', 'day', 'month'
        ]
        
        # Categorical features
        cat_cols = ['weather_main', 'city', 'country']
        
        # Target
        target_col = 'next_day_temp'
        
        # Split features and target
        X_train = train_df[feature_cols + cat_cols]
        y_train = train_df[target_col]
        X_test = test_df[feature_cols + cat_cols]
        y_test = test_df[target_col]
        
        return X_train, X_test, y_train, y_test, feature_cols, cat_cols
    
    def build_model_pipeline(self, feature_cols, cat_cols):
        """Build scikit-learn pipeline with preprocessing and model."""
        # Define preprocessing steps
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        # Combine preprocessing steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, feature_cols),
                ('cat', categorical_transformer, cat_cols)
            ]
        )
        
        # Create pipelines for different models
        rf_pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', RandomForestRegressor(random_state=42))
        ])
        
        gb_pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', GradientBoostingRegressor(random_state=42))
        ])
        
        lr_pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', LinearRegression())
        ])
        
        return { # only linear regression for now
            # 'random_forest': rf_pipeline,
            # 'gradient_boosting': gb_pipeline,
            'linear_regression': lr_pipeline
        }
    
    def train_and_evaluate(self, pipelines, X_train, X_test, y_train, y_test):
        """Train models and evaluate their performance."""
        results = {}
        
        for name, pipeline in pipelines.items():
            print(f"Training {name} model...")
            
            # Define parameter grid for grid search
            if name == 'random_forest':
                param_grid = {
                    'model__n_estimators': [50, 100],
                    'model__max_depth': [None, 10, 20]
                }
            elif name == 'gradient_boosting':
                param_grid = {
                    'model__n_estimators': [50, 100],
                    'model__learning_rate': [0.01, 0.1]
                }
            else:  # linear regression
                param_grid = {}
            
            # Use grid search if param_grid is not empty
            if param_grid:
                grid_search = GridSearchCV(
                    pipeline, param_grid, cv=3, n_jobs=-1, 
                    scoring='neg_mean_squared_error'
                )
                grid_search.fit(X_train, y_train)
                pipeline = grid_search.best_estimator_
                best_params = grid_search.best_params_
            else:
                pipeline.fit(X_train, y_train)
                best_params = {}
            
            # Make predictions
            y_pred = pipeline.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Store results
            results[name] = {
                'pipeline': pipeline,
                'best_params': best_params,
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            }
            
            print(f"{name} - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")
        
        return results
    
    def save_best_model(self, results):
        """Save the best performing model."""
        # Find best model based on RMSE
        best_model_name = min(results, key=lambda x: results[x]['rmse'])
        best_model = results[best_model_name]['pipeline']
        
        # Save the model
        model_path = "models/weather_prediction_model.joblib"
        joblib.dump(best_model, model_path)
        
        # Save model info
        model_info = {
            'model_name': best_model_name,
            'metrics': {
                'rmse': results[best_model_name]['rmse'],
                'mae': results[best_model_name]['mae'],
                'r2': results[best_model_name]['r2']
            },
            'best_params': results[best_model_name]['best_params']
        }
        
        # Save model info as JSON
        import json
        with open("models/model_info.json", "w") as f:
            json.dump(model_info, f, indent=4)
        
        print(f"Best model ({best_model_name}) saved to {model_path}")
        return model_path, model_info
    
    def train_model(self):
        """Train weather prediction model."""
        # Load data
        print("Loading data...")
        df = self.load_data()
        
        # Prepare features
        print("Preparing features...")
        X_train, X_test, y_train, y_test, feature_cols, cat_cols = self.prepare_features(df)
        
        # Build model pipelines
        print("Building model pipelines...")
        pipelines = self.build_model_pipeline(feature_cols, cat_cols)
        
        # Train and evaluate models
        print("Training and evaluating models...")
        results = self.train_and_evaluate(pipelines, X_train, X_test, y_train, y_test)
        
        # Save best model
        print("Saving best model...")
        model_path, model_info = self.save_best_model(results)
        
        return model_path, model_info

if __name__ == "__main__":
    trainer = WeatherModelTrainer()
    trainer.train_model()