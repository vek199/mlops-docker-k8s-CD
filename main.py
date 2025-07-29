# main.py
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import time
import logging

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from opentelemetry.sdk.trace.sampling import AlwaysOnSampler

# Enhanced OpenTelemetry setup with AlwaysOnSampler
trace.set_tracer_provider(TracerProvider(
    sampler=AlwaysOnSampler()  # Captures 100% of traces
))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- OpenTelemetry Setup ---
trace.set_tracer_provider(TracerProvider())

# Try to use Cloud Trace exporter, fall back to console exporter for local testing
try:
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(CloudTraceSpanExporter())
)
    logger.info("OpenTelemetry configured with Cloud Trace exporter")
except Exception as e:
    logger.warning(f"Could not configure Cloud Trace exporter: {e}")
    # Fall back to console exporter for local testing
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(ConsoleSpanExporter())
    )
    logger.info("OpenTelemetry configured with Console exporter (local testing mode)")

tracer = trace.get_tracer(__name__)
# --- End of OpenTelemetry Setup ---

# Initialize FastAPI app
app = FastAPI(title="Iris Species Predictor API", version="2.0.0")

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Define the request body structure using Pydantic
class IrisRequest(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# Global variable to store the model
model = None

# Load the trained model from the file
def load_model():
    """Load the trained model with error handling and tracing."""
    global model
    with tracer.start_as_current_span("model_loading") as span:
        try:
            start_time = time.time()
            model = joblib.load('model.joblib')
            load_time = time.time() - start_time
            
            span.set_attribute("model.load_time_seconds", load_time)
            span.set_attribute("model.status", "loaded_successfully")
            
            logger.info(f"Model loaded successfully in {load_time:.4f} seconds")
        except Exception as e:
            span.set_attribute("model.status", "load_failed")
            span.set_attribute("model.error", str(e))
            logger.error(f"Failed to load model: {e}")
            raise e

# Load model on startup
load_model()

@app.get("/")
async def read_root():
    """A welcome message for the API root."""
    with tracer.start_as_current_span("root_endpoint"):
        return {
            "message": "Welcome to the Iris Prediction API! Visit /docs for more info.",
            "version": "2.0.0",
            "status": "running"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancing."""
    with tracer.start_as_current_span("health_check") as span:
        try:
            # Check if model is loaded
            if model is None:
                span.set_attribute("health.status", "unhealthy")
                span.set_attribute("health.reason", "model_not_loaded")
                raise HTTPException(status_code=503, detail="Model not loaded")
            
            # Quick model test
            start_time = time.time()
            test_data = pd.DataFrame([[5.1, 3.5, 1.4, 0.2]], 
                                   columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
            _ = model.predict(test_data)
            health_check_time = time.time() - start_time
            
            span.set_attribute("health.status", "healthy")
            span.set_attribute("health.model_test_time_seconds", health_check_time)
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "model_loaded": True,
                "model_test_time": f"{health_check_time:.4f}s"
            }
        except Exception as e:
            span.set_attribute("health.status", "unhealthy")
            span.set_attribute("health.error", str(e))
            raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.post("/predict")
async def predict_species(iris_features: IrisRequest):
    """Predicts the Iris species based on input features with detailed performance tracking."""
    
    with tracer.start_as_current_span("prediction_request") as main_span:
        request_start_time = time.time()
        
        # Set request attributes
        main_span.set_attribute("request.sepal_length", iris_features.sepal_length)
        main_span.set_attribute("request.sepal_width", iris_features.sepal_width)
        main_span.set_attribute("request.petal_length", iris_features.petal_length)
        main_span.set_attribute("request.petal_width", iris_features.petal_width)
        
        try:
            # Data preparation span
            with tracer.start_as_current_span("data_preparation") as data_span:
                data_start_time = time.time()
        data = pd.DataFrame([[
            iris_features.sepal_length,
            iris_features.sepal_width,
            iris_features.petal_length,
            iris_features.petal_width
        ]], columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])
                
                data_prep_time = time.time() - data_start_time
                data_span.set_attribute("data_preparation.time_seconds", data_prep_time)
            
            # Model prediction span
            with tracer.start_as_current_span("model_inference") as model_span:
                model_start_time = time.time()
        
        prediction = model.predict(data)
        probability = model.predict_proba(data).max()
        
                model_inference_time = time.time() - model_start_time
                model_span.set_attribute("model.inference_time_seconds", model_inference_time)
                model_span.set_attribute("model.predicted_species", prediction[0])
                model_span.set_attribute("model.prediction_probability", float(probability))
            
            # Total request time
            total_request_time = time.time() - request_start_time
            main_span.set_attribute("request.total_time_seconds", total_request_time)
            main_span.set_attribute("request.status", "success")
            
            logger.info(f"Prediction completed in {total_request_time:.4f}s - Species: {prediction[0]}")
       
    return {
        "predicted_species": prediction[0],
                "prediction_probability": round(probability, 4),
                "inference_time": f"{model_inference_time:.4f}s",
                "total_time": f"{total_request_time:.4f}s"
            }
            
        except Exception as e:
            main_span.set_attribute("request.status", "error")
            main_span.set_attribute("request.error", str(e))
            logger.error(f"Prediction failed: {e}")
            raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")