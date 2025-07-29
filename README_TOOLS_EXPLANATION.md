# MLOps Scaling Tools - Technical Overview

## 🎯 **Overview**
This document explains the four key tools used in our MLOps scaling pipeline: OpenTelemetry, Horizontal Pod Autoscaler (HPA), WRK, and Locust. Each tool serves a specific purpose in monitoring, scaling, and testing our Iris prediction API under concurrent load.

---

## 🔍 **OpenTelemetry - Distributed Tracing & Observability**

### **What it does:**
OpenTelemetry provides distributed tracing and observability for our FastAPI application, allowing us to monitor performance bottlenecks at a granular level.

### **Key Components in our implementation:**

#### **1. Tracer Configuration**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

# Configure with AlwaysOnSampler for complete trace collection
trace.set_tracer_provider(TracerProvider(
    sampler=AlwaysOnSampler()  # Captures 100% of traces
))
```

#### **2. Custom Spans in our API**
- **`model_loading`**: Tracks startup model loading time
- **`prediction_request`**: Overall request processing time
- **`data_preparation`**: Time to convert input to DataFrame
- **`model_inference`**: **Core ML prediction timing** (most critical metric)
- **`health_check`**: Health endpoint performance monitoring

#### **3. Span Attributes**
```python
# Example span with detailed attributes
with tracer.start_as_current_span("model_inference") as span:
    model_start_time = time.time()
    prediction = model.predict(data)
    inference_time = time.time() - model_start_time
    
    # Set performance attributes
    span.set_attribute("model.inference_time_seconds", inference_time)
    span.set_attribute("model.predicted_species", prediction[0])
    span.set_attribute("model.prediction_probability", float(probability))
```

### **Why it's important:**
- **Bottleneck Identification**: Pinpoints exactly where time is spent in each request
- **Performance Regression Detection**: Tracks performance changes over time
- **Distributed System Monitoring**: Traces requests across multiple services
- **Production Debugging**: Helps debug slow requests in production

### **Expected Outputs:**
- **Google Cloud Trace Console**: Visual trace timeline showing span durations
- **Span Details**: Detailed timing breakdown for each request component
- **Performance Trends**: Historical performance data for optimization

---

## 📈 **Horizontal Pod Autoscaler (HPA) - Automatic Scaling**

### **What it does:**
HPA automatically scales the number of pod replicas based on observed CPU utilization, memory usage, and custom metrics.

### **Our HPA Configuration:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: iris-prediction-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: iris-prediction-api
  minReplicas: 2
  maxReplicas: 15
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Percent
        value: 100  # Double replicas
        periodSeconds: 30
      - type: Pods
        value: 3    # Or add 3 pods
        periodSeconds: 30
    scaleDown:
      stabilizationWindowSeconds: 120
      policies:
      - type: Percent
        value: 50   # Remove 50% of replicas
        periodSeconds: 60
```

### **Key Features:**
1. **Multi-Metric Scaling**: CPU (60%) and Memory (70%) thresholds
2. **Aggressive Scale-Up**: Doubles replicas or adds 3 pods every 30 seconds
3. **Conservative Scale-Down**: 50% reduction with 2-minute stabilization
4. **Range**: 2-15 replicas to handle varying load

### **Scaling Triggers:**
- **Scale Up**: When CPU > 60% OR Memory > 70%
- **Scale Down**: When CPU < 60% AND Memory < 70% for 2+ minutes

### **Expected Outputs:**
```bash
# HPA Status Commands
kubectl get hpa iris-prediction-api-hpa
kubectl describe hpa iris-prediction-api-hpa

# Expected Output:
NAME                      REFERENCE                        TARGETS   MINPODS   MAXPODS   REPLICAS
iris-prediction-api-hpa   Deployment/iris-prediction-api   45%/60%   2         15        4

# Scaling Events
kubectl get events --sort-by='.lastTimestamp' | grep HorizontalPodAutoscaler
```

---

## ⚡ **WRK - HTTP Benchmarking Tool**

### **What it does:**
WRK is a high-performance HTTP benchmarking tool that generates controlled load to test API performance and measure throughput/latency.

### **Our WRK Implementation:**
```lua
-- wrk_script.lua
wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.body = '{"sepal_length": 6.765352725982666, "sepal_width": 2.824432849884033, "petal_width": 1.8131520748138428, "petal_length": 4.90852165222168}'

function response(status, headers, body)
    if status ~= 200 then
        print("Error: " .. status)
    end
end
```

### **Test Commands:**
```bash
# Basic load test
wrk -t4 -c100 -d30s -s wrk_script.lua http://EXTERNAL_IP/predict

# High concurrency test
wrk -t8 -c300 -d60s -s wrk_script.lua http://EXTERNAL_IP/predict

# Stress test
wrk -t12 -c500 -d120s -s wrk_script.lua http://EXTERNAL_IP/predict
```

### **Parameters Explained:**
- **-t**: Number of threads (CPU cores)
- **-c**: Number of connections (concurrent users)
- **-d**: Duration of test
- **-s**: Script file for custom request

### **Expected Outputs:**
```
Running 30s test @ http://EXTERNAL_IP/predict
  4 threads and 100 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency   245.67ms  123.45ms   2.10s    87.56%
    Req/Sec    89.12     23.45   156.00     78.23%
  10654 requests in 30.00s, 2.34MB read
  Socket errors: connect 0, read 0, write 0, timeout 5
Requests/sec:    355.13
Transfer/sec:     79.87KB
```

### **Why WRK is valuable:**
- **High Performance**: C-based tool with minimal overhead
- **Precise Control**: Exact concurrency and duration control
- **Detailed Metrics**: Latency distribution and throughput statistics
- **Custom Scripts**: Lua scripting for complex request patterns

---

## 🐝 **Locust - Load Testing Framework**

### **What it does:**
Locust is a Python-based load testing tool that simulates realistic user behavior with a web-based UI for monitoring and control.

### **Our Locust Implementation:**

#### **1. User Classes**
```python
class IrisPredictionAPIUser(HttpUser):
    """Normal load testing (0.5-2s intervals)"""
    wait_time = between(0.5, 2.0)
    
    @task(10)  # High weight for prediction endpoint
    def test_predict_endpoint(self):
        sample_data = self.generate_iris_data()
        with self.client.post("/predict", json=sample_data, catch_response=True) as response:
            # Performance monitoring and validation

class HighLoadUser(IrisPredictionAPIUser):
    """Aggressive load testing (0.1-0.5s intervals)"""
    wait_time = between(0.1, 0.5)

class StressTestUser(IrisPredictionAPIUser):
    """Stress testing (0.05-0.2s intervals)"""
    wait_time = between(0.05, 0.2)
```

#### **2. Realistic Data Generation**
```python
def generate_iris_data(self):
    """Generate realistic Iris measurements based on dataset statistics"""
    iris_samples = [
        # Setosa samples
        {"sepal_length": round(random.uniform(4.3, 5.8), 1), ...},
        # Versicolor samples  
        {"sepal_length": round(random.uniform(4.9, 7.0), 1), ...},
        # Virginica samples
        {"sepal_length": round(random.uniform(4.9, 7.9), 1), ...}
    ]
    return random.choice(iris_samples)
```

### **Locust Features:**
1. **Web UI**: Real-time monitoring at `http://localhost:8089`
2. **Performance Monitoring**: Built-in slow request detection
3. **Multiple User Types**: Different load patterns for comprehensive testing
4. **Response Validation**: Automatic API response verification

### **Test Scenarios:**
```bash
# Start Locust
locust -f locustfile.py --host=http://EXTERNAL_IP

# Web UI Configuration:
# 150 Users Test: 150 users, 10 users/sec spawn rate
# 300 Users Test: 300 users, 10 users/sec spawn rate
# Stress Test: 500+ users, 20 users/sec spawn rate
```

### **Expected Outputs:**
- **Statistics Tab**: Request counts, response times, failure rates
- **Charts Tab**: Real-time performance graphs
- **Failures Tab**: Failed request details
- **Exceptions Tab**: Application errors

---

## 🔄 **How These Tools Work Together**

### **1. Monitoring Pipeline:**
```
Locust/WRK → Generate Load → FastAPI + OpenTelemetry → Cloud Trace
                ↓
           HPA Monitors Metrics → Scales Pods → Handles Increased Load
```

### **2. Bottleneck Detection Workflow:**
1. **Load Generation**: Locust/WRK creates concurrent requests
2. **Performance Tracking**: OpenTelemetry captures detailed timing
3. **Resource Monitoring**: HPA tracks CPU/memory usage
4. **Automatic Scaling**: HPA adds/removes pods based on load
5. **Analysis**: Cloud Trace provides performance insights

### **3. Key Metrics Correlation:**
- **WRK Latency** ↔ **OpenTelemetry Span Duration**
- **Locust RPS** ↔ **HPA CPU Utilization**
- **Pod Count** ↔ **Response Time Improvements**
- **Failure Rate** ↔ **Resource Constraints**

---

## 📊 **Expected Integration Results**

### **Under Normal Load (150 users):**
- **WRK**: ~200ms average latency, 300+ RPS
- **OpenTelemetry**: 5-15ms model inference time
- **HPA**: Scales to 4-6 pods
- **Locust**: <1% failure rate

### **Under High Load (300 users):**
- **WRK**: ~400ms average latency, 500+ RPS
- **OpenTelemetry**: 10-25ms model inference time (increased)
- **HPA**: Scales to 8-12 pods
- **Locust**: 2-5% failure rate during scaling

### **Bottleneck Identification:**
1. **Model Inference**: Primary bottleneck under concurrent load
2. **Memory Pressure**: Secondary bottleneck for data processing
3. **Pod Startup Time**: Scaling delay during traffic spikes
4. **Network I/O**: Load balancer limitations at extreme load

This comprehensive tooling setup provides complete visibility into system performance and automatic scaling capabilities for production MLOps workloads. 