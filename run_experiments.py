import os
import yaml
import mlflow
from src.train import train

experiments = [
    {"n_estimators": 50, "learning_rate": 0.05, "max_depth": 2},
    {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
    {"n_estimators": 200, "learning_rate": 0.1, "max_depth": 5},
    {"n_estimators": 150, "learning_rate": 0.15, "max_depth": 4},
]

mlflow.set_tracking_uri("sqlite:///mlflow.db")

print("=== Running Training Experiments ===")
results = []
for i, p in enumerate(experiments, 1):
    print(f"\n[Experiment {i}] params: {p}")
    with open("params.yaml", "w") as f:
        yaml.safe_dump(p, f)
    f1 = train(p)
    results.append((p, f1))

best_p, best_f1 = max(results, key=lambda x: x[1])
print(f"\n=== BEST HYPERPARAMETERS ===")
print(f"Params: {best_p}, Best F1: {best_f1:.4f}")

# Save best params to params.yaml
with open("params.yaml", "w") as f:
    yaml.safe_dump(best_p, f)
