import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
df = pd.read_csv(os.path.join(RESULTS_DIR, "uav_dataset.csv"))

# ------------------------------------------------------------
# HANDLE NOFLY_ZONES COLUMN
# Convert list of tuples to string for XGBoost compatibility
# ------------------------------------------------------------
if 'nofly_zones' in df.columns:
    df['nofly_zones'] = df['nofly_zones'].apply(lambda x: str(x))  # now XGBoost sees it as object/string

# ------------------------------------------------------------
# Separate features and target
# ------------------------------------------------------------
X = df.drop(columns=["next_move"])
y = df["next_move"]

# Encode all object columns in X
for col in X.select_dtypes(include='object').columns:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])

# Encode target labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# ------------------------------------------------------------
# TRAIN / TEST SPLIT
# ------------------------------------------------------------
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# ------------------------------------------------------------
# MODEL TRAINING
# ------------------------------------------------------------
model = XGBClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="multi:softmax",
    eval_metric="mlogloss",
    random_state=42
)

print("🚀 Training XGBoost model...")
model.fit(X_train, y_train)

# ------------------------------------------------------------
# EVALUATION
# ------------------------------------------------------------
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {acc * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# ------------------------------------------------------------
# SAVE MODEL + ENCODER
# ------------------------------------------------------------
model_path = os.path.join(RESULTS_DIR, "uav_xgb_ml.pkl")
encoder_path = os.path.join(RESULTS_DIR, "label_encoder.pkl")

joblib.dump(model, model_path)
joblib.dump(label_encoder, encoder_path)

print(f"✅ Model saved to: {model_path}")
print(f"✅ Label encoder saved to: {encoder_path}")
