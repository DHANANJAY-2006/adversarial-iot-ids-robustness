import os
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt

from config import DATA_PROCESSED_DIR, MODELS_DIR, FIGURES_DIR

def run_shap_analysis():
    try:
        X_test = pd.read_parquet(os.path.join(DATA_PROCESSED_DIR, "X_test.parquet"))
        model = joblib.load(os.path.join(MODELS_DIR, "XGBoost_baseline.joblib"))
    except FileNotFoundError:
        print("[ERROR] Test data or trained XGBoost model not found.")
        return

    print("Computing SHAP values on test sample...")
    X_sample = X_test.sample(n=min(1000, len(X_test)), random_state=42)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})
    plt.figure(figsize=(10, 7))
    shap.summary_plot(shap_values, X_sample, show=False, max_display=12)
    plt.title("SHAP Value Distribution: Feature Impact on Evasion Detection",
              fontsize=14, fontweight='bold', pad=15)

    output_path = os.path.join(FIGURES_DIR, "shap_beeswarm_publication.png")
    plt.savefig(output_path, dpi=600, bbox_inches='tight')
    plt.close()
    print(f"[INFO] Saved SHAP summary plot: {output_path}")

if __name__ == "__main__":
    run_shap_analysis()
