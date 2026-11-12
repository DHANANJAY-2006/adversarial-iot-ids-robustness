import os
from time import time
import warnings
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

warnings.filterwarnings('ignore')

from config import DATA_PROCESSED_DIR, MODELS_DIR, FIGURES_DIR

NUM_ATTACKS_TO_SIMULATE = 2000
POPULATION_SIZE = 300
GENERATIONS = 100
EPSILON = 5.0

def evaluate_packet(original_packet, mutable_indices, model):
    population = np.zeros((POPULATION_SIZE, len(original_packet)))
    for p in range(POPULATION_SIZE):
        noise = np.random.uniform(-EPSILON, EPSILON, size=len(mutable_indices))
        population[p, mutable_indices] = noise

    best_adv_packet = None
    evaded = False
    best_confidence = 1.0
    best_l2_dist = float('inf')

    for gen in range(GENERATIONS):
        candidates = original_packet + population
        probs = model.predict_proba(candidates)[:, 1]

        l2_distances = np.linalg.norm(population[:, mutable_indices], axis=1)
        fitness = probs + (0.05 * l2_distances)

        if np.any(probs < 0.5):
            evasion_indices = np.where(probs < 0.5)[0]
            stealthiest_idx = evasion_indices[np.argmin(l2_distances[evasion_indices])]
            best_adv_packet = candidates[stealthiest_idx]
            evaded = True
            best_confidence = probs[stealthiest_idx]
            best_l2_dist = l2_distances[stealthiest_idx]
            break

        best_indices = np.argsort(fitness)[:POPULATION_SIZE // 2]
        survivors = population[best_indices]

        next_gen = np.zeros_like(population)
        next_gen[:len(survivors)] = survivors

        for j in range(len(survivors), POPULATION_SIZE):
            parent1 = survivors[np.random.randint(len(survivors))]
            parent2 = survivors[np.random.randint(len(survivors))]
            child = np.where(np.random.rand(len(original_packet)) > 0.5, parent1, parent2)
            mutation_mask = np.random.rand(len(mutable_indices)) > 0.3
            noise = np.random.normal(0, EPSILON / 3, size=len(mutable_indices)) * mutation_mask
            child[mutable_indices] = np.clip(child[mutable_indices] + noise, -EPSILON, EPSILON)
            next_gen[j] = child

        population = next_gen

        if np.min(probs) < best_confidence:
            best_confidence = np.min(probs)
            best_idx = np.argmin(probs)
            best_adv_packet = candidates[best_idx]
            best_l2_dist = l2_distances[best_idx]

    return evaded, best_adv_packet, best_confidence, best_l2_dist

def run_evasion_attack():
    try:
        X_test = pd.read_parquet(os.path.join(DATA_PROCESSED_DIR, "X_test.parquet"))
        y_test = pd.read_parquet(os.path.join(DATA_PROCESSED_DIR, "y_test.parquet")).squeeze()
        model = joblib.load(os.path.join(MODELS_DIR, "XGBoost_baseline.joblib"))
    except FileNotFoundError:
        print("[ERROR] Missing models or preprocessed dataset.")
        return

    importances = model.feature_importances_
    continuous_features = [
        (i, col, importances[i]) for i, col in enumerate(X_test.columns)
        if len(X_test[col].unique()) > 15
    ]
    continuous_features.sort(key=lambda x: x[2], reverse=True)
    mutable_indices = [x[0] for x in continuous_features[:15]]

    y_pred_initial = model.predict(X_test)
    true_positive_mask = (y_test.values == 1) & (y_pred_initial == 1)
    X_attacks = X_test[true_positive_mask].values

    attacks_to_run = min(NUM_ATTACKS_TO_SIMULATE, len(X_attacks))
    np.random.seed(42)
    X_sample = X_attacks[np.random.choice(len(X_attacks), attacks_to_run, replace=False)]

    print(f"[INFO] Executing multi-objective genetic evasion attack on {attacks_to_run} flows...")
    t0 = time()
    results = Parallel(n_jobs=-1)(
        delayed(evaluate_packet)(packet, mutable_indices, model) for packet in X_sample
    )
    attack_time = time() - t0

    successful_evasions = 0
    adversarial_examples = []
    plot_confidences = []
    plot_distances = []

    for evaded, adv_packet, conf, dist in results:
        adversarial_examples.append(adv_packet)
        plot_confidences.append(conf)
        if evaded:
            successful_evasions += 1
            plot_distances.append(dist)

    asr = (successful_evasions / attacks_to_run) * 100

    plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.hist(plot_confidences, bins=30, color='#8b0000', alpha=0.7, edgecolor='black')
    ax1.axvline(x=0.5, color='black', linestyle='--', label='Decision Threshold (0.5)')
    ax1.set_title("Post-Attack Model Confidence Distribution", fontweight='bold')
    ax1.set_xlabel("Malicious Probability Score")
    ax1.set_ylabel("Count")
    ax1.legend()

    if plot_distances:
        evasion_confs = [c for c, e in zip(plot_confidences, [r[0] for r in results]) if e]
        sc = ax2.scatter(plot_distances, evasion_confs, alpha=0.6, c=plot_distances, cmap='viridis')
        ax2.set_title("Evasion Stealth Analysis (L2 Perturbation)", fontweight='bold')
        ax2.set_xlabel("L2 Distance")
        ax2.set_ylabel("Model Confidence")
        fig.colorbar(sc, ax=ax2, label="L2 Norm")

    plt.tight_layout()
    graph_path = os.path.join(FIGURES_DIR, "adversarial_stealth_analysis.png")
    plt.savefig(graph_path, dpi=600, bbox_inches='tight')
    plt.close()

    X_adv_df = pd.DataFrame(adversarial_examples, columns=X_test.columns)
    adv_path = os.path.join(DATA_PROCESSED_DIR, "X_adversarial_sample.parquet")
    X_adv_df.to_parquet(adv_path)

    print(f"\n[INFO] Attack Evaluation Summary:")
    print(f"  Samples attacked: {attacks_to_run:,}")
    print(f"  Attack Success Rate (ASR): {asr:.2f}%")
    print(f"  Execution time: {attack_time / 60:.1f} minutes")
    print(f"  Adversarial dataset saved to: {adv_path}")

if __name__ == "__main__":
    run_evasion_attack()
