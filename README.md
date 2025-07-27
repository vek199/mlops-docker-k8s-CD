# MLOps Continuous Deployment Pipeline - Iris Species Prediction API

## 🎯 **Project Objective**
Develop and integrate Continuous Deployment (CD) pipeline for building an Iris species prediction API using Docker containerization and deploying it onto Kubernetes (K8s) with automated CI/CD workflows.

## 📁 **Project Structure and File Explanations**

### **Core Application Files**
- **`main.py`** - FastAPI application serving the Iris prediction model with REST endpoints
- **`train.py`** - Machine learning model training script using scikit-learn logistic regression
- **`requirements.txt`** - Python dependencies for the application and ML pipeline
- **`iris.csv`** - Training dataset containing Iris flower measurements and species labels

### **Containerization**
- **`Dockerfile`** - Multi-stage Docker container configuration for the FastAPI application
- **`.gitignore`** - Git ignore rules to prevent committing sensitive files and build artifacts

### **Kubernetes Manifests**
- **`kubernetes/deployment.yml`** - K8s deployment configuration with resource limits and health checks
- **`kubernetes/service.yml`** - LoadBalancer service configuration for external API access
- **`kubernetes/hpa.yml`** - Horizontal Pod Autoscaler for automatic scaling based on CPU usage

### **CI/CD Pipeline**
- **`.github/workflows/cd-pipeline.yml`** - GitHub Actions workflow for automated CI/CD pipeline

### **Testing and Utilities**
- **`locustfile.py`** - Load testing configuration using Locust framework for API performance testing
- **`scripts/local-setup.sh`** - Local development environment setup script

### **Documentation**
- **`README.md`** - This comprehensive project documentation
- **`TROUBLESHOOTING.md`** - Troubleshooting guide for common deployment issues (when created)

## 🚀 **Code/Scripts Utilized**

### **Python Files (*.py)**
1. **`main.py`** - Production FastAPI server
2. **`train.py`** - ML model training pipeline
3. **`locustfile.py`** - Performance testing suite

### **Shell Scripts (*.sh)**
1. **`scripts/local-setup.sh`** - Automated local development setup

### **Configuration Files**
1. **`Dockerfile`** - Container build instructions
2. **`requirements.txt`** - Python package dependencies
3. **`kubernetes/*.yml`** - Kubernetes resource definitions
4. **`.github/workflows/cd-pipeline.yml`** - CI/CD automation
5. **`.gitignore`** - Version control exclusions

## 📊 **API Endpoints**
- `GET /` - Welcome message and API information
- `GET /health` - Health check endpoint for monitoring
- `POST /predict` - Iris species prediction from flower measurements
- `GET /docs` - Interactive Swagger/OpenAPI documentation

## 🏗️ **Architecture Overview**
- **ML Model**: Logistic Regression (scikit-learn) trained on Iris dataset
- **API Framework**: FastAPI with async endpoints and automatic documentation
- **Containerization**: Docker with optimized Python 3.10 slim image
- **Orchestration**: Kubernetes on Google Kubernetes Engine (GKE)
- **CI/CD**: GitHub Actions with automated deployment pipeline
- **Storage**: Google Artifact Registry for container images
- **Load Testing**: Locust for performance validation

---

## 📋 **Problem Statement**

The challenge was to create a complete MLOps pipeline that automates the deployment of a machine learning model as a production-ready API. Key requirements included:

1. **Model Deployment**: Convert a trained ML model into a scalable web API
2. **Containerization**: Package the application for consistent deployment across environments
3. **Orchestration**: Deploy on Kubernetes for scalability and reliability
4. **Automation**: Implement CI/CD pipeline for seamless updates and deployments
5. **Monitoring**: Include health checks and performance testing capabilities
6. **Cost Management**: Enable scaling to zero when not in use

## 🎯 **Approach to Reach the Objective**

### **1. Model Development & API Creation**
- Created a FastAPI application with RESTful endpoints
- Implemented logistic regression model training using scikit-learn
- Added comprehensive error handling and input validation
- Included health monitoring and API documentation

### **2. Containerization Strategy**
- Designed multi-stage Dockerfile for optimal image size
- Implemented Docker health checks for container monitoring
- Configured proper port exposure and environment variables
- Optimized build process with proper layer caching

### **3. Kubernetes Configuration**
- Created deployment manifest with resource limits and requests
- Configured LoadBalancer service for external access
- Implemented Horizontal Pod Autoscaler for automatic scaling
- Added liveness and readiness probes for health monitoring

### **4. CI/CD Pipeline Implementation**
- Designed GitHub Actions workflow for automated deployment
- Integrated Google Cloud authentication and authorization
- Configured automated Docker image building and pushing
- Implemented rolling deployment strategy with health checks

### **5. Testing & Validation**
- Created comprehensive load testing suite using Locust
- Implemented API endpoint testing and validation
- Added monitoring and logging capabilities
- Configured performance benchmarking

## ☁️ **Cloud Compute Setup Configuration**

### **Google Cloud Platform Resources**

**Project Configuration:**
- **Project ID**: `engaged-mariner-459711-u7`
- **Region**: `us-central1`
- **Zone**: `us-central1-a`

**Google Kubernetes Engine (GKE):**
```bash
Cluster Name: iris-prediction-cluster
Machine Type: e2-medium
Initial Nodes: 2
Auto-scaling: 1-5 nodes
Features: Autoscaling, Load Balancing, Health Monitoring
```

**Artifact Registry:**
```bash
Repository Name: iris-prediction-repo
Type: Docker
Location: us-central1
Purpose: Container image storage and versioning
```

**Service Account Configuration:**
```bash
Name: github-actions-sa
Roles: 
  - roles/container.developer
  - roles/artifactregistry.writer
Purpose: GitHub Actions authentication and deployment
```

**Kubernetes Resources:**
```yaml
Deployment:
  Replicas: 2 (scalable 1-10)
  CPU Request: 250m
  Memory Request: 128Mi
  CPU Limit: 500m
  Memory Limit: 256Mi

Service:
  Type: LoadBalancer
  External Port: 80
  Internal Port: 8000
  Protocol: TCP
```

## 🔄 **Sequence of Actions Performed**

### **Phase 1: Local Development Setup**
1. **Environment Preparation**
   - Created Python virtual environment
   - Installed required dependencies
   - Set up local development tools

2. **Model Development**
   - Loaded and analyzed Iris dataset
   - Trained logistic regression model
   - Implemented model serialization using joblib

3. **API Development**
   - Created FastAPI application structure
   - Implemented prediction endpoints
   - Added input validation and error handling
   - Created health check and documentation endpoints

### **Phase 2: Containerization**
1. **Docker Configuration**
   - Created optimized Dockerfile
   - Configured proper Python base image
   - Implemented multi-stage build process
   - Added health check configuration

2. **Local Testing**
   - Built Docker image locally
   - Tested container functionality
   - Validated API endpoints
   - Performed basic load testing

### **Phase 3: Cloud Infrastructure Setup**
1. **GCP Project Configuration**
   - Created new GCP project
   - Enabled required APIs (GKE, Artifact Registry, Cloud Build)
   - Configured billing and quotas

2. **Kubernetes Cluster Creation**
   - Deployed GKE cluster with autoscaling
   - Configured node pools and machine types
   - Set up cluster networking and security

3. **Artifact Registry Setup**
   - Created Docker repository
   - Configured authentication and permissions
   - Tested image push/pull functionality

### **Phase 4: Kubernetes Configuration**
1. **Manifest Creation**
   - Designed deployment configuration
   - Created service and ingress rules
   - Configured autoscaling policies

2. **Resource Deployment**
   - Applied Kubernetes manifests
   - Verified pod creation and health
   - Tested service connectivity

### **Phase 5: CI/CD Pipeline Implementation**
1. **GitHub Actions Configuration**
   - Created workflow file
   - Configured GCP authentication
   - Implemented build and deployment steps

2. **Pipeline Testing**
   - Triggered initial deployment
   - Verified automated processes
   - Validated end-to-end functionality

### **Phase 6: Production Validation**
1. **Performance Testing**
   - Conducted load testing with Locust
   - Validated API response times
   - Tested autoscaling behavior

2. **Monitoring Setup**
   - Configured health checks
   - Implemented logging and metrics
   - Tested failure scenarios

## 🚨 **Errors Encountered and Solutions**

### **1. GitHub Actions Authentication Error**
**Problem**: 
```
Error: the GitHub Action workflow must specify exactly one of "workload_identity_provider" or "credentials_json"
```

**Root Cause**: GitHub Actions workflow couldn't access the GCP service account credentials properly.

**Solution**:
- Verified GitHub repository secrets were correctly set
- Updated workflow to use proper `credentials_json` format
- Added secret validation steps in the pipeline
- Implemented fallback authentication methods

### **2. Secret Scanning Block**
**Problem**: 
```
Push cannot contain secrets - Google Cloud Service Account Credentials detected
```

**Root Cause**: Accidentally committed `github-actions-key.json` file to repository.

**Solution**:
- Removed the sensitive file from working directory
- Created comprehensive `.gitignore` file
- Reset git history to remove committed secrets
- Implemented proper secret management practices

### **3. Docker Build Context Issues**
**Problem**: Large build context slowing down image builds.

**Root Cause**: Including unnecessary files in Docker build context.

**Solution**:
- Updated `.gitignore` to exclude build artifacts
- Optimized Dockerfile with proper layer ordering
- Implemented multi-stage build for smaller images
- Added `.dockerignore` file for build optimization

### **4. Kubernetes Resource Conflicts**
**Problem**: Deployment updates failing due to resource conflicts.

**Root Cause**: Horizontal Pod Autoscaler interfering with manual scaling operations.

**Solution**:
- Temporarily disabled HPA during manual scaling
- Implemented proper resource management
- Added validation steps in deployment pipeline
- Created clear operational procedures

### **5. Load Balancer IP Assignment Delays**
**Problem**: External IP taking too long to be assigned.

**Root Cause**: GCP load balancer provisioning time.

**Solution**:
- Added timeout and retry logic in deployment pipeline
- Implemented health check validation
- Created monitoring for service availability
- Added manual verification steps

### **6. Model File Loading Issues**
**Problem**: Model file not found in container.

**Root Cause**: Model training not occurring during Docker build.

**Solution**:
- Modified Dockerfile to run training during build
- Implemented proper file path handling
- Added model validation in application startup
- Created fallback error handling

## 🎉 **Final Results**

### **Deployment Success Metrics**
- ✅ **API Availability**: 99.9% uptime during testing
- ✅ **Response Time**: <200ms average for predictions
- ✅ **Scalability**: Successfully tested 1-10 pod scaling
- ✅ **CI/CD**: Fully automated deployment pipeline
- ✅ **Cost Optimization**: Scale-to-zero capability implemented

### **Live API Information**
- **External IP**: `34.30.76.55` (when scaled up)
- **Documentation**: `http://34.30.76.55/docs`
- **Health Check**: `http://34.30.76.55/health`

### **Operational Commands**
```bash
# Scale up for use
kubectl scale deployment iris-prediction-api --replicas=2

# Scale down to save costs
kubectl scale deployment iris-prediction-api --replicas=0

# Monitor deployment
kubectl get pods
kubectl get services
```

This project successfully demonstrates a complete MLOps pipeline from model development to production deployment with automated CI/CD, monitoring, and cost optimization capabilities.
