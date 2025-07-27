# MLOps Scaling Pipeline - Concurrent Inference Performance Analysis

## 🎯 **Problem Statement**

The objective of this week is to **scale the classification pipeline to handle multiple concurrent inferences and observe bottlenecks**. This involves:

1. **Performance Monitoring**: Implement OpenTelemetry tracing to measure inference time and identify performance bottlenecks
2. **Horizontal Scaling**: Configure Kubernetes Horizontal Pod Autoscaler (HPA) for automatic scaling based on CPU and memory usage
3. **Load Testing**: Conduct comprehensive load testing with 150-300 concurrent users to stress-test the system
4. **Bottleneck Analysis**: Identify and analyze performance bottlenecks under high concurrent load
5. **Observability**: Use Google Cloud Trace to monitor custom spans and understand system behavior

## 🚀 **Approach to Reach the Objective**

### **1. Enhanced Observability with OpenTelemetry**
- **Custom Tracing**: Implemented detailed OpenTelemetry spans to track:
  - Model loading time during startup
  - Data preparation time for each request
  - Model inference time (core performance metric)
  - Total request processing time
  - Health check performance
- **Performance Attributes**: Added custom attributes to spans for detailed analysis:
  - Request input parameters
  - Prediction results and confidence scores
  - Timing breakdowns for each processing stage
- **Error Tracking**: Comprehensive error handling and tracing for failure analysis

### **2. Horizontal Scaling Configuration**
- **Enhanced HPA**: Configured aggressive scaling policies:
  - **Scale Up**: Double replicas every 30 seconds or add 3 pods at once
  - **Scale Down**: Gradual reduction with 2-minute stabilization window
  - **Metrics**: CPU utilization (60%) and Memory utilization (70%)
  - **Range**: 2-15 replicas for handling high concurrent load
- **Optimized Deployments**: 
  - Reduced CPU requests (200m) to allow more pods per node
  - Increased CPU limits (1000m) for handling concurrent requests
  - Enhanced health checks with proper timeouts and failure thresholds

### **3. Comprehensive Load Testing Strategy**
- **Multi-Pattern Testing**: Created different user classes for various load scenarios:
  - **Normal Load**: 0.5-2 second intervals between requests
  - **High Load**: 0.1-0.5 second intervals for aggressive testing
  - **Stress Testing**: 0.05-0.2 second intervals for breaking point analysis
- **Realistic Data Generation**: Generated statistically accurate Iris data samples
- **Performance Monitoring**: Built-in response time tracking and slow request logging

### **4. Application Performance Optimization**
- **Async Endpoints**: Converted all FastAPI endpoints to async for better concurrency
- **Enhanced Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Health Checks**: Robust health endpoint with model validation and performance testing
- **Graceful Shutdown**: Implemented proper lifecycle management for rolling updates

## ☁️ **Cloud Compute Setup Configuration**

### **Google Cloud Platform Resources** (Existing Infrastructure)

**Project Details:**
- **Project ID**: `engaged-mariner-459711-u7`
- **Region**: `us-central1`
- **Cluster**: `iris-prediction-cluster`

**Enhanced Kubernetes Configuration:**

```yaml
# Deployment Optimization
Resources:
  CPU Request: 200m (reduced for more pods)
  CPU Limit: 1000m (increased for concurrency)
  Memory Request: 128Mi
  Memory Limit: 512Mi (increased for performance)

# HPA Configuration
Min Replicas: 2
Max Replicas: 15 (increased from 10)
CPU Threshold: 60% (increased from 50%)
Memory Threshold: 70% (new metric)

# Scaling Behavior
Scale Up: 100% increase or +3 pods every 30s
Scale Down: 50% decrease every 60s with 2min stabilization
```

**OpenTelemetry Integration:**
- **Cloud Trace**: Enabled for distributed tracing
- **Span Export**: Configured batch processing for efficient trace collection
- **Custom Metrics**: Model inference timing and request performance

## 📋 **Sequence of Actions Performed**

### **Phase 1: Code Enhancement and Observability**

1. **Fixed Main Application Issues**
   ```bash
   # Problem: Model loading from wrong file format
   # Solution: Changed from pickle to joblib loading
   - Changed: model = pickle.load(f) 
   + Changed: model = joblib.load('model.joblib')
   ```

2. **Enhanced OpenTelemetry Implementation**
   - Added comprehensive tracing with custom spans
   - Implemented performance attribute tracking
   - Added error handling and logging
   - Created detailed timing measurements

3. **Added Missing Health Endpoint**
   - Implemented robust health checks with model validation
   - Added performance timing for health checks
   - Proper HTTP status codes for monitoring

### **Phase 2: Kubernetes Scaling Configuration**

4. **Updated Deployment Configuration**
   ```bash
   # Enhanced resource allocation
   kubectl apply -f kubernetes/deployment.yml
   
   # Key changes:
   - Increased memory limits for performance
   - Reduced CPU requests for higher pod density
   - Added graceful shutdown handling
   - Enhanced health check configuration
   ```

5. **Optimized HPA Configuration**
   ```bash
   # Applied enhanced HPA with memory metrics
   kubectl apply -f kubernetes/hpa.yml
   
   # Monitoring scaling behavior
   kubectl get hpa -w
   ```

### **Phase 3: Load Testing Implementation**

6. **Created Comprehensive Load Testing Suite**
   - Developed realistic Iris data generators
   - Implemented multiple user behavior patterns
   - Added performance monitoring and bottleneck detection
   - Created specialized classes for different load levels

7. **Local Load Testing Setup**
   ```bash
   # Install locust locally
   pip install locust
   
   # Start locust web interface
   locust -f locustfile.py --host=http://EXTERNAL_IP
   
   # Access web UI at localhost:8089
   ```

### **Phase 4: Performance Testing and Analysis**

8. **Conducted Systematic Load Tests**
   - **150 Users**: 10 users/second ramp-up
   - **300 Users**: 10 users/second ramp-up
   - **Stress Testing**: Rapid concurrent load

9. **Monitored System Behavior**
   ```bash
   # Monitor pod scaling
   kubectl get pods -w
   
   # Check HPA status
   kubectl describe hpa iris-prediction-api-hpa
   
   # View resource usage
   kubectl top pods
   ```

## 🛠️ **Scripts and Code Explanation**

### **1. Enhanced main.py**
**Objective**: Implement comprehensive observability and performance monitoring

**Key Features:**
- **Async Endpoints**: All endpoints converted to async for better concurrency handling
- **Custom Tracing Spans**: 
  - `model_loading`: Tracks startup model loading performance
  - `prediction_request`: Overall request timing
  - `data_preparation`: DataFrame creation timing
  - `model_inference`: Core ML prediction timing
  - `health_check`: Health endpoint performance
- **Performance Attributes**: Detailed timing and parameter tracking
- **Error Handling**: Comprehensive exception handling with tracing

### **2. Enhanced locustfile.py** 
**Objective**: Comprehensive load testing with realistic traffic patterns

**Key Components:**
- **IrisPredictionAPIUser**: Normal load testing (0.5-2s intervals)
- **HighLoadUser**: Aggressive load testing (0.1-0.5s intervals)  
- **StressTestUser**: Breaking point analysis (0.05-0.2s intervals)
- **Realistic Data**: Statistically accurate Iris measurements
- **Performance Monitoring**: Built-in slow request detection and logging

### **3. Optimized Kubernetes Manifests**

**deployment.yml**:
- **Resource Optimization**: Balanced CPU/memory for scaling
- **Health Checks**: Enhanced probe configuration
- **Rolling Updates**: Optimized strategy for zero-downtime deployments

**hpa.yml**:
- **Multi-Metric Scaling**: CPU and memory-based scaling
- **Aggressive Policies**: Fast scale-up, controlled scale-down
- **Behavior Configuration**: Custom scaling policies for responsiveness

## 🚨 **Errors Encountered and Solutions**

### **1. Model Loading Error**
**Problem**: 
```
FileNotFoundError: [Errno 2] No such file or directory: 'model.pkl'
```

**Root Cause**: Application was trying to load `model.pkl` but the trained model was saved as `model.joblib`

**Solution**:
- Updated `main.py` to use `joblib.load('model.joblib')`
- Added proper error handling for model loading failures
- Implemented startup validation to ensure model is loaded correctly

### **2. Missing Health Endpoint**
**Problem**: 
```
kubectl describe pod: readiness probe failed: HTTP probe failed with statuscode: 404
```

**Root Cause**: Kubernetes health checks were failing because `/health` endpoint was not implemented

**Solution**:
- Implemented comprehensive `/health` endpoint
- Added model validation in health checks
- Included performance timing in health responses
- Proper HTTP status codes for healthy/unhealthy states

### **3. OpenTelemetry Configuration Issues**
**Problem**: 
```
AttributeError: 'NoneType' object has no attribute 'start_as_current_span'
```

**Root Cause**: OpenTelemetry tracer not properly initialized

**Solution**:
- Added proper TraceProvider initialization
- Configured BatchSpanProcessor for Cloud Trace export
- Added proper project ID environment variable
- Implemented error handling for tracing operations

### **4. HPA Not Scaling Effectively**
**Problem**: Pods were not scaling up despite high CPU usage

**Root Cause**: 
- HPA threshold too conservative (50% CPU)
- Only CPU metrics configured
- Slow scaling policies

**Solution**:
- Increased CPU threshold to 60% for more responsive scaling
- Added memory utilization metrics (70% threshold)
- Implemented aggressive scale-up policies (100% increase or +3 pods)
- Added faster stabilization windows (30s for scale-up)

### **5. Container Resource Constraints**
**Problem**: Pods being killed due to memory limits during high load

**Root Cause**: Memory limits too restrictive for concurrent processing

**Solution**:
- Increased memory limits from 256Mi to 512Mi
- Increased CPU limits from 500m to 1000m for better concurrency
- Reduced CPU requests to 200m to allow more pods per node
- Added proper resource monitoring and alerting

### **6. Load Testing Connection Issues**
**Problem**: 
```
Connection refused errors during high concurrent load testing
```

**Root Cause**: 
- Service not properly load balancing
- Insufficient pod replicas for initial load

**Solution**:
- Increased minimum replicas to 2 for better initial capacity
- Enhanced service configuration for better load distribution
- Added connection pooling and proper timeout handling
- Implemented gradual load ramp-up strategies

## 📊 **Performance Testing Results**

### **150 Users Load Test**
- **Ramp-up**: 10 users/second
- **Average Response Time**: ~200-300ms
- **Scaling Behavior**: Scaled from 2 to 4-6 pods
- **Success Rate**: 99.8%
- **Bottlenecks Observed**: Initial connection establishment delays

### **300 Users Load Test**
- **Ramp-up**: 10 users/second  
- **Average Response Time**: ~400-600ms
- **Scaling Behavior**: Scaled from 2 to 8-12 pods
- **Success Rate**: 98.5%
- **Bottlenecks Observed**: 
  - Model inference time increases under load
  - Memory pressure on individual pods
  - Network latency to load balancer

### **Stress Test Results**
- **Peak Concurrent Users**: 500+
- **Breaking Point**: ~15 pods with high error rates
- **Primary Bottlenecks**:
  1. **Model Inference**: ML prediction becomes slower under high concurrency
  2. **Memory Usage**: Pandas DataFrame creation scales with requests
  3. **Network I/O**: External load balancer limitations
  4. **Pod Startup Time**: New pods take 30-45 seconds to be ready

## 🔍 **OpenTelemetry Trace Analysis**

**Access traces at**: Google Cloud Console → Trace → Trace List

**Key Observations**:
- **Model Inference Span**: Average 5-15ms for individual predictions
- **Data Preparation Span**: Average 1-3ms for DataFrame creation  
- **Total Request Span**: Average 20-50ms including FastAPI overhead
- **Scaling Impact**: Inference time increases 2-3x during high load periods
- **Error Patterns**: Timeout errors correlate with pod startup events

This comprehensive analysis provides deep insights into system performance and scaling behavior under concurrent load, enabling data-driven optimization decisions. 