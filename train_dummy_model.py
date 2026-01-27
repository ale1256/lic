import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'diagnosis', 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'pd_classifier.pkl')

def force_train_model():
    print("🛠️  Initializing Dummy Model Generator...")
    
    # 1. Create the directory if it doesn't exist
    if not os.path.exists(MODEL_DIR):
        print(f"   -> Creating directory: {MODEL_DIR}")
        os.makedirs(MODEL_DIR)

    # 2. Generate Fake Training Data
    # The ml_logic.py expects exactly 741 features (upper triangle of correlation matrix)
    print("   -> Generating synthetic training data (741 features)...")
    n_samples = 50
    n_features = 741
    
    X = np.random.rand(n_samples, n_features)
    y = np.random.randint(0, 2, n_samples) # 0 = Control, 1 = Parkinson's

    # 3. Train the Classifier
    print("   -> Training LogisticRegression model...")
    model = LogisticRegression()
    model.fit(X, y)

    # 4. Save the model
    joblib.dump(model, MODEL_PATH)
    print(f"✅ SUCCESS: Model saved at: {MODEL_PATH}")
    print("   -> The confidence score should now work.")

if __name__ == "__main__":
    force_train_model()