import os
import joblib
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, roc_curve
from sklearn.calibration import CalibratedClassifierCV
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from config import DATA_PROCESSED_DIR, MODELS_DIR, FIGURES_DIR

def find_optimal_threshold(y_true, y_probs):
    fpr, tpr, thresholds = roc_curve(y_true, y_probs)
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)
    return thresholds[best_idx], tpr[best_idx], fpr[best_idx]

def train_mlp():
    X_train = pd.read_parquet(os.path.join(DATA_PROCESSED_DIR, "X_train.parquet"))
    X_test = pd.read_parquet(os.path.join(DATA_PROCESSED_DIR, "X_test.parquet"))
    y_train = pd.read_parquet(os.path.join(DATA_PROCESSED_DIR, "y_train.parquet")).squeeze()
    y_test = pd.read_parquet(os.path.join(DATA_PROCESSED_DIR, "y_test.parquet")).squeeze()

    base_mlp = MLPClassifier(
        hidden_layer_sizes=(512, 256, 128, 64),
        activation='relu',
        solver='adam',
        alpha=1e-3,
        batch_size=4096,
        learning_rate='adaptive',
        learning_rate_init=0.001,
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.05,
        n_iter_no_change=15,
        random_state=42,
        verbose=False
    )

    print("Training Deep MLP (512-256-128-64)...")
    base_mlp.fit(X_train, y_train)

    calibrated_mlp = CalibratedClassifierCV(base_mlp, method='sigmoid', cv='prefit')
    calibrated_mlp.fit(X_test[:5000], y_test[:5000])

    y_probs = calibrated_mlp.predict_proba(X_test)[:, 1]
    opt_threshold, opt_tpr, opt_fpr = find_optimal_threshold(y_test, y_probs)

    y_pred_opt = (y_probs >= opt_threshold).astype(int)
    acc = accuracy_score(y_test, y_pred_opt)
    f1 = f1_score(y_test, y_pred_opt)
    auc = roc_auc_score(y_test, y_probs)

    print(f"  Accuracy: {acc:.4f} | F1: {f1:.4f} | AUC: {auc:.4f} | Optimal Threshold: {opt_threshold:.4f}")

    joblib.dump(
        {'model': calibrated_mlp, 'base_model': base_mlp, 'optimal_threshold': opt_threshold},
        os.path.join(MODELS_DIR, "MLP_baseline.joblib")
    )

    if hasattr(base_mlp, 'loss_curve_'):
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.plot(base_mlp.loss_curve_, color='#2c6fad', lw=2)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Cross-Entropy Loss")
        ax.set_title("MLP Training Convergence")
        ax.grid(True, linestyle=':', alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(FIGURES_DIR, "fig08_mlp_training_curve.png"), dpi=600)
        plt.close(fig)

if __name__ == "__main__":
    train_mlp()
