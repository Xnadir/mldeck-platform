"""Custom metrics for model evaluation."""
import numpy as np

def mean_absolute_percentage_error(y_true, y_pred) -> float:
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    nonzero = y_true != 0
    return float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100)

def top_k_accuracy(y_true, y_proba, k: int = 3) -> float:
    correct = 0
    for true_label, probs in zip(y_true, y_proba):
        top_k_preds = np.argsort(probs)[-k:]
        if true_label in top_k_preds: correct += 1
    return correct / len(y_true) if y_true else 0.0
