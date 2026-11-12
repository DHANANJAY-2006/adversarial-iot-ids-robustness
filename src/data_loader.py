import os
import glob
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

from config import (
    DATA_RAW_DIR, DATA_PROCESSED_DIR,
    BENIGN_LABEL, TEST_SIZE, RANDOM_SEED
)

def load_and_preprocess():
    csv_files = glob.glob(os.path.join(DATA_RAW_DIR, "*.csv"))
    if not csv_files:
        print(f"[ERROR] No CSV files found in {DATA_RAW_DIR}")
        return None

    print(f"Loading {len(csv_files)} CSV files...")
    df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
    df.columns = df.columns.str.strip()
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    target_col = None
    for col in df.columns:
        if col.lower() in ['label', 'attack', 'class']:
            target_col = col
            break

    if not target_col:
        print("[ERROR] Target column not found.")
        return None

    benign_str = BENIGN_LABEL
    for u in df[target_col].unique():
        if 'benign' in str(u).lower() or 'normal' in str(u).lower():
            benign_str = u
            break

    df['Binary_Label'] = df[target_col].apply(lambda x: 0 if x == benign_str else 1)
    df['Original_Label'] = df[target_col].astype(str)

    X = df.drop(columns=[target_col, 'Binary_Label', 'Original_Label'])
    y_binary = df['Binary_Label']
    y_original = df['Original_Label']

    X = X.select_dtypes(include=[np.number])

    X_train, X_test, y_train, y_test, y_orig_train, y_orig_test = train_test_split(
        X, y_binary, y_original,
        test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y_binary
    )

    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

    joblib.dump(scaler, os.path.join(DATA_PROCESSED_DIR, "scaler.joblib"))

    X_train_scaled.to_parquet(os.path.join(DATA_PROCESSED_DIR, "X_train.parquet"))
    X_test_scaled.to_parquet(os.path.join(DATA_PROCESSED_DIR, "X_test.parquet"))
    y_train.to_frame().to_parquet(os.path.join(DATA_PROCESSED_DIR, "y_train.parquet"))
    y_test.to_frame().to_parquet(os.path.join(DATA_PROCESSED_DIR, "y_test.parquet"))
    y_orig_test.to_frame(name="Original_Label").to_parquet(
        os.path.join(DATA_PROCESSED_DIR, "y_test_original_labels.parquet")
    )

    print(f"[INFO] Processed dataset saved to {DATA_PROCESSED_DIR}")
    print(f"[INFO] Train samples: {len(X_train_scaled):,}, Test samples: {len(X_test_scaled):,}")
    return X_train_scaled, X_test_scaled, y_train, y_test

if __name__ == "__main__":
    load_and_preprocess()
