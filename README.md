# Adversarial Robustness of Tree-Based Intrusion Detection Systems Under Feature-Constrained Evasion Attacks

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dataset: CIC-IoT2023](https://img.shields.io/badge/Dataset-CIC--IoT2023-green.svg)](https://www.unb.ca/cic/datasets/iotdataset-2023.html)

Official implementation and reproducibility artifacts for:  
**"Adversarial Robustness of Tree-Based Intrusion Detection Systems Under Feature-Constrained Evasion Attacks"**  
*Dhananjay Kadge and Monali Maid*  
Department of Computer Science and Engineering, MGM University, Chhatrapati Sambhajinagar 431001, Maharashtra, India.

---

## Overview

Tree ensemble classifiers (Random Forest, XGBoost, LightGBM) serve as primary detection engines in operational Network Intrusion Detection Systems (NIDS) for IoT deployments due to their sub-millisecond inference and high clean benchmark accuracy (>99%). However, evaluating their security under unconstrained gradient perturbations fails to reflect realistic operational conditions. 

Unlike continuous image domains, network flow evasion must preserve transport-layer syntax, discrete protocol flags, and socket validity to prevent packets from being dropped by intermediate firewalls and middleboxes. This repository provides the complete experimental suite evaluating tree-based and deep neural classifiers across **701,962 clean flow records** and **31 attack classes** from the **CIC-IoT2023** benchmark under strict protocol-preserving constraints.

---

## Key Empirical Findings

1. **Non-Linear Phase Transition:** Tree ensembles do not exhibit gradual margin degradation. XGBoost maintains an evasion rate of 2.40% until a critical perturbation budget of $\varepsilon = 4.69$, where attack success abruptly surges to 63.20% as perturbations breach root-level decision splits on packet count statistics.
2. **Architectural Robustness Disparity:** Continuous neural decision surfaces prove markedly more brittle on tabular traffic: Deep MLP suffers 100.00% attack success (0.00% residual recall), whereas XGBoost retains a 44.00% detection margin under identical constraints.
3. **Random Forest Transfer Disparity:** Random Forest demonstrates an asymmetric vulnerability profile, neutralizing 98.00% of surrogate-transferred adversarial flows (2.00% ASR) while failing under direct query access (99.00% ASR).
4. **Gaussian Subspace Smoothing (GSS):** Standard adversarial retraining on tree models causes severe leaf-level memorization. GSS injects continuous stochastic perturbations into mutable feature subspaces during training, reducing XGBoost evasion from 41.67% to 1.33% while preserving clean detection recall at 99.33%.

---

## Summary of Core Results

### 1. Baseline Performance on Clean Telemetry

| Architecture | Clean Accuracy | Macro F1 | ROC-AUC | Inference Latency |
| :--- | :---: | :---: | :---: | :---: |
| Random Forest | 99.22% | 99.60% | 0.9981 | 10.18 s |
| **XGBoost** | **99.25%** | **99.62%** | **0.9981** | **3.41 s** |
| LightGBM | 99.24% | 99.61% | 0.9980 | **1.99 s** |
| Deep MLP (Neural) | 99.02% | 89.38% | 0.9969 | 16.42 s |

### 2. Defense Benchmark Under Adaptive Attack ($\varepsilon = 5.0$)

| Model Configuration | Defense Mechanism | Clean Recall | Adversarial Recall | Evasion ASR |
| :--- | :--- | :---: | :---: | :---: |
| XGBoost (Baseline) | None | 99.33% | 58.33% | 41.67% |
| **XGBoost (AT + GSS)** | **Gaussian Subspace Smoothing** | **99.33%** | **98.67%** | **1.33%** |
| Deep MLP (Baseline) | None | 98.00% | 0.00% | 100.00% |
| Deep MLP (AT + GSS) | Gaussian Subspace Smoothing | 98.00% | 55.00% | 45.00% |

---

## Repository Structure

```
.
├── main.py                     # Command-line entry point for pipeline execution
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Environment and package specification
├── data/
│   └── processed/              # Preprocessed Parquet partitions and scalers
├── src/                        # Experimental analysis modules
│   ├── config.py               # Paths, feature definitions, and global constants
│   ├── data_loader.py          # Data ingestion and train/test partition routine
│   ├── train_baseline.py       # Baseline classifier training (RF, XGB, LGBM)
│   ├── train_mlp.py            # Deep MLP baseline architecture and calibration
│   ├── shap_analysis.py        # SHAP feature importance attribution
│   ├── genetic_evasion.py      # Feature-constrained genetic algorithm evasion engine
│   ├── eval_evasion.py         # Epsilon sensitivity, transferability, and per-class sweeps
│   ├── eval_cross_architecture.py # Tree vs. Neural comparative robustness evaluation
│   ├── adversarial_training.py # Adversarial training with Gaussian Subspace Smoothing
│   ├── eval_defense.py         # Adaptive robustness benchmarks on defended models
│   ├── generate_final_figures.py # Master figure generation (Figures 1-22)
│   └── generate_excel_summary.py # Consolidated experimental spreadsheet exporter
├── paper/
│   ├── main.tex                # LaTeX source of the preprint
│   ├── manuscript.pdf          # Full-length manuscript preprint
│   └── references.bib          # BibTeX bibliography
└── results/
    ├── figures/                # High-resolution figures (22 PNGs)
    └── models/                 # Pretrained and defended serialized models (.joblib)
```

---

## Setup & Reproduction

### 1. Environment Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/DHANANJAY-2006/adversarial-iot-ids-robustness.git
cd adversarial-iot-ids-robustness
pip install -r requirements.txt
```

### 2. Direct Reproduction of Paper Tables
To verify and reproduce individual tables from the paper directly, standalone scripts are provided:

```bash
# Table 2: Clean Baseline Classification Performance (N = 140,393 holdout)
python reproduce_baseline.py

# Table 4: Evasion Performance Under Feature-Constrained GA Attack (ε = 5.0)
python run_ga_attack.py

# Table 5: Perturbation Sensitivity Sweep (ε ∈ [0.05, 5.00])
python run_epsilon_sweep.py

# Table 7: Mutable Feature Subspace Ablation (k ∈ [2, 14])
python run_feature_ablation.py

# Table 8: Operational Attack Validity & Functional Preservation Audit
python audit_functional_preservation.py

# Table 10: Gaussian Subspace Smoothing Defense Evaluation (AT + GSS vs. Standard-AT)
python train_gss_defense.py

# Appendix Table 12: Comprehensive 31-Class Robustness and Validity Telemetry
python generate_per_class_table.py
```

### 3. Execution Pipeline (From Source)
Use `main.py` to invoke individual experimental modules:

```bash
# 1. Train clean baseline classifiers
python main.py --module baseline
python main.py --module mlp

# 2. Compute SHAP feature importance
python main.py --module shap

# 3. Execute feature-constrained genetic evasion attack
python main.py --module evasion
python main.py --module eval-evasion

# 4. Compare tree vs. deep neural robustness
python main.py --module eval-cross

# 5. Run adversarial training with Gaussian Subspace Smoothing (GSS)
python main.py --module defense
python main.py --module eval-defense

# 6. Generate all 22 publication figures
python main.py --module figures
```

---

## Dataset Access

The raw benchmark is sourced from the Canadian Institute for Cybersecurity (CIC):
- **CIC-IoT2023:** [https://www.unb.ca/cic/datasets/iotdataset-2023.html](https://www.unb.ca/cic/datasets/iotdataset-2023.html)
- The processed feature partitions used in our experiments are hosted under `data/processed/` for direct reproducibility.

---

## Citation

```bibtex
@article{kadge2026adversarial,
  title={Adversarial Robustness of Tree-Based Intrusion Detection Systems Under Feature-Constrained Evasion Attacks},
  author={Kadge, Dhananjay and Maid, Monali},
  journal={Manuscript under review},
  year={2026}
}
```

---

## Responsible Disclosure & Dual-Use Statement

All adversarial attack methodologies detailed in this repository were evaluated strictly offline on pre-recorded benchmark captures from the CIC-IoT2023 dataset; no live operational networks or physical IoT endpoints were targeted. The genetic algorithm generates statistical flow summaries rather than raw, weaponized packet payloads or network exploits. Code and models are released openly for defensive auditing purposes: enabling security practitioners and SOC teams to evaluate tree-based NIDS pipelines against feature-constrained evasion and reproduce the Gaussian Subspace Smoothing hardening defense. This repository contains no automated scanning or exploit delivery modules.

---

## Hardware Telemetry & Deterministic Seeds

- **Hardware:** Intel Core i9-13900K CPU (24 cores, 32 threads, up to 5.8 GHz), 64 GB DDR5-5600 RAM, NVIDIA GeForce RTX 4090 GPU (24 GB GDDR6X).
- **OS & Environment:** Ubuntu 22.04 LTS (Linux kernel 5.15), Python 3.10.12.
- **Key Dependencies:** XGBoost 1.7.6, LightGBM 4.1.0, scikit-learn 1.3.0, PyTorch 2.0.1+cu118, SHAP 0.42.1, NumPy 1.24.3, Pandas 2.0.3, SciPy 1.11.1.
- **Deterministic Evaluation Seeds:** $\mathcal{S} = \{42, 101, 202, 303, 404\}$.

---

## License & Inquiries
- **License:** Released under the [MIT License](LICENSE).
- **Corresponding Author:** Dhananjay Kadge (`kadge.dhananjay.in@gmail.com`)
- **Institution:** Department of Computer Science and Engineering, School of Engineering and Technology, MGM University, Chhatrapati Sambhajinagar 431001, Maharashtra, India.
