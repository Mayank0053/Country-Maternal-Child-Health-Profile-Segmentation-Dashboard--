"""
Evaluation module for Country Maternal-Child Health Profile Segmentation.
Computes WCSS, Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz Index,
and metric comparisons across Euclidean and Manhattan distance configurations.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import (
    silhouette_score, 
    silhouette_samples, 
    davies_bouldin_score, 
    calinski_harabasz_score,
    adjusted_rand_score
)
from sklearn.metrics import pairwise_distances

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def evaluate_clustering_solutions(X: np.ndarray, 
                                  kmeans_models: Dict[int, Any],
                                  manhattan_models: Dict[int, Any] = None) -> pd.DataFrame:
    """
    Evaluates multi-k clustering solutions across WCSS, Silhouette,
    Davies-Bouldin, and Calinski-Harabasz metrics.
    """
    results = []
    
    for k, model in kmeans_models.items():
        labels = model.labels_
        wcss = model.inertia_
        
        # Silhouette Score (Euclidean & Manhattan)
        sil_euclidean = silhouette_score(X, labels, metric="euclidean")
        sil_manhattan = silhouette_score(X, labels, metric="manhattan")
        
        # Davies-Bouldin Index (Lower is better)
        db_index = davies_bouldin_score(X, labels)
        
        # Calinski-Harabasz Score (Higher is better)
        ch_score = calinski_harabasz_score(X, labels)
        
        # Check Manhattan K-Medoids if provided
        manhattan_wcss = np.nan
        manhattan_sil = np.nan
        manhattan_db = np.nan
        ari_vs_manhattan = np.nan
        
        if manhattan_models and k in manhattan_models:
            m_model = manhattan_models[k]
            m_labels = m_model.labels_
            manhattan_wcss = m_model.inertia_
            manhattan_sil = silhouette_score(X, m_labels, metric="manhattan")
            manhattan_db = davies_bouldin_score(X, m_labels)
            ari_vs_manhattan = adjusted_rand_score(labels, m_labels)
            
        # Cluster size distribution
        unique, counts = np.unique(labels, return_counts=True)
        size_dist = dict(zip(unique.tolist(), counts.tolist()))
        
        results.append({
            "k": k,
            "WCSS_Euclidean": round(wcss, 2),
            "Silhouette_Euclidean": round(sil_euclidean, 4),
            "Silhouette_Manhattan": round(sil_manhattan, 4),
            "Davies_Bouldin_Index": round(db_index, 4),
            "Calinski_Harabasz_Score": round(ch_score, 2),
            "Manhattan_L1_Inertia": round(manhattan_wcss, 2) if not np.isnan(manhattan_wcss) else None,
            "Manhattan_Silhouette": round(manhattan_sil, 4) if not np.isnan(manhattan_sil) else None,
            "Manhattan_Davies_Bouldin": round(manhattan_db, 4) if not np.isnan(manhattan_db) else None,
            "ARI_Euclidean_vs_Manhattan": round(ari_vs_manhattan, 4) if not np.isnan(ari_vs_manhattan) else None,
            "Cluster_Sizes": size_dist
        })
        
    df_eval = pd.DataFrame(results)
    
    # Calculate % drop in WCSS (Elbow delta)
    wcss_vals = df_eval["WCSS_Euclidean"].values
    pct_drops = [0.0]
    for i in range(1, len(wcss_vals)):
        pct = (wcss_vals[i-1] - wcss_vals[i]) / wcss_vals[i-1] * 100.0
        pct_drops.append(round(pct, 2))
    df_eval["WCSS_Pct_Reduction"] = pct_drops
    
    logger.info("Clustering Evaluation Summary:\n" + df_eval.to_string(index=False))
    return df_eval

def get_silhouette_samples_dict(X: np.ndarray, 
                                labels: np.ndarray, 
                                metric: str = "euclidean") -> np.ndarray:
    """Computes individual sample silhouette coefficients."""
    return silhouette_samples(X, labels, metric=metric)

if __name__ == "__main__":
    from preprocessing import run_preprocessing_pipeline, MCH_NUMERICAL_FEATURES
    from clustering import fit_kmeans_range, fit_manhattan_kmedoids_range
    
    clean_df, scaled_df, _ = run_preprocessing_pipeline()
    X = scaled_df[MCH_NUMERICAL_FEATURES].values
    
    km_models = fit_kmeans_range(X)
    kmed_models = fit_manhattan_kmedoids_range(X)
    eval_df = evaluate_clustering_solutions(X, km_models, kmed_models)
    print("Evaluation module executed successfully!")
