import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import os
from simulate_uav import build_grid_graph, apply_no_fly_zones

G, pos = build_grid_graph(rows=12, cols=8)



# =========================
# 1️⃣ Load dataset
# =========================
dataset_path = "results/dataset_flat.csv"  # change if needed
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"{dataset_path} not found. Please generate dataset first.")

df = pd.read_csv(dataset_path)

df.rename(columns={
    "cur_x": "x",
    "cur_y": "y",
    "nb0_is_nofly": "up_blocked",
    "nb1_is_nofly": "down_blocked",
    "nb2_is_nofly": "left_blocked",
    "nb3_is_nofly": "right_blocked"

}, inplace=True)


# =========================
# 2️⃣ Feature Engineering
# =========================
# Ensure your dataset has columns for UAV current pos (x,y), goal pos (goal_x, goal_y),
# speed, and info about blocked neighbors (up, down, left, right)
# Also, the dataset must have 'next_action' (0=up,1=down,2=left,3=right)

# Distance to goal
df["dist_to_goal"] = np.sqrt((df["goal_x"] - df["x"])**2 + (df["goal_y"] - df["y"])**2)

# Feature matrix
feature_cols = ["x", "y", "goal_x", "goal_y", "speed", "dist_to_goal",
                "up_blocked", "down_blocked", "left_blocked", "right_blocked"]

def add_blocked_flags(df, positions, G):
    """Add up/down/left/right blocked flags for each UAV position."""
    # Assume positions are (x, y)
    df['up_blocked'] = df.apply(lambda row: (row['x'], row['y']+1) not in positions or (row['x'], row['y']+1) in NOFLY_NODES, axis=1)
    df['down_blocked'] = df.apply(lambda row: (row['x'], row['y']-1) not in positions or (row['x'], row['y']-1) in NOFLY_NODES, axis=1)
    df['left_blocked'] = df.apply(lambda row: (row['x']-1, row['y']) not in positions or (row['x']-1, row['y']) in NOFLY_NODES, axis=1)
    df['right_blocked'] = df.apply(lambda row: (row['x']+1, row['y']) not in positions or (row['x']+1, row['y']) in NOFLY_NODES, axis=1)
    return df

df = add_blocked_flags(df, positions=pos, G=G)  # pos and G from your grid

# Check all columns exist
for col in feature_cols + ["next_action"]:
    if col not in df.columns:
        raise ValueError(f"Column '{col}' missing in dataset. Please preprocess dataset accordingly.")

X = df[feature_cols]
y = df["next_action"]

# =========================
# 3️⃣ Split train/test
# =========================
le = LabelEncoder()
y=le.fit_transform(df["next_action"])

joblib.dump(le,"results/label_encoder.pkl")
x=df.drop(columns=["next_action","label"],errors="ignore")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# =========================
# 4️⃣ Train XGBoost Classifier
# =========================
model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softmax",
    num_class=4,
    use_label_encoder=False,
    eval_metric="mlogloss",
    random_state=42
)

model.fit(X_train, y_train)

# =========================
# 5️⃣ Evaluate
# =========================
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"✅ XGBoost model accuracy: {acc*100:.2f}%")

# =========================
# 6️⃣ Save model
# =========================
joblib.dump(model, os.path.join("results","uav_xgb_model.pkl"))
joblib.dump(le, os.path.join("results", "label_encoder.pkl"))
print(f"✅ Model saved")
