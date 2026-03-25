"""
Script to generate and train a sample ML model for CKD prediction
This creates a RandomForest model and saves it as model.pkl
"""

import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import os

def create_sample_dataset(n_samples=200):
    """
    Create a sample dataset with realistic medical values for training
    """
    np.random.seed(42)
    
    # Generate realistic medical data
    data = {
        'bp': np.random.uniform(80, 180, n_samples),                    # Blood pressure
        'sg': np.random.uniform(1.005, 1.030, n_samples),               # Specific gravity
        'al': np.random.choice([0, 1, 2, 3, 4, 5], n_samples),         # Albumin levels
        'su': np.random.choice([0, 1, 2, 3, 4, 5], n_samples),         # Sugar levels
        'rbc': np.random.choice([0, 1], n_samples),                     # RBC (0=abnormal, 1=normal)
        'pc': np.random.choice([0, 1], n_samples),                      # Pus cell
        'pcc': np.random.choice([0, 1], n_samples),                     # Pus cell clumps
        'ba': np.random.choice([0, 1], n_samples),                      # Bacteria
        'bgr': np.random.uniform(70, 200, n_samples),                   # Blood glucose random
        'bu': np.random.uniform(15, 100, n_samples),                    # Blood urea
        'sc': np.random.uniform(0.5, 5.0, n_samples),                   # Serum creatinine
        'sod': np.random.uniform(120, 160, n_samples),                  # Sodium
        'pot': np.random.uniform(2.0, 8.0, n_samples),                  # Potassium
        'hemo': np.random.uniform(7.0, 17.0, n_samples),                # Hemoglobin
        'pcv': np.random.uniform(20, 55, n_samples),                    # Packed cell volume
        'wc': np.random.uniform(3.0, 12.0, n_samples),                  # White blood cell count
        'rc': np.random.uniform(3.5, 6.0, n_samples),                   # Red blood cell count
        'htn': np.random.choice([0, 1], n_samples),                     # Hypertension (yes/no)
        'dm': np.random.choice([0, 1], n_samples),                      # Diabetes (yes/no)
        'cad': np.random.choice([0, 1], n_samples),                     # Coronary artery disease
        'appet': np.random.choice([0, 1], n_samples),                   # Appetite (0=poor, 1=good)
        'pe': np.random.choice([0, 1], n_samples),                      # Pedal edema
        'ane': np.random.choice([0, 1], n_samples),                     # Anemia
    }
    
    df = pd.DataFrame(data)
    
    # Generate target variable (CKD: 1 = High Risk, 0 = Low Risk)
    # Higher values of certain features increase CKD risk
    risk_score = (
        (df['sc'] / 5.0) * 0.2 +           # Serum creatinine
        (df['bu'] / 100.0) * 0.15 +        # Blood urea
        (df['bp'] / 180.0) * 0.15 +        # Blood pressure
        (df['htn'] * 0.15) +                # Hypertension
        (df['dm'] * 0.15) +                 # Diabetes
        ((1 - df['hemo'] / 17.0) * 0.1) +  # Low hemoglobin
        (df['cad'] * 0.1)                   # Coronary artery disease
    )
    
    # Convert to binary classification
    y = (risk_score > 0.5).astype(int)
    
    # Add some randomness
    random_flip = np.random.choice([0, 1], n_samples, p=[0.85, 0.15])
    y = np.abs(y - random_flip)
    
    return df, y

def train_model(X, y):
    """
    Train a RandomForest classifier
    """
    print("🤖 Training RandomForest Model...")
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X, y)
    print("✓ Model trained successfully!")
    
    return model

def test_model(model, X_test, y_test):
    """
    Test the model and print accuracy
    """
    print("\n📊 Testing Model...")
    accuracy = model.score(X_test, y_test)
    print(f"✓ Model Accuracy: {accuracy * 100:.2f}%")
    
    # Test with sample data
    sample_data = X_test.iloc[0:3]
    predictions = model.predict(sample_data)
    probabilities = model.predict_proba(sample_data)
    
    print("\n🧪 Sample Predictions:")
    for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
        risk_level = "High Risk" if pred == 1 else "Low Risk"
        confidence = max(prob) * 100
        print(f"   Sample {i+1}: {risk_level} (Confidence: {confidence:.2f}%)")

def save_model(model, filepath):
    """
    Save the model to a pickle file
    """
    print(f"\n💾 Saving model to {filepath}...")
    
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"✓ Model saved successfully!")
    
    # Verify file was saved
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath) / 1024  # KB
        print(f"   File size: {file_size:.2f} KB")
    
    return True

def load_and_verify_model(filepath):
    """
    Load the model and verify it works
    """
    print(f"\n🔍 Verifying saved model...")
    
    try:
        with open(filepath, 'rb') as f:
            loaded_model = pickle.load(f)
        
        print("✓ Model loaded successfully!")
        print(f"   Model type: {type(loaded_model).__name__}")
        print(f"   Features expected: {loaded_model.n_features_in_}")
        
        return loaded_model
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return None

def main():
    """
    Main function to orchestrate model creation
    """
    print("=" * 60)
    print("🏥 CKD PREDICTION MODEL CREATION")
    print("=" * 60)
    
    # Create dataset
    print("\n📚 Creating sample dataset...")
    X, y = create_sample_dataset(n_samples=300)
    print(f"✓ Dataset created: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"   Class distribution: {np.sum(y == 0)} Low Risk, {np.sum(y == 1)} High Risk")
    
    # Split into train and test
    train_size = int(0.8 * len(X))
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Train model
    model = train_model(X_train, y_train)
    
    # Test model
    test_model(model, X_test, y_test)
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    save_model(model, model_path)
    
    # Verify
    loaded_model = load_and_verify_model(model_path)
    
    print("\n" + "=" * 60)
    print("✅ MODEL CREATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nModel ready at: {model_path}")
    print("\nYou can now run: python app.py")
    print("Then visit: http://localhost:5000")

if __name__ == '__main__':
    main()
