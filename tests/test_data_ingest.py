# tests/test_data_ingest.py
import unittest
from src.data_ingest import fetch_weather

class TestDataIngest(unittest.TestCase):
    """
    TestDataIngest is a test case class for testing the data ingestion functionality.

    Methods:
        test_fetch_weather_failure():
            Tests the behavior of the fetch_weather function when provided with an invalid lat, long.
            Ensures that an exception is raised in such cases.
    """
    def test_fetch_weather_failure(self):
        # Since an invalid latlong  should raise an exception
        with self.assertRaises(Exception):
            fetch_weather("inf", "inf")

if __name__ == "__main__":
    unittest.main()
