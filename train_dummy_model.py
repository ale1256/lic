import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'diagnosis', 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'pd_classifier.pkl')

def force_train_model():
    print("🛠️  Initializing Dummy Model Generator...")
    
    if not os.path.exists(MODEL_DIR):
        print(f"   -> Creating directory: {MODEL_DIR}")
        os.makedirs(MODEL_DIR)


    print("   -> Generating synthetic training data (741 features)...")
    n_samples = 50
    n_features = 741
    
    X = np.random.rand(n_samples, n_features)
    y = np.random.randint(0, 2, n_samples) 

    print("   -> Training LogisticRegression model...")
    model = LogisticRegression()
    model.fit(X, y)


    joblib.dump(model, MODEL_PATH)
    print(f" SUCCESS: Model saved at: {MODEL_PATH}")
    print("   -> The confidence score should now work.")

if __name__ == "__main__":
    force_train_model()