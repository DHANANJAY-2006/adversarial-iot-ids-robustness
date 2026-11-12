"""
main.py

Execution interface for:
"Adversarial Robustness of Tree-Based Intrusion Detection Systems Under Feature-Constrained Evasion Attacks"
"""

import argparse
import os
import sys
import runpy

MODULES = {
    "baseline": "train_baseline.py",
    "mlp": "train_mlp.py",
    "shap": "shap_analysis.py",
    "evasion": "genetic_evasion.py",
    "eval-evasion": "eval_evasion.py",
    "eval-cross": "eval_cross_architecture.py",
    "defense": "adversarial_training.py",
    "eval-defense": "eval_defense.py",
    "figures": "generate_final_figures.py",
    "summary": "generate_excel_summary.py",
}

def execute(module_name):
    script_name = MODULES.get(module_name)
    if not script_name:
        print(f"[ERROR] Unknown module: {module_name}")
        return
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", script_name)
    print(f"\n--- Running: src/{script_name} ---")
    sys.path.insert(0, os.path.dirname(script_path))
    runpy.run_path(script_path, run_name="__main__")

def main():
    parser = argparse.ArgumentParser(
        description="Adversarial Robustness of Tree-Based IDS: Pipeline Runner"
    )
    parser.add_argument(
        "--module",
        type=str,
        choices=list(MODULES.keys()) + ["all"],
        help="Select module to run"
    )
    args = parser.parse_args()

    if not args.module:
        parser.print_help()
        print("\nAvailable modules:")
        for k, v in MODULES.items():
            print(f"  {k:<14} -> src/{v}")
        return

    if args.module == "all":
        for mod in ["baseline", "mlp", "shap", "evasion", "eval-evasion", "eval-cross", "defense", "eval-defense", "figures"]:
            execute(mod)
    else:
        execute(args.module)

if __name__ == "__main__":
    main()
