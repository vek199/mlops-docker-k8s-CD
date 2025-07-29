# MLOps Scaling Testing Instructions - Complete Guide

## 🎯 **Overview**
This guide provides detailed instructions to generate all the required outputs for your final submission including WRK benchmarks, Locust load tests, HPA scaling demonstrations, OpenTelemetry traces, and pod failure analysis.

---

## 📋 **Prerequisites Setup**

### **1. Environment Verification**
```bash
# Verify Kubernetes cluster is running
kubectl cluster-info
kubectl get nodes

# Check deployment status
kubectl get deployments iris-prediction-api
kubectl get services iris-prediction-api-service
kubectl get hpa iris-prediction-api-hpa

# Get external IP for testing
EXTERNAL_IP=$(kubectl get service iris-prediction-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"
```

### **2. Install Testing Tools**
```bash
# Install WRK (HTTP benchmarking)
# On macOS:
brew install wrk

# On Ubuntu/Debian:
sudo apt-get install wrk

# On CentOS/RHEL:
sudo yum install wrk

# Install Locust (already done)
pip install locust

# Verify installations
wrk --version
locust --version
```

---

## ⚡ **WRK Load Testing - Required Outputs**

### **1. Create WRK Script**
```bash
# Create wrk_script.lua
cat > wrk_script.lua << 'EOF'
wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.body = '{"sepal_length": 6.765352725982666, "sepal_width": 2.824432849884033, "petal_width": 1.8131520748138428, "petal_length": 4.90852165222168}'

-- Track successful and failed requests
local counter = 0

function response(status, headers, body)
    counter = counter + 1
    if status ~= 200 then
        print("Request " .. counter .. " failed with status: " .. status)
    elseif counter % 100 == 0 then
        print("Completed " .. counter .. " requests")
    end
end

function done(summary, latency, requests)
    print("Total requests: " .. summary.requests)
    print("Total errors: " .. summary.errors.status)
    print("Average latency: " .. latency.mean .. "ms")
    print("Max latency: " .. latency.max .. "ms")
    print("Requests/sec: " .. summary.requests / summary.duration * 1000000)
end
EOF
```

### **2. WRK Test Scenarios**

#### **Test 1: Light Load (50 concurrent users)**
```bash
echo "=== WRK Test 1: Light Load ==="
wrk -t4 -c50 -d30s -s wrk_script.lua http://$EXTERNAL_IP/predict

# Expected Output:
# Running 30s test @ http://EXTERNAL_IP/predict
#   4 threads and 50 connections
#   Thread Stats   Avg      Stdev     Max   +/- Stdev
#     Latency   120.34ms   45.67ms   500.00ms    73.45%
#     Req/Sec   104.23     15.67     140.00     81.23%
#   12453 requests in 30.03s, 2.89MB read
# Requests/sec:    414.56
# Transfer/sec:     98.45KB
```

#### **Test 2: Medium Load (150 concurrent users)**
```bash
echo "=== WRK Test 2: Medium Load ==="
wrk -t6 -c150 -d60s -s wrk_script.lua http://$EXTERNAL_IP/predict

# Monitor HPA during this test
kubectl get hpa iris-prediction-api-hpa -w &
kubectl get pods -l app=iris-prediction-api -w &
```

#### **Test 3: High Load (300 concurrent users)**
```bash
echo "=== WRK Test 3: High Load ==="
wrk -t8 -c300 -d90s -s wrk_script.lua http://$EXTERNAL_IP/predict

# This should trigger aggressive scaling
```

#### **Test 4: Stress Test (500+ concurrent users)**
```bash
echo "=== WRK Test 4: Stress Test ==="
wrk -t12 -c500 -d120s -s wrk_script.lua http://$EXTERNAL_IP/predict

# This should show pod failures and limits
```

### **3. Capture WRK Outputs**
```bash
# Run comprehensive WRK test with output capture
{
    echo "=== MLOps Scaling WRK Test Results ==="
    echo "Date: $(date)"
    echo "External IP: $EXTERNAL_IP"
    echo
    
    echo "=== Test 1: Light Load (50 users, 30s) ==="
    wrk -t4 -c50 -d30s -s wrk_script.lua http://$EXTERNAL_IP/predict
    echo
    
    echo "=== Test 2: Medium Load (150 users, 60s) ==="
    wrk -t6 -c150 -d60s -s wrk_script.lua http://$EXTERNAL_IP/predict
    echo
    
    echo "=== Test 3: High Load (300 users, 90s) ==="
    wrk -t8 -c300 -d90s -s wrk_script.lua http://$EXTERNAL_IP/predict
    echo
    
    echo "=== Test 4: Stress Test (500 users, 120s) ==="
    wrk -t12 -c500 -d120s -s wrk_script.lua http://$EXTERNAL_IP/predict
    echo
    
} | tee wrk_test_results.txt
```

---

## 🐝 **Locust Load Testing - Required Outputs**

### **1. Start Locust with Web UI**
```bash
# Start Locust
locust -f locustfile.py --host=http://$EXTERNAL_IP

# Access web UI at: http://localhost:8089
echo "Locust Web UI: http://localhost:8089"
```

### **2. Locust Test Scenarios**

#### **Test 1: 150 Users Load Test**
1. **Web UI Configuration:**
   - Number of users: `150`
   - Spawn rate: `10` users/second
   - Host: `http://EXTERNAL_IP`

2. **Monitor During Test:**
```bash
# Terminal 1: Monitor HPA
watch "kubectl get hpa iris-prediction-api-hpa"

# Terminal 2: Monitor Pods
watch "kubectl get pods -l app=iris-prediction-api"

# Terminal 3: Monitor Resource Usage
watch "kubectl top pods -l app=iris-prediction-api"
```

3. **Capture Screenshots:**
   - Locust Statistics tab
   - Locust Charts tab
   - Any failures in Failures tab

#### **Test 2: 300 Users Load Test**
1. **Stop previous test** in Locust UI
2. **Configure new test:**
   - Number of users: `300`
   - Spawn rate: `10` users/second
3. **Run for 10-15 minutes** to observe scaling

#### **Test 3: Stress Test (500+ Users)**
1. **Configure stress test:**
   - Number of users: `500`
   - Spawn rate: `20` users/second
   - User class: `StressTestUser` (if available)

### **3. Capture Locust Outputs**
```bash
# Generate Locust report (run after tests)
# Note: Replace with actual stats from Locust UI

cat > locust_test_results.txt << 'EOF'
=== Locust Load Test Results ===

Test 1: 150 Users (10 users/sec spawn)
- Total Requests: 45,632
- Failures: 127 (0.28%)
- Average Response Time: 245ms
- Min Response Time: 12ms
- Max Response Time: 2,340ms
- Requests/sec: 304.2
- Test Duration: 150 seconds

Test 2: 300 Users (10 users/sec spawn)  
- Total Requests: 89,754
- Failures: 2,341 (2.61%)
- Average Response Time: 456ms
- Min Response Time: 15ms
- Max Response Time: 8,970ms
- Requests/sec: 448.7
- Test Duration: 200 seconds

Test 3: Stress Test (500 Users, 20 users/sec spawn)
- Total Requests: 134,567
- Failures: 8,934 (6.64%)
- Average Response Time: 1,234ms
- Min Response Time: 18ms
- Max Response Time: 30,000ms (timeouts)
- Requests/sec: 672.8
- Test Duration: 300 seconds
EOF
```

---

## 📈 **HPA Monitoring - Required Outputs**

### **1. HPA Status Commands**
```bash
# Basic HPA status
kubectl get hpa iris-prediction-api-hpa

# Detailed HPA description
kubectl describe hpa iris-prediction-api-hpa

# HPA events and scaling decisions
kubectl get events --sort-by='.lastTimestamp' | grep HorizontalPodAutoscaler

# Real-time HPA monitoring
kubectl get hpa iris-prediction-api-hpa -w
```

### **2. Pod Scaling Monitoring**
```bash
# Monitor pod scaling in real-time
kubectl get pods -l app=iris-prediction-api -w

# Pod resource usage
kubectl top pods -l app=iris-prediction-api

# Pod status with detailed info
kubectl get pods -l app=iris-prediction-api -o wide
```

### **3. Capture HPA Scaling Events**
```bash
# Generate HPA scaling report
{
    echo "=== HPA Scaling Analysis ==="
    echo "Date: $(date)"
    echo
    
    echo "=== Current HPA Status ==="
    kubectl get hpa iris-prediction-api-hpa
    echo
    
    echo "=== HPA Configuration ==="
    kubectl describe hpa iris-prediction-api-hpa
    echo
    
    echo "=== Recent Scaling Events ==="
    kubectl get events --sort-by='.lastTimestamp' | grep HorizontalPodAutoscaler | tail -10
    echo
    
    echo "=== Current Pod Status ==="
    kubectl get pods -l app=iris-prediction-api -o wide
    echo
    
    echo "=== Pod Resource Usage ==="
    kubectl top pods -l app=iris-prediction-api
    echo
    
} | tee hpa_scaling_report.txt
```

---

## 🔍 **OpenTelemetry Traces - Required Outputs**

### **1. Configure AlwaysOnSampler**

Update your `main.py` to include AlwaysOnSampler:
```python
from opentelemetry.sdk.trace.sampling import AlwaysOnSampler

# Enhanced OpenTelemetry setup with AlwaysOnSampler
trace.set_tracer_provider(TracerProvider(
    sampler=AlwaysOnSampler()  # Captures 100% of traces
))
```

### **2. Access Google Cloud Trace**
```bash
# Open Google Cloud Trace Console
echo "Google Cloud Trace URL:"
echo "https://console.cloud.google.com/traces/list?project=engaged-mariner-459711-u7"

# CLI to check traces (if gcloud is configured)
gcloud logging read 'resource.type="gce_instance"' --limit=10 --format=json
```

### **3. Trace Analysis Commands**
```bash
# Generate sample requests for tracing
for i in {1..50}; do
    curl -X POST http://$EXTERNAL_IP/predict \
        -H "Content-Type: application/json" \
        -d '{"sepal_length": 6.765352725982666, "sepal_width": 2.824432849884033, "petal_width": 1.8131520748138428, "petal_length": 4.90852165222168}' \
        -w "Request $i: %{time_total}s\n" \
        -o /dev/null -s
    sleep 0.5
done
```

### **4. Expected Trace Outputs**
Document these from Google Cloud Trace Console:
- **Trace List**: Timeline of requests with durations
- **Span Details**: Breakdown of model_inference, data_preparation, etc.
- **Performance Trends**: Latency increases under load
- **Error Traces**: Failed requests during high load

---

## ❌ **Pod Failures - Required Outputs**

### **1. Induce Pod Failures**
```bash
# Method 1: Resource exhaustion (increase load until pods fail)
wrk -t16 -c1000 -d300s -s wrk_script.lua http://$EXTERNAL_IP/predict

# Method 2: Scale beyond cluster capacity
kubectl scale deployment iris-prediction-api --replicas=20

# Method 3: Delete pods during high load
kubectl delete pod -l app=iris-prediction-api --force
```

### **2. Monitor Pod Failures**
```bash
# Watch pod status for failures
kubectl get pods -l app=iris-prediction-api -w

# Check pod events and errors
kubectl describe pods -l app=iris-prediction-api | grep -A 10 -B 10 "Error\|Failed\|Unhealthy"

# Check pod logs for errors
kubectl logs -l app=iris-prediction-api --tail=100

# System events related to failures
kubectl get events --sort-by='.lastTimestamp' | grep -i "failed\|error\|unhealthy"
```

### **3. Capture Failure Documentation**
```bash
# Generate pod failure report
{
    echo "=== Pod Failure Analysis ==="
    echo "Date: $(date)"
    echo
    
    echo "=== Failed Pod Status ==="
    kubectl get pods -l app=iris-prediction-api | grep -E "Error|Failed|CrashLoopBackOff|Pending"
    echo
    
    echo "=== Pod Failure Events ==="
    kubectl get events --sort-by='.lastTimestamp' | grep -i "failed\|error\|unhealthy\|backoff" | tail -20
    echo
    
    echo "=== Resource Constraints ==="
    kubectl describe nodes | grep -A 5 -B 5 "Resource\|Pressure"
    echo
    
    echo "=== Failed Pod Logs (sample) ==="
    kubectl logs -l app=iris-prediction-api --tail=50 | grep -i error
    echo
    
} | tee pod_failure_report.txt
```

---

## 📊 **Success Logs - Required Outputs**

### **1. Capture Successful Operations**
```bash
# Application success logs
kubectl logs -l app=iris-prediction-api --tail=100 | grep -i "prediction completed\|healthy\|success"

# Successful scaling events
kubectl get events --sort-by='.lastTimestamp' | grep "SuccessfulRescale\|ScaledUp\|ScaledDown"

# Successful deployments
kubectl get events --sort-by='.lastTimestamp' | grep "Successful"
```

### **2. Generate Success Report**
```bash
{
    echo "=== Successful Operations Report ==="
    echo "Date: $(date)"
    echo
    
    echo "=== Successful Predictions (Last 50) ==="
    kubectl logs -l app=iris-prediction-api --tail=100 | grep "Prediction completed" | tail -50
    echo
    
    echo "=== Successful Health Checks ==="
    kubectl logs -l app=iris-prediction-api --tail=100 | grep "healthy" | tail -10
    echo
    
    echo "=== Successful Scaling Events ==="
    kubectl get events --sort-by='.lastTimestamp' | grep "Successful.*Scale" | tail -10
    echo
    
    echo "=== Current Healthy Status ==="
    kubectl get pods -l app=iris-prediction-api
    kubectl get hpa iris-prediction-api-hpa
    echo
    
} | tee success_operations_report.txt
```

---

## 📋 **Complete Testing Workflow**

### **Step-by-Step Execution:**

1. **Preparation Phase:**
```bash
# Verify setup
./verify_setup.sh
EXTERNAL_IP=$(kubectl get service iris-prediction-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
```

2. **WRK Testing Phase:**
```bash
# Run all WRK tests
./run_wrk_tests.sh > wrk_results.txt 2>&1
```

3. **Locust Testing Phase:**
```bash
# Start Locust (background)
locust -f locustfile.py --host=http://$EXTERNAL_IP &

# Run monitoring scripts
./monitor_hpa.sh &
./monitor_pods.sh &

# Manual Locust tests via Web UI at localhost:8089
```

4. **Data Collection Phase:**
```bash
# Collect all outputs
./collect_outputs.sh
```

5. **OpenTelemetry Analysis:**
   - Access Google Cloud Trace Console
   - Filter by time range of your tests
   - Export trace data and screenshots

### **Final Output Files:**
- `wrk_test_results.txt`
- `locust_test_results.txt`
- `hpa_scaling_report.txt`
- `pod_failure_report.txt`
- `success_operations_report.txt`
- `opentelemetry_traces/` (screenshots and data)

This comprehensive testing approach will generate all the required outputs for your final submission demonstrating the complete MLOps scaling pipeline under various load conditions. 