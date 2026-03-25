"""
Sample CKD Model Generator Script
This script creates a sample trained ML model for CKD prediction
You can replace this with your actual trained model
"""

import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os

def create_sample_ckd_model():
    """
    Create a sample Random Forest model for CKD prediction
    This is for demonstration purposes. Replace with your actual trained model.
    """
    
    print("Generating sample CKD prediction model...")
    
    # Define feature names (order matters!)
    feature_names = [
        'age', 'bp', 'sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba',
        'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc',
        'htn', 'dm', 'cad', 'appet', 'pe', 'ane'
    ]
    
    # Generate sample training data
    # In real scenario, this would be your actual CKD dataset
    np.random.seed(42)
    
    n_samples = 400  # Sample size
    X_train = np.random.randn(n_samples, len(feature_names))
    
    # Scale features to realistic ranges
    X_train[:, 0] = np.abs(X_train[:, 0]) * 20 + 30  # age: 30-70
    X_train[:, 1] = np.abs(X_train[:, 1]) * 30 + 70  # bp: 70-130
    X_train[:, 2] = np.abs(X_train[:, 2]) * 0.005 + 1.015  # sg: 1.010-1.025
    X_train[:, 3:5] = np.abs(X_train[:, 3:5]) * 3  # al, su: 0-5
    X_train[:, 5:9] = np.abs(X_train[:, 5:9]) % 2  # rbc, pc, pcc, ba: 0-1
    X_train[:, 9] = np.abs(X_train[:, 9]) * 50 + 80  # bgr: 80-180
    X_train[:, 10] = np.abs(X_train[:, 10]) * 30 + 20  # bu: 20-80
    X_train[:, 11] = np.abs(X_train[:, 11]) * 2 + 0.6  # sc: 0.6-4.6
    X_train[:, 12] = np.abs(X_train[:, 12]) * 20 + 130  # sod: 130-150
    X_train[:, 13] = np.abs(X_train[:, 13]) * 2 + 3  # pot: 3-7
    X_train[:, 14] = np.abs(X_train[:, 14]) * 4 + 10  # hemo: 10-18
    X_train[:, 15] = np.abs(X_train[:, 15]) * 20 + 35  # pcv: 35-55
    X_train[:, 16] = np.abs(X_train[:, 16]) * 4 + 4  # wc: 4-12
    X_train[:, 17] = np.abs(X_train[:, 17]) * 2 + 3  # rc: 3-7
    X_train[:, 18:23] = np.abs(X_train[:, 18:23]) % 2  # binary features
    
    # Generate sample target (CKD prediction: 0 = No CKD, 1 = CKD)
    # Make it somewhat related to features for realism
    y_train = (X_train[:, 11] > 1.5).astype(int)  # Higher creatinine -> more CKD
    # Add some randomness
    y_train[np.random.rand(n_samples) < 0.2] = 1 - y_train[np.random.rand(n_samples) < 0.2]
    
    # Create and train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Add feature names to model for reference
    model.feature_names_ = feature_names
    
    print(f"✓ Model trained on {n_samples} samples")
    print(f"✓ Model accuracy on training data: {model.score(X_train, y_train):.2%}")
    print(f"✓ Features: {len(feature_names)}")
    
    return model

def save_model(model, save_path='app/model.pkl'):
    """Save the trained model to a pickle file"""
    
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"✓ Model saved to: {save_path}")
        return True
    except Exception as e:
        print(f"✗ Error saving model: {e}")
        return False

def load_and_test_model(model_path='app/model.pkl'):
    """Load and test the saved model"""
    
    try:
        with open(model_path, 'rb') as f:
            loaded_model = pickle.load(f)
        
        print(f"✓ Model loaded from: {model_path}")
        
        # Test prediction with sample data
        test_data = np.array([[
            55,      # age
            130,     # bp
            1.020,   # sg
            0,       # al
            0,       # su
            1,       # rbc
            1,       # pc
            0,       # pcc
            0,       # ba
            120,     # bgr
            40,      # bu
            1.2,     # sc
            140,     # sod
            5.0,     # pot
            13,      # hemo
            40,      # pcv
            7,       # wc
            5,       # rc
            1,       # htn
            0,       # dm
            0,       # cad
            1,       # appet (good=1)
            0,       # pe
            0        # ane
        ]])
        
        prediction = loaded_model.predict(test_data)[0]
        probability = loaded_model.predict_proba(test_data)[0]
        
        print(f"✓ Test prediction: {'CKD Present (1)' if prediction == 1 else 'No CKD (0)'}")
        print(f"✓ Prediction probabilities: No CKD={probability[0]:.2%}, CKD={probability[1]:.2%}")
        
        return loaded_model
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print(" CKD PREDICTION MODEL GENERATOR")
    print("=" * 60)
    
    # 1. Create sample model
    print("\n[1] Creating sample model...")
    model = create_sample_ckd_model()
    
    # 2. Save model
    print("\n[2] Saving model...")
    save_model(model)
    
    # 3. Load and test model
    print("\n[3] Loading and testing model...")
    loaded_model = load_and_test_model()
    
    print("\n" + "=" * 60)
    print(" ✓ Setup complete! Model is ready for use.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run Flask app: python app/app.py")
    print("3. Open browser: http://localhost:5000")
    print("\nNote: This is a sample model for demonstration.")
    print("Replace it with your actual trained CKD prediction model.")
    print("=" * 60)
