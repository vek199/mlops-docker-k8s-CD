# MLOps Scaling Pipeline - Testing Guide

## 🎯 **Overview**
This guide provides step-by-step instructions to test and demonstrate the concurrent inference scaling capabilities of the Iris Prediction API. Follow these steps to observe bottlenecks and scaling behavior under load.

## 📋 **Prerequisites**
- Google Cloud Project: `engaged-mariner-459711-u7`
- GKE Cluster: `iris-prediction-cluster` (already deployed)
- Docker Image: Available in Artifact Registry
- Local machine with Python 3.8+

## 🚀 **Step-by-Step Testing Instructions**

### **Phase 1: Environment Setup and Verification**

#### **1.1 Verify Kubernetes Deployment**
```bash
# Check if pods are running
kubectl get pods -l app=iris-prediction-api

# Verify service and external IP
kubectl get services iris-prediction-api-service

# Check HPA status
kubectl get hpa iris-prediction-api-hpa
```

**Expected Output:**
```
NAME                                READY   STATUS    RESTARTS   AGE
iris-prediction-api-xxxxxxxxx-xxxxx   1/1     Running   0          5m
iris-prediction-api-xxxxxxxxx-xxxxx   1/1     Running   0          5m

NAME                           TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)        AGE
iris-prediction-api-service    LoadBalancer   10.xx.xxx.xx   XX.XX.XX.XX      80:30xxx/TCP   10m

NAME                          REFERENCE                        TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
iris-prediction-api-hpa       Deployment/iris-prediction-api   15%/60%   2         15        2          10m
```

#### **1.2 Get External IP Address**
```bash
# Get the external IP (note this for load testing)
EXTERNAL_IP=$(kubectl get service iris-prediction-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"
```

#### **1.3 Test Basic API Functionality**
```bash
# Test root endpoint
curl http://$EXTERNAL_IP/

# Test health endpoint
curl http://$EXTERNAL_IP/health

# Test prediction endpoint
curl -X POST http://$EXTERNAL_IP/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

**Expected Responses:**
- Root: Welcome message with version 2.0.0
- Health: Status "healthy" with timing information
- Predict: Species prediction with inference timing

### **Phase 2: Install and Configure Load Testing**

#### **2.1 Install Locust Locally**
```bash
# Create virtual environment (recommended)
python -m venv locust_env
source locust_env/bin/activate  # On Windows: locust_env\Scripts\activate

# Install locust
pip install locust

# Verify installation
locust --version
```

#### **2.2 Prepare Load Testing Configuration**
```bash
# Navigate to project directory
cd /path/to/mlops-docker-k8s-CD

# Verify locustfile.py exists and review configuration
cat locustfile.py
```

#### **2.3 Start Locust Web Interface**
```bash
# Start locust with the external IP
locust -f locustfile.py --host=http://$EXTERNAL_IP

# Alternative if you know the IP:
locust -f locustfile.py --host=http://XX.XX.XX.XX
```

**Expected Output:**
```
[2024-01-XX XX:XX:XX,XXX] INFO/locust.main: Starting web interface at http://0.0.0.0:8089
[2024-01-XX XX:XX:XX,XXX] INFO/locust.main: Starting Locust XX.X.X
```

#### **2.4 Access Locust Web UI**
```bash
# Open browser to Locust interface
open http://localhost:8089
# Or manually navigate to: http://localhost:8089
```

### **Phase 3: Conduct Load Testing - 150 Users**

#### **3.1 Configure First Load Test**
In the Locust Web UI:
- **Number of users**: `150`
- **Spawn rate**: `10` (users per second)
- **Host**: Should show your external IP
- **User class**: Leave default (IrisPredictionAPIUser)

#### **3.2 Start Load Test**
1. Click **"Start swarming"**
2. Monitor the following tabs:
   - **Statistics**: Response times, RPS, failure rate
   - **Charts**: Real-time performance graphs
   - **Failures**: Any failed requests
   - **Exceptions**: Application errors

#### **3.3 Monitor Kubernetes Scaling**
Open a new terminal and monitor scaling behavior:
```bash
# Watch pods being created/terminated
kubectl get pods -l app=iris-prediction-api -w

# Monitor HPA scaling decisions
kubectl get hpa iris-prediction-api-hpa -w

# Check resource usage
kubectl top pods -l app=iris-prediction-api
```

#### **3.4 Observe and Record Results**
**Monitor for 5-10 minutes and record:**
- Average response time
- Requests per second (RPS)
- Failure rate
- Number of pods scaled to
- CPU/Memory utilization

**Expected Behavior:**
- Initial response time: 50-200ms
- RPS: 100-200 requests/second
- Scaling: 2 → 4-6 pods
- Minimal failures (<1%)

### **Phase 4: Conduct Load Testing - 300 Users**

#### **4.1 Stop Previous Test**
1. Click **"Stop"** in Locust UI
2. Wait for all users to stop
3. Reset statistics if desired

#### **4.2 Configure High Load Test**
- **Number of users**: `300`
- **Spawn rate**: `10` (users per second)
- **Advanced options**: Select `HighLoadUser` class if available

#### **4.3 Start High Load Test**
1. Click **"Start swarming"**
2. Monitor more aggressively - scaling should be faster

#### **4.4 Monitor System Stress**
```bash
# Watch aggressive scaling
kubectl get hpa -w

# Monitor pod resources under stress
watch "kubectl top pods -l app=iris-prediction-api"

# Check for any pod restarts or failures
kubectl get events --sort-by='.lastTimestamp' | grep iris-prediction-api
```

#### **4.5 Record High Load Results**
**Expected Behavior:**
- Response time: 200-500ms (higher than 150 users)
- RPS: 200-400 requests/second
- Scaling: 2 → 8-12 pods
- Some failures (2-5%) during scaling events

### **Phase 5: OpenTelemetry Trace Analysis**

#### **5.1 Access Google Cloud Trace**
```bash
# Open Google Cloud Console
open https://console.cloud.google.com/traces/list?project=engaged-mariner-459711-u7

# Or navigate manually:
# 1. Go to Google Cloud Console
# 2. Select project: engaged-mariner-459711-u7
# 3. Navigate to "Trace" → "Trace list"
```

#### **5.2 Analyze Custom Spans**
Look for these custom spans in the trace list:
- **`prediction_request`**: Overall request timing
- **`model_inference`**: Core ML prediction time
- **`data_preparation`**: DataFrame creation time
- **`health_check`**: Health endpoint performance

#### **5.3 Trace Analysis Steps**
1. **Filter traces** by time range of your load tests
2. **Sort by latency** to find slowest requests
3. **Click on traces** to see detailed span breakdown
4. **Look for patterns** in timing during scaling events

**Key Metrics to Observe:**
- Model inference time increase during high load
- Total request time breakdown
- Error patterns during pod scaling
- Performance degradation points

### **Phase 6: Bottleneck Analysis and Results**

#### **6.1 Performance Comparison**
Create a comparison table:

| Metric | 150 Users | 300 Users | Difference |
|--------|-----------|-----------|------------|
| Avg Response Time | XXXms | XXXms | +XX% |
| Max Pods Scaled | X | X | +X |
| Failure Rate | X% | X% | +X% |
| RPS Peak | XXX | XXX | +XX% |

#### **6.2 Identified Bottlenecks**
Based on testing, document:
1. **Model Inference Bottleneck**: ML prediction time increases under concurrent load
2. **Memory Pressure**: Pandas operations consume increasing memory
3. **Pod Startup Latency**: New pods take 30-45 seconds to become ready
4. **Network Limitations**: Load balancer connection limits

#### **6.3 Scaling Behavior Analysis**
```bash
# Review HPA scaling events
kubectl describe hpa iris-prediction-api-hpa

# Check scaling policies effectiveness
kubectl get events --sort-by='.lastTimestamp' | grep HorizontalPodAutoscaler
```

### **Phase 7: Cleanup and Documentation**

#### **7.1 Stop Load Testing**
1. Stop Locust tests
2. Close Locust web interface
3. Deactivate virtual environment if used

#### **7.2 Scale Down for Cost Savings**
```bash
# Scale down to minimum replicas
kubectl scale deployment iris-prediction-api --replicas=2

# Verify scaling
kubectl get pods -l app=iris-prediction-api
```

#### **7.3 Generate Test Report**
Document your findings:
- Performance metrics from both tests
- Scaling behavior observations
- OpenTelemetry trace insights
- Identified bottlenecks and potential optimizations

## 🔧 **Troubleshooting Guide**

### **Common Issues and Solutions**

#### **External IP Not Available**
```bash
# Check service status
kubectl describe service iris-prediction-api-service

# If pending, wait a few minutes for GCP load balancer provisioning
kubectl get service iris-prediction-api-service -w
```

#### **Locust Connection Errors**
```bash
# Verify API is accessible
curl http://$EXTERNAL_IP/health

# Check firewall rules if needed
gcloud compute firewall-rules list --filter="name~iris"
```

#### **Pods Not Scaling**
```bash
# Check HPA configuration
kubectl describe hpa iris-prediction-api-hpa

# Verify metrics server is running
kubectl get deployment metrics-server -n kube-system
```

#### **High Error Rates**
```bash
# Check pod logs for errors
kubectl logs -l app=iris-prediction-api --tail=100

# Monitor pod resource usage
kubectl top pods -l app=iris-prediction-api
```

## 📊 **Expected Results Summary**

After completing all tests, you should observe:

1. **Successful Horizontal Scaling**: 2 → 15 pods under high load
2. **Performance Degradation**: Response times increase with concurrent users
3. **OpenTelemetry Insights**: Detailed timing breakdown showing ML inference bottlenecks
4. **System Resilience**: API maintains functionality under stress with acceptable failure rates
5. **Resource Optimization**: Effective CPU/memory-based scaling policies

This comprehensive testing demonstrates the system's ability to handle concurrent load while providing visibility into performance characteristics and scaling behavior. 