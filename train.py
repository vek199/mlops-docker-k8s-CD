# train.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


def train_iris_model():
    """Train a logistic regression model on the Iris dataset and save it."""
    print("Training Iris classification model...")
    
    # Load the dataset
    df = pd.read_csv('iris.csv')
    
    # Define features (X) and target (y)
    feature_columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
    target_column = 'species'
    
    X = df[feature_columns]
    y = df[target_column]
    
    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )
    
    # Initialize and train the model
    model = LogisticRegression(max_iter=200, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Save the model using joblib
    model_filename = 'model.joblib'
    joblib.dump(model, model_filename)
    print(f"Model saved as {model_filename}")
    
    return model, accuracy


if __name__ == '__main__':
    train_iris_model()