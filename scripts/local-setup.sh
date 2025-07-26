#!/bin/bash

# Local Setup Script for Iris Prediction API
# This script sets up the local development environment

set -e

echo "🚀 Setting up Iris Prediction API locally..."

# Check if Python 3.10+ is available
if ! python3 --version | grep -E "3\.(1[0-9]|[2-9][0-9])" > /dev/null; then
    echo "❌ Python 3.10+ is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Train model
echo "🤖 Training ML model..."
python train.py

# Check if model was created
if [ ! -f "model.joblib" ]; then
    echo "❌ Model training failed!"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run the API: uvicorn main:app --reload"
echo "2. Visit: http://localhost:8000/docs"
echo "3. Test health: curl http://localhost:8000/health"
echo "4. Test prediction:"
echo '   curl -X POST "http://localhost:8000/predict" \'
echo '   -H "Content-Type: application/json" \'
echo '   -d '"'"'{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'"'"
echo ""
echo "🧪 For load testing: locust -f locustfile.py --host=http://localhost:8000" 