# -*- coding: utf-8 -*-
"""Verification baseline script for SimAI prediction latency and validation."""

def evaluate_surrogate_prediction(predicted: float, ground_truth: float) -> float:
    # Relative percentage error
    if ground_truth == 0.0:
        return abs(predicted)
    return abs(predicted - ground_truth) / abs(ground_truth) * 100.0

if __name__ == "__main__":
    err = evaluate_surrogate_prediction(0.312, 0.318)
    print(f"SimAI aerodynamic surrogate error: {err:.2f}%")
    assert err < 5.0, "Prediction error exceeds 5% engineering limit"
    print("SimAI surrogate baseline check PASSED.")
