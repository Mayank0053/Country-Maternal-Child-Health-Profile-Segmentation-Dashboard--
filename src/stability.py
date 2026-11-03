"""
Stability analysis module for Country Maternal-Child Health Profile Segmentation.
Measures clustering stability across bootstrap resampling, random initialization seeds,
and distance metric perturbations using the Adjusted Rand Index (ARI).
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.utils import resample

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def evaluate_initialization_stability(X: np.ndarray, 
                                      k: int = 4, 
                                      n_runs: int = 30) -> Dict[str, Any]:
    """
    Evaluates stability of K-Means clustering across different random seeds.
    Measures pairwise Adjusted Rand Index (ARI) among runs.
    """
    logger.info(f"Evaluating initialization stability for k={k} across {n_runs} runs...")
    models_labels = []
    
    for seed in range(n_runs):
        km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=seed)
        km.fit(X)
        models_labels.append(km.labels_)
        
    pairwise_aris = []
    for i in range(n_runs):
        for j in range(i + 1, n_runs):
            ari = adjusted_rand_score(models_labels[i], models_labels[j])
            pairwise_aris.append(ari)
            
    mean_ari = float(np.mean(pairwise_aris))
    std_ari = float(np.std(pairwise_aris))
    min_ari = float(np.min(pairwise_aris))
    max_ari = float(np.max(pairwise_aris))
    
    logger.info(f"Initialization Stability (k={k}): Mean ARI = {mean_ari:.4f} +/- {std_ari:.4f} (Min: {min_ari:.4f}, Max: {max_ari:.4f})")
    
    return {
        "k": k,
        "n_runs": n_runs,
        "mean_ari": round(mean_ari, 4),
        "std_ari": round(std_ari, 4),
        "min_ari": round(min_ari, 4),
        "max_ari": round(max_ari, 4),
        "pairwise_aris": pairwise_aris
    }

def evaluate_bootstrap_stability(X: np.ndarray, 
                                 k: int = 4, 
                                 n_bootstraps: int = 50, 
                                 sample_ratio: float = 0.85, 
                                 random_state: int = 42) -> Dict[str, Any]:
    """
    Assesses cluster robustness via bootstrap subsampling.
    Trains K-Means on subsample, predicts on full dataset, and compares with baseline ARI.
    """
    logger.info(f"Evaluating bootstrap stability for k={k} ({n_bootstraps} subsamples at {int(sample_ratio*100)}%)...")
    np.random.seed(random_state)
    n_samples = X.shape[0]
    n_sub = int(n_samples * sample_ratio)
    
    # Baseline model
    baseline_km = KMeans(n_clusters=k, init="k-means++", n_init=30, random_state=random_state)
    baseline_km.fit(X)
    baseline_labels = baseline_km.labels_
    
    bootstrap_aris = []
    for b in range(n_bootstraps):
        sub_indices = np.random.choice(n_samples, size=n_sub, replace=False)
        X_sub = X[sub_indices]
        
        sub_km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=b)
        sub_km.fit(X_sub)
        
        # Predict on full dataset
        pred_full_labels = sub_km.predict(X)
        ari = adjusted_rand_score(baseline_labels, pred_full_labels)
        bootstrap_aris.append(ari)
        
    mean_boot_ari = float(np.mean(bootstrap_aris))
    std_boot_ari = float(np.std(bootstrap_aris))
    
    logger.info(f"Bootstrap Stability (k={k}): Mean ARI = {mean_boot_ari:.4f} +/- {std_boot_ari:.4f}")
    
    return {
        "k": k,
        "n_bootstraps": n_bootstraps,
        "sample_ratio": sample_ratio,
        "mean_bootstrap_ari": round(mean_boot_ari, 4),
        "std_bootstrap_ari": round(std_boot_ari, 4),
        "min_bootstrap_ari": round(float(np.min(bootstrap_aris)), 4),
        "max_bootstrap_ari": round(float(np.max(bootstrap_aris)), 4)
    }

if __name__ == "__main__":
    from preprocessing import run_preprocessing_pipeline, MCH_NUMERICAL_FEATURES
    clean_df, scaled_df, _ = run_preprocessing_pipeline()
    X = scaled_df[MCH_NUMERICAL_FEATURES].values
    
    init_res = evaluate_initialization_stability(X, k=4)
    boot_res = evaluate_bootstrap_stability(X, k=4)
    print("Stability module executed successfully!")
