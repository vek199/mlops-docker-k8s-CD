"""
Load testing configuration for Iris Prediction API using Locust.
"""
from locust import HttpUser, task, between


class IrisPredictionAPIUser(HttpUser):
    """Locust user class for testing the Iris Prediction API."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts."""
        # Test the health endpoint first
        self.client.get("/health")
    
    @task(3)
    def test_predict_endpoint(self):
        """Test the prediction endpoint with sample data."""
        sample_data = {
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2
        }
        response = self.client.post("/predict", json=sample_data)
        
        if response.status_code == 200:
            result = response.json()
            assert "predicted_species" in result
            assert "prediction_probability" in result
    
    @task(1)
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        self.client.get("/health")
    
    @task(1)
    def test_root_endpoint(self):
        """Test the root endpoint."""
        self.client.get("/")