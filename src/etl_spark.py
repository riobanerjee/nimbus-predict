# src/etl_spark.py
from pyspark.sql import SparkSession

def create_spark_session():
    """
    Creates a Spark session for processing data.
    This function initializes a Spark session with the application name "Weather ETL".
    It is used to read and process data in a distributed manner.
    Returns:
        SparkSession: A Spark session object.
    """
    spark = SparkSession.builder \
        .appName("Weather ETL") \
        .getOrCreate()
    return spark

def process_raw_data(spark, input_path, output_path):
    """
    Processes raw JSON weather data and extracts specific fields for cleaning and saving.

    Args:
        spark (pyspark.sql.SparkSession): The Spark session used for reading and processing data.
        input_path (str): The file path to the input JSON data.
        output_path (str): The file path where the cleaned CSV data will be saved.

    Returns:
        None

    This function reads raw weather data in JSON format from the specified input path,
    extracts the "temp", "humidity", and "pressure" fields from the "current" section,
    and writes the cleaned data to a single CSV file at the specified output path.
    The output CSV file includes a header and overwrites any existing file at the location.
    """
    df = spark.read.json(input_path)
    # Example transformation: select current weather info
    cleaned_df = df.select("current.temp", "current.humidity", "current.pressure")
    cleaned_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)
    print(f"Cleaned data saved to {output_path}")

if __name__ == "__main__":
    spark = create_spark_session()
    input_path = "../data/raw_data.json"
    output_path = "../data/cleaned_data.csv"
    process_raw_data(spark, input_path, output_path)
    spark.stop()
