# main.py
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel


# Initialize FastAPI app
app = FastAPI(
    title="Iris Species Prediction API",
    description="API for predicting Iris flower species based on sepal and petal measurements",
    version="1.0.0"
)


class IrisFeatures(BaseModel):
    """Pydantic model for Iris flower feature inputs."""
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


# Load the trained model
try:
    model = joblib.load('model.joblib')
    print("Model loaded successfully")
except FileNotFoundError:
    print("Error: model.joblib not found. Please run train.py first.")
    model = None


@app.get("/")
async def get_root():
    """Welcome message for the API root endpoint."""
    return {
        "message": "Welcome to the Iris Species Prediction API!",
        "docs": "Visit /docs for interactive API documentation",
        "health": "Visit /health for API health status"
    }


@app.get("/health")
async def get_health():
    """Health check endpoint."""
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None
    }


@app.post("/predict")
async def predict_iris_species(features: IrisFeatures):
    """Predict the Iris species based on input features."""
    if model is None:
        return {"error": "Model not loaded. Please contact administrator."}
    
    # Convert input to DataFrame
    input_data = pd.DataFrame([[
        features.sepal_length,
        features.sepal_width,
        features.petal_length,
        features.petal_width
    ]], columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
    
    # Make prediction
    prediction = model.predict(input_data)
    prediction_probability = model.predict_proba(input_data).max()
    
    return {
        "predicted_species": prediction[0],
        "prediction_probability": round(float(prediction_probability), 4),
        "input_features": features.dict()
    }