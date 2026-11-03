"""
Visualization module for Country Maternal-Child Health Profile Segmentation.
Generates publication-quality figures:
1. Elbow curve (WCSS / Inertia)
2. Silhouette score comparison & per-cluster silhouette distributions
3. Davies-Bouldin index comparison
4. PCA 2D cluster projection with country labels
5. PCA 3D projection
6. PCA loadings heatmap (principal health axes)
7. Multi-axis Radar / Spider chart comparing cluster archetypes
8. Feature distribution boxplots across discovered clusters
9. Euclidean vs. Manhattan distance metric cross-comparison
"""

import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
from sklearn.metrics import silhouette_samples

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Set publication style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

CLUSTER_COLORS = ["#D9381E", "#F4A261", "#2A9D8F", "#264653", "#9B5DE5", "#00B4D8"]

def plot_elbow_wcss(eval_df: pd.DataFrame, output_path: str = "outputs/figures/elbow_wcss_curve.png"):
    """Plots WCSS (Inertia) vs Number of Clusters k."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=300)
    
    k_vals = eval_df["k"]
    wcss = eval_df["WCSS_Euclidean"]
    pct_red = eval_df["WCSS_Pct_Reduction"]
    
    color1 = "#1f77b4"
    ax1.plot(k_vals, wcss, marker="o", markersize=8, linewidth=2.5, color=color1, label="WCSS (Inertia)")
    ax1.set_xlabel("Number of Clusters (k)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Within-Cluster Sum of Squares (WCSS)", fontsize=12, fontweight="bold", color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_xticks(k_vals)
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # Secondary axis for % reduction
    ax2 = ax1.twinx()
    color2 = "#e67e22"
    ax2.bar(k_vals, pct_red, alpha=0.35, color=color2, width=0.35, label="% WCSS Drop")
    ax2.set_ylabel("Percentage WCSS Drop (%)", fontsize=12, fontweight="bold", color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.grid(False)
    
    plt.title("Elbow Method: WCSS and Marginal Variance Explained across k", fontsize=14, fontweight="bold", pad=15)
    fig.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved Elbow curve to {output_path}")

def plot_validation_metrics(eval_df: pd.DataFrame, 
                            output_path: str = "outputs/figures/clustering_validation_metrics.png"):
    """Plots Silhouette Scores and Davies-Bouldin Index side by side."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)
    
    k_vals = eval_df["k"]
    
    # 1. Silhouette Scores (Higher is better)
    ax1.plot(k_vals, eval_df["Silhouette_Euclidean"], marker="s", markersize=8, linewidth=2.5, 
             color="#2A9D8F", label="Euclidean Silhouette")
    if "Silhouette_Manhattan" in eval_df.columns:
        ax1.plot(k_vals, eval_df["Silhouette_Manhattan"], marker="^", markersize=8, linewidth=2, 
                 linestyle="--", color="#E76F51", label="Manhattan Silhouette")
    ax1.set_title("Silhouette Score vs k (Higher = Superior Separation)", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Number of Clusters (k)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Mean Silhouette Coefficient", fontsize=11, fontweight="bold")
    ax1.set_xticks(k_vals)
    ax1.legend(frameon=True, facecolor="white", edgecolor="#ddd")
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # 2. Davies-Bouldin Index (Lower is better)
    ax2.plot(k_vals, eval_df["Davies_Bouldin_Index"], marker="D", markersize=8, linewidth=2.5, 
             color="#9B5DE5", label="Davies-Bouldin Index (Euclidean)")
    if "Manhattan_Davies_Bouldin" in eval_df.columns and eval_df["Manhattan_Davies_Bouldin"].notna().any():
        ax2.plot(k_vals, eval_df["Manhattan_Davies_Bouldin"], marker="v", markersize=8, linewidth=2,
                 linestyle="--", color="#F15BB5", label="Davies-Bouldin (Manhattan)")
    ax2.set_title("Davies-Bouldin Index vs k (Lower = Superior Compactness)", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Number of Clusters (k)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Davies-Bouldin Index", fontsize=11, fontweight="bold")
    ax2.set_xticks(k_vals)
    ax2.legend(frameon=True, facecolor="white", edgecolor="#ddd")
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved Validation metrics plot to {output_path}")

def plot_silhouette_sample_analysis(X: np.ndarray, 
                                    labels: np.ndarray, 
                                    k: int,
                                    output_path: str = "outputs/figures/silhouette_analysis_k.png"):
    """Plots silhouette coefficient distribution for each individual cluster."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sample_sil_values = silhouette_samples(X, labels)
    mean_sil = np.mean(sample_sil_values)
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    y_lower = 10
    
    for i in range(k):
        ith_cluster_sil_values = sample_sil_values[labels == i]
        ith_cluster_sil_values.sort()
        size_cluster_i = ith_cluster_sil_values.shape[0]
        y_upper = y_lower + size_cluster_i
        
        color = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
        ax.fill_betweenx(np.arange(y_lower, y_upper), 0, ith_cluster_sil_values,
                         facecolor=color, edgecolor=color, alpha=0.8, label=f"Cluster {i+1} (n={size_cluster_i})")
        y_lower = y_upper + 10
        
    ax.axvline(x=mean_sil, color="red", linestyle="--", linewidth=1.5, label=f"Mean Silhouette ({mean_sil:.3f})")
    ax.set_title(f"Silhouette Profile Analysis for k={k} Solution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Silhouette Coefficient Value", fontsize=11, fontweight="bold")
    ax.set_ylabel("Cluster Member Instances", fontsize=11, fontweight="bold")
    ax.set_yticks([])
    ax.legend(loc="lower right", frameon=True, facecolor="white")
    ax.grid(True, linestyle=":", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved Silhouette sample analysis to {output_path}")

def plot_pca_2d_clusters(X_pca: np.ndarray, 
                         labels: np.ndarray, 
                         country_names: List[str],
                         pca_model: Any,
                         cluster_names: Dict[int, str] = None,
                         output_path: str = "outputs/figures/pca_2d_clusters.png"):
    """Visualizes 2D PCA projection of countries colored by assigned cluster."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    
    k = len(np.unique(labels))
    exp_var = pca_model.explained_variance_ratio_ * 100
    
    for i in range(k):
        mask = (labels == i)
        c_label = cluster_names[i] if cluster_names and i in cluster_names else f"Cluster {i+1}"
        ax.scatter(X_pca[mask, 0], X_pca[mask, 1], s=90, color=CLUSTER_COLORS[i % len(CLUSTER_COLORS)],
                   alpha=0.85, edgecolors="white", linewidth=0.8, label=c_label)
        
    # Annotate select representative countries
    for idx, name in enumerate(country_names):
        # Annotate countries with notable positions
        if idx % 3 == 0 or name in ["Nigeria", "India", "Kenya", "Haiti", "Bangladesh", "South Africa", "Egypt"]:
            ax.annotate(name, (X_pca[idx, 0], X_pca[idx, 1]), fontsize=7.5, alpha=0.75,
                        xytext=(4, 4), textcoords="offset points")
            
    ax.set_title(f"PCA 2D Projection: Country Maternal-Child Health Clusters (k={k})", fontsize=14, fontweight="bold")
    ax.set_xlabel(f"Principal Component 1 ({exp_var[0]:.1f}% Variance Explained)", fontsize=11, fontweight="bold")
    ax.set_ylabel(f"Principal Component 2 ({exp_var[1]:.1f}% Variance Explained)", fontsize=11, fontweight="bold")
    ax.legend(title="Public Health Typology", frameon=True, facecolor="white", edgecolor="#ccc", loc="best")
    ax.grid(True, linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved 2D PCA cluster plot to {output_path}")

def plot_pca_loadings_heatmap(loadings_df: pd.DataFrame, 
                              output_path: str = "outputs/figures/pca_loadings_heatmap.png"):
    """Visualizes PCA component loadings across the original MCH features."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    
    # Clean feature names for display
    clean_index = [col.replace("_", " ") for col in loadings_df.index]
    plot_df = loadings_df.copy()
    plot_df.index = clean_index
    
    sns.heatmap(plot_df, annot=True, fmt=".2f", cmap="coolwarm", center=0, 
                cbar_kws={"label": "Component Loading Weight"}, ax=ax, linewidths=0.5)
    
    ax.set_title("PCA Component Loadings (Maternal-Child Health Axes)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Principal Components", fontsize=11, fontweight="bold")
    ax.set_ylabel("MCH Survey Indicators", fontsize=11, fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved PCA loadings heatmap to {output_path}")

def plot_cluster_radar_profiles(profile_df: pd.DataFrame, 
                                cluster_names: Dict[int, str] = None,
                                output_path: str = "outputs/figures/cluster_radar_profiles.png"):
    """Generates a spider/radar chart displaying comparative cluster health profiles."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Normalize features to 0-1 scale for radar chart display
    norm_df = (profile_df - profile_df.min()) / (profile_df.max() - profile_df.min() + 1e-9)
    
    categories = [col.replace("_", " ") for col in norm_df.columns]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True), dpi=300)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    plt.xticks(angles[:-1], categories, size=9, fontweight="semibold")
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=8)
    plt.ylim(0, 1.05)
    
    for idx in norm_df.index:
        values = norm_df.loc[idx].values.flatten().tolist()
        values += values[:1]
        c_label = cluster_names[idx] if cluster_names and idx in cluster_names else f"Cluster {idx+1}"
        color = CLUSTER_COLORS[idx % len(CLUSTER_COLORS)]
        
        ax.plot(angles, values, linewidth=2, linestyle="solid", color=color, label=c_label)
        ax.fill(angles, values, color=color, alpha=0.15)
        
    plt.title("Maternal-Child Health Profile Segmentation\nComparative Cluster Radar Chart", size=14, fontweight="bold", y=1.08)
    plt.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), frameon=True, facecolor="white", edgecolor="#ccc")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved Cluster radar chart to {output_path}")

def plot_distance_metric_comparison(contingency_matrix: pd.DataFrame, 
                                    output_path: str = "outputs/figures/distance_metric_comparison.png"):
    """Visualizes cross-tabulation heatmap between Euclidean K-Means and Manhattan K-Medoids."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    
    sns.heatmap(contingency_matrix, annot=True, fmt="d", cmap="YlGnBu", cbar=True, ax=ax)
    ax.set_title("Cluster Congruence: Euclidean K-Means vs. Manhattan K-Medoids", fontsize=13, fontweight="bold")
    ax.set_xlabel("Manhattan K-Medoids Assigned Cluster", fontsize=11, fontweight="bold")
    ax.set_ylabel("Euclidean K-Means Assigned Cluster", fontsize=11, fontweight="bold")
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    logger.info(f"Saved distance metric comparison to {output_path}")

def plot_feature_boxplots_by_cluster(clean_df: pd.DataFrame, 
                                     labels: np.ndarray,
                                     key_features: List[str],
                                     cluster_names: Dict[int, str] = None,
                                     output_path: str = "outputs/figures/feature_boxplots_by_cluster.png"):
    """Plots comparative boxplots of key health indicators across discovered clusters."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plot_df = clean_df.copy()
    plot_df["Cluster"] = [cluster_names[l] if cluster_names and l in cluster_names else f"Cluster {l+1}" for l in labels]
    
    n_feats = len(key_features)
    ncols = 3
    nrows = int(np.ceil(n_feats / ncols))
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4 * nrows), dpi=300)
    axes = axes.flatten()
    
    for i, feat in enumerate(key_features):
        ax = axes[i]
        sns.boxplot(x="Cluster", y=feat, data=plot_df, hue="Cluster", palette=CLUSTER_COLORS[:len(np.unique(labels))], legend=False, ax=ax)
        ax.set_title(feat.replace("_", " "), fontsize=12, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel("Survey Value", fontsize=10)
        ax.tick_params(axis="x", rotation=25)
        ax.grid(True, linestyle=":", alpha=0.5)
        
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])
        
    plt.suptitle("Key Maternal-Child Health Indicators by Discovered Cluster", fontsize=15, fontweight="bold", y=1.00)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved feature boxplots to {output_path}")
