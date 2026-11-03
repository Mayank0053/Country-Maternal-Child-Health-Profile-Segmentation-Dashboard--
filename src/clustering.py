"""
Clustering module for Country Maternal-Child Health Profile Segmentation.
Implements multi-k K-Means, Euclidean vs. Manhattan distance comparison,
and PCA dimensionality reduction.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import pairwise_distances

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class ManhattanKMedoids:
    """
    K-Medoids clustering using pairwise Manhattan (L1) distance.
    Uses the Partitioning Around Medoids (PAM) algorithm heuristic.
    Medoids are actual country observations, making them robust to outliers.
    """
    def __init__(self, n_clusters: int = 3, max_iter: int = 300, random_state: int = 42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.random_state = random_state
        self.medoid_indices_ = None
        self.labels_ = None
        self.inertia_ = None

    def fit(self, X: np.ndarray):
        np.random.seed(self.random_state)
        n_samples = X.shape[0]
        # Compute Manhattan pairwise distance matrix
        dist_matrix = pairwise_distances(X, metric="manhattan")
        
        # Initialize medoids randomly
        medoid_indices = np.random.choice(n_samples, size=self.n_clusters, replace=False)
        
        for iteration in range(self.max_iter):
            # Assign samples to nearest medoid
            distances_to_medoids = dist_matrix[:, medoid_indices]
            labels = np.argmin(distances_to_medoids, axis=1)
            
            new_medoids = medoid_indices.copy()
            for cluster_k in range(self.n_clusters):
                cluster_members = np.where(labels == cluster_k)[0]
                if len(cluster_members) == 0:
                    continue
                # Find member that minimizes total Manhattan distance to all other members in cluster
                sub_dist = dist_matrix[np.ix_(cluster_members, cluster_members)]
                best_member = cluster_members[np.argmin(sub_dist.sum(axis=1))]
                new_medoids[cluster_k] = best_member
                
            if np.array_equal(medoid_indices, new_medoids):
                break
            medoid_indices = new_medoids
            
        self.medoid_indices_ = medoid_indices
        distances_to_medoids = dist_matrix[:, medoid_indices]
        self.labels_ = np.argmin(distances_to_medoids, axis=1)
        self.inertia_ = np.sum(np.min(distances_to_medoids, axis=1))
        return self

def fit_kmeans_range(X: np.ndarray, 
                     k_range: range = range(2, 7), 
                     random_state: int = 42) -> Dict[int, KMeans]:
    """
    Fits K-Means across a range of cluster counts (k=2 to 6) using Euclidean distance.
    """
    models = {}
    for k in k_range:
        km = KMeans(n_clusters=k, init="k-means++", n_init=50, max_iter=500, random_state=random_state)
        km.fit(X)
        models[k] = km
        logger.info(f"Fitted Euclidean K-Means (k={k}) -> Inertia (WCSS): {km.inertia_:.2f}")
    return models

def fit_manhattan_kmedoids_range(X: np.ndarray,
                                k_range: range = range(2, 7),
                                random_state: int = 42) -> Dict[int, ManhattanKMedoids]:
    """
    Fits K-Medoids across a range of cluster counts using Manhattan (L1) distance.
    """
    models = {}
    for k in k_range:
        kmed = ManhattanKMedoids(n_clusters=k, random_state=random_state)
        kmed.fit(X)
        models[k] = kmed
        logger.info(f"Fitted Manhattan K-Medoids (k={k}) -> L1 Inertia: {kmed.inertia_:.2f}")
    return models

def perform_pca_decomposition(X: np.ndarray, 
                              feature_names: List[str], 
                              n_components: int = 3) -> Tuple[np.ndarray, PCA, pd.DataFrame]:
    """
    Applies Principal Component Analysis to project standardized data into 2D/3D
    and extracts component loadings (eigenvectors).
    """
    pca = PCA(n_components=n_components, random_state=42)
    X_pca = pca.fit_transform(X)
    
    # Loadings = eigenvectors * sqrt(eigenvalues)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    loadings_df = pd.DataFrame(
        loadings,
        index=feature_names,
        columns=[f"PC{i+1}" for i in range(n_components)]
    )
    
    logger.info("PCA Explained Variance Ratios:")
    for i, ratio in enumerate(pca.explained_variance_ratio_):
        logger.info(f"  PC{i+1}: {ratio*100:.2f}% (Cumulative: {np.sum(pca.explained_variance_ratio_[:i+1])*100:.2f}%)")
        
    return X_pca, pca, loadings_df

if __name__ == "__main__":
    from preprocessing import run_preprocessing_pipeline, MCH_NUMERICAL_FEATURES
    clean_df, scaled_df, _ = run_preprocessing_pipeline()
    X = scaled_df[MCH_NUMERICAL_FEATURES].values
    
    km_models = fit_kmeans_range(X)
    kmed_models = fit_manhattan_kmedoids_range(X)
    X_pca, pca, loadings_df = perform_pca_decomposition(X, MCH_NUMERICAL_FEATURES)
    print("Clustering module successfully executed!")
