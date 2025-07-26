# MLOps Pipeline - Iris Species Prediction API

A complete MLOps pipeline for deploying an Iris species prediction model using FastAPI, Docker, Kubernetes, and Google Cloud Platform with CI/CD automation.

## 🏗️ Architecture

- **ML Model**: Logistic Regression (scikit-learn) trained on Iris dataset
- **API Framework**: FastAPI with async endpoints
- **Containerization**: Docker with multi-stage build
- **Orchestration**: Kubernetes on Google Kubernetes Engine (GKE)
- **CI/CD**: GitHub Actions with automated deployment
- **Artifact Storage**: Google Artifact Registry
- **Load Testing**: Locust for performance testing

## 📁 Project Structure

```
mlops-docker-k8s-CD/
├── main.py                 # FastAPI application
├── train.py               # Model training script
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── locustfile.py         # Load testing configuration
├── iris.csv              # Training dataset
├── kubernetes/           # K8s manifests
│   ├── deployment.yml    # Application deployment
│   ├── service.yml       # Load balancer service
│   └── hpa.yml          # Horizontal Pod Autoscaler
└── .github/workflows/
    └── cd-pipeline.yml   # CI/CD pipeline

```

## 🚀 API Endpoints

- `GET /` - Welcome message and API information
- `GET /health` - Health check endpoint
- `POST /predict` - Predict Iris species from features
- `GET /docs` - Interactive Swagger documentation

## 🛠️ Setup Guide

### Prerequisites

1. **Google Cloud Platform Account**
2. **GitHub Repository**
3. **Local Development Environment**:
   - Python 3.10+
   - Docker
   - kubectl
   - gcloud CLI

### 1. GCP Setup

#### Create GCP Project
```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID
```

#### Enable Required APIs
```bash
gcloud services enable \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com
```

#### Create Artifact Registry Repository
```bash
gcloud artifacts repositories create iris-prediction-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Iris prediction API images"
```

#### Create GKE Cluster
```bash
gcloud container clusters create iris-prediction-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5
```

#### Create Service Account for GitHub Actions
```bash
# Create service account
gcloud iam service-accounts create github-actions-sa \
  --description="Service account for GitHub Actions" \
  --display-name="GitHub Actions SA"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Create and download service account key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com
```

### 2. GitHub Repository Setup

#### Set Repository Secrets
In your GitHub repository, go to Settings > Secrets and variables > Actions, and add:

- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Contents of the `github-actions-key.json` file

### 3. Local Development

#### Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Train Model Locally
```bash
python train.py
```

#### Run API Locally
```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

#### Test with Sample Request
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

### 4. Docker Testing

#### Build and Run Container
```bash
# Build image
docker build -t iris-prediction-api .

# Run container
docker run -p 8000:8000 iris-prediction-api

# Test health endpoint
curl http://localhost:8000/health
```

### 5. Deploy to Production

#### Manual Deployment
```bash
# Configure kubectl
gcloud container clusters get-credentials iris-prediction-cluster --zone=us-central1-a

# Apply Kubernetes manifests
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods
kubectl get services
```

#### Automated Deployment
Push code to the `main` branch to trigger the CI/CD pipeline:

```bash
git add .
git commit -m "Deploy iris prediction API"
git push origin main
```

## 🧪 Testing

### Load Testing with Locust
```bash
# Install locust
pip install locust

# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Prediction test
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 6.3,
    "sepal_width": 2.8,
    "petal_length": 5.1,
    "petal_width": 1.5
  }'
```

## 📊 Monitoring

- **Kubernetes Dashboard**: Monitor pods, services, and resource usage
- **GCP Console**: View cluster health, logs, and metrics
- **Load Balancer**: Get external IP from `kubectl get services`

## 🔧 Configuration

### Environment Variables
- `PORT`: Application port (default: 8000)
- `GCP_PROJECT_ID`: Google Cloud project ID

### Kubernetes Resources
- **CPU Request**: 250m (0.25 cores)
- **Memory Request**: 128Mi
- **CPU Limit**: 500m (0.5 cores)
- **Memory Limit**: 256Mi

## 🚨 Troubleshooting

### Common Issues

1. **Model not found**: Ensure `train.py` runs successfully during Docker build
2. **Authentication errors**: Verify GCP service account permissions
3. **Deployment failures**: Check pod logs with `kubectl logs <pod-name>`
4. **Service not accessible**: Verify LoadBalancer external IP with `kubectl get services`

### Useful Commands
```bash
# View pod logs
kubectl logs -l app=iris-prediction-api

# Describe deployment
kubectl describe deployment iris-prediction-api

# Port forward for local testing
kubectl port-forward service/iris-prediction-api-service 8080:80

# Scale deployment
kubectl scale deployment iris-prediction-api --replicas=3
```

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
