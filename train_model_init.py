import os
import joblib
import numpy as np
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
MODEL_DIR = os.path.join('diagnosis', 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'pd_classifier.pkl')
os.makedirs(MODEL_DIR, exist_ok=True)

print("Initializare si antrenare model demonstrativ (SVM)...")

n_features = 741 

print(f"Generare date sintetice ({n_features} features)...")
X_train = np.random.rand(50, n_features)
y_train = np.random.randint(0, 2, 50) 

clf = Pipeline([
    ('scaler', StandardScaler()), 
    ('svc', SVC(kernel='rbf', probability=True, random_state=42)) 
])

clf.fit(X_train, y_train)
joblib.dump(clf, MODEL_PATH)

print(f"✅ Model salvat cu succes la: {MODEL_PATH}")
print(f"   Modelul este gata sa primeasca vectori de dimensiunea {n_features}.")