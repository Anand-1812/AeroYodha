import os
import pandas as pd
dataset_path = "results/dataset_flat.csv"
if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"{dataset_path} not found. Please generate dataset first.")

df = pd.read_csv(dataset_path)
print(df.columns)
# print(df.head())