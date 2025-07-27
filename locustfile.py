"""
Enhanced Load Testing Configuration for Iris Prediction API using Locust
Designed for testing scalability with 150-300 concurrent users
"""
from locust import HttpUser, task, between
import random
import json


class IrisPredictionAPIUser(HttpUser):
    """
    Locust user class for testing the Iris Prediction API with realistic traffic patterns.
    Simulates users making prediction requests with varying wait times.
    """
    
    # Simulate realistic user behavior with varying wait times
    wait_time = between(0.5, 2.0)  # 0.5-2 seconds between requests for high concurrency
    
    def on_start(self):
        """Called when a user starts - perform initial health check."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed with status {response.status_code}")
    
    def generate_iris_data(self):
        """Generate realistic Iris flower measurements for testing."""
        # Generate data based on real Iris dataset statistics
        iris_samples = [
            # Iris setosa samples
            {"sepal_length": round(random.uniform(4.3, 5.8), 1),
             "sepal_width": round(random.uniform(2.3, 4.4), 1),
             "petal_length": round(random.uniform(1.0, 1.9), 1),
             "petal_width": round(random.uniform(0.1, 0.6), 1)},
            
            # Iris versicolor samples  
            {"sepal_length": round(random.uniform(4.9, 7.0), 1),
             "sepal_width": round(random.uniform(2.0, 3.4), 1),
             "petal_length": round(random.uniform(3.0, 5.1), 1),
             "petal_width": round(random.uniform(1.0, 1.8), 1)},
            
            # Iris virginica samples
            {"sepal_length": round(random.uniform(4.9, 7.9), 1),
             "sepal_width": round(random.uniform(2.2, 3.8), 1),
             "petal_length": round(random.uniform(4.5, 6.9), 1),
             "petal_width": round(random.uniform(1.4, 2.5), 1)}
        ]
        return random.choice(iris_samples)
    
    @task(10)  # High weight for the main prediction endpoint
    def test_predict_endpoint(self):
        """Test the prediction endpoint with realistic data and performance monitoring."""
        sample_data = self.generate_iris_data()
        
        with self.client.post("/predict", 
                             json=sample_data,
                             catch_response=True) as response:
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    # Validate response structure
                    required_fields = ["predicted_species", "prediction_probability", 
                                     "inference_time", "total_time"]
                    if all(field in result for field in required_fields):
                        
                        # Extract timing information for performance analysis
                        inference_time = float(result["inference_time"].replace('s', ''))
                        total_time = float(result["total_time"].replace('s', ''))
                        
                        # Log slow predictions for bottleneck analysis
                        if total_time > 1.0:  # Log predictions taking > 1 second
                            print(f"SLOW PREDICTION: {total_time:.4f}s - Data: {sample_data}")
                        
                        response.success()
                    else:
                        response.failure(f"Missing required fields in response: {result}")
                        
                except (ValueError, KeyError) as e:
                    response.failure(f"Invalid JSON response: {e}")
            else:
                response.failure(f"HTTP {response.status_code}: {response.text}")
    
    @task(2)  # Lower weight for health checks
    def test_health_endpoint(self):
        """Test the health check endpoint for monitoring."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get("status") == "healthy":
                        response.success()
                    else:
                        response.failure(f"API unhealthy: {result}")
                except ValueError:
                    response.failure("Invalid JSON in health response")
            else:
                response.failure(f"Health check failed with status {response.status_code}")
    
    @task(1)  # Lowest weight for documentation endpoint
    def test_root_endpoint(self):
        """Test the root endpoint."""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Root endpoint failed with status {response.status_code}")
    
    @task(1)
    def test_docs_endpoint(self):
        """Test the API documentation endpoint."""
        with self.client.get("/docs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Docs endpoint failed with status {response.status_code}")


class HighLoadUser(IrisPredictionAPIUser):
    """
    Specialized user class for high-load testing (300+ users).
    Reduced wait time to generate maximum concurrent load.
    """
    wait_time = between(0.1, 0.5)  # Very aggressive load pattern


class StressTestUser(IrisPredictionAPIUser):
    """
    Stress test user that sends rapid-fire requests to identify breaking points.
    """
    wait_time = between(0.05, 0.2)  # Minimal wait time for stress testing
    
    @task(15)  # Even higher weight on prediction endpoint for stress testing
    def stress_test_predict(self):
        """Stress test the prediction endpoint with minimal delay."""
        sample_data = self.generate_iris_data()
        self.client.post("/predict", json=sample_data)