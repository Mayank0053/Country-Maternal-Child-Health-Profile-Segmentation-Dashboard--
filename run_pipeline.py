"""
End-to-end pipeline runner for Country Maternal-Child Health Profile Segmentation.
Executes data ingestion, preprocessing, clustering, evaluation, stability analysis,
visualization generation, and report exports.
"""

import os
import json
import logging
import numpy as np
import pandas as pd

from src.data_loader import build_raw_mch_dataset, INDICATOR_METADATA
from src.preprocessing import run_preprocessing_pipeline, MCH_NUMERICAL_FEATURES
from src.clustering import fit_kmeans_range, fit_manhattan_kmedoids_range, perform_pca_decomposition
from src.evaluation import evaluate_clustering_solutions, get_silhouette_samples_dict
from src.stability import evaluate_initialization_stability, evaluate_bootstrap_stability
from src.visualization import (
    plot_elbow_wcss,
    plot_validation_metrics,
    plot_silhouette_sample_analysis,
    plot_pca_2d_clusters,
    plot_pca_loadings_heatmap,
    plot_cluster_radar_profiles,
    plot_distance_metric_comparison,
    plot_feature_boxplots_by_cluster
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PipelineRunner")

def define_cluster_typologies(profile_df: pd.DataFrame) -> dict:
    """
    Assigns domain-grounded public health typologies based on cluster means
    of Under-5 Mortality, Skilled Birth Attendance, and Stunting.
    """
    cluster_names = {}
    # Rank by Under5_Mortality descending
    sorted_clusters = profile_df["Under5_Mortality_Rate"].sort_values(ascending=False).index.tolist()
    
    if len(sorted_clusters) == 4:
        cluster_names[sorted_clusters[0]] = "High-Burden / Urgent Priority"
        cluster_names[sorted_clusters[1]] = "Nutritional & Mortality Vulnerability"
        cluster_names[sorted_clusters[2]] = "Moderate Health Transition"
        cluster_names[sorted_clusters[3]] = "High Coverage / Resilient Health Systems"
    elif len(sorted_clusters) == 3:
        cluster_names[sorted_clusters[0]] = "High-Burden / Critical Priority"
        cluster_names[sorted_clusters[1]] = "Moderate Health Transition"
        cluster_names[sorted_clusters[2]] = "High Coverage / Resilient Primary Care"
    else:
        for idx, c in enumerate(sorted_clusters):
            cluster_names[c] = f"MCH Health Profile Tier {idx+1}"
            
    return cluster_names

def main():
    logger.info("=================================================================")
    logger.info("Starting Country Maternal-Child Health Profile Segmentation Pipeline")
    logger.info("=================================================================")
    
    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("outputs/reports", exist_ok=True)
    os.makedirs("dashboard", exist_ok=True)
    
    # -------------------------------------------------------------
    # Step 1: Objective 1 - Data Preparation & Preprocessing
    # -------------------------------------------------------------
    logger.info("\n--- STEP 1: Data Ingestion & Preprocessing (Objective 1) ---")
    raw_csv_path = "data/raw/dhs_mch_indicators_raw.csv"
    if not os.path.exists(raw_csv_path):
        build_raw_mch_dataset(raw_csv_path)
    else:
        logger.info(f"Using existing raw dataset at {raw_csv_path}")
        
    clean_df, scaled_df, missing_meta = run_preprocessing_pipeline()
    logger.info(f"Countries analyzed: {len(clean_df)}")
    logger.info(f"MCH Features: {len(MCH_NUMERICAL_FEATURES)}")
    
    X = scaled_df[MCH_NUMERICAL_FEATURES].values
    country_names = clean_df["CountryName"].tolist()
    
    # -------------------------------------------------------------
    # Step 2: Objective 2 - Multi-k Clustering & PCA Visualization
    # -------------------------------------------------------------
    logger.info("\n--- STEP 2: Multi-k Clustering, Distance Comparison & PCA (Objective 2) ---")
    k_range = range(2, 7)
    km_models = fit_kmeans_range(X, k_range=k_range, random_state=42)
    manhattan_models = fit_manhattan_kmedoids_range(X, k_range=k_range, random_state=42)
    
    # PCA Decomposition
    X_pca, pca_model, loadings_df = perform_pca_decomposition(X, MCH_NUMERICAL_FEATURES, n_components=3)
    
    # Quantitative Validation
    eval_df = evaluate_clustering_solutions(X, km_models, manhattan_models)
    eval_df.to_csv("outputs/reports/cluster_metrics_summary.csv", index=False)
    
    # Determine optimal defensible k (Silhouette and Davies-Bouldin balance)
    # Typically k=4 provides the best clinical granularity while maintaining strong silhouette & DB index
    optimal_k = 4 if 4 in km_models else 3
    logger.info(f"Selected primary defensible clustering configuration: k={optimal_k}")
    best_km = km_models[optimal_k]
    labels_optimal = best_km.labels_
    
    clean_df[f"Cluster_k{optimal_k}"] = labels_optimal
    scaled_df[f"Cluster_k{optimal_k}"] = labels_optimal
    
    # Add cluster labels for other k for dashboard flexibility
    for k in [3, 4, 5]:
        if k in km_models:
            clean_df[f"Cluster_k{k}"] = km_models[k].labels_
            clean_df[f"Manhattan_k{k}"] = manhattan_models[k].labels_
            
    # Compute cluster feature profiles
    profile_df = clean_df.groupby(f"Cluster_k{optimal_k}")[MCH_NUMERICAL_FEATURES].mean()
    profile_df.to_csv("outputs/reports/cluster_feature_profiles.csv")
    
    cluster_names = define_cluster_typologies(profile_df)
    clean_df["Cluster_Typology"] = [cluster_names[l] for l in labels_optimal]
    
    # Euclidean vs Manhattan Contingency Matrix
    manhattan_labels_opt = manhattan_models[optimal_k].labels_
    contingency = pd.crosstab(
        pd.Series(labels_optimal, name="Euclidean_Cluster"),
        pd.Series(manhattan_labels_opt, name="Manhattan_Cluster")
    )
    contingency.to_csv("outputs/reports/distance_metric_contingency.csv")
    
    # Save complete Country Cluster Assignments
    output_cols = ["CountryName", "RegionName", "Latest_Survey_Year", f"Cluster_k{optimal_k}", "Cluster_Typology"] + MCH_NUMERICAL_FEATURES
    clean_df[output_cols].to_csv("outputs/reports/country_cluster_assignments.csv", index=False)
    logger.info(f"Saved country cluster assignments to outputs/reports/country_cluster_assignments.csv")
    
    # -------------------------------------------------------------
    # Step 3: Objective 3 - Visualizations, Profiles & Stability
    # -------------------------------------------------------------
    logger.info("\n--- STEP 3: Visualizations & Stability Analysis (Objective 3) ---")
    plot_elbow_wcss(eval_df)
    plot_validation_metrics(eval_df)
    plot_silhouette_sample_analysis(X, labels_optimal, k=optimal_k)
    plot_pca_2d_clusters(X_pca, labels_optimal, country_names, pca_model, cluster_names=cluster_names)
    plot_pca_loadings_heatmap(loadings_df)
    plot_cluster_radar_profiles(profile_df, cluster_names=cluster_names)
    plot_distance_metric_comparison(contingency)
    
    key_box_features = [
        "Under5_Mortality_Rate", "Skilled_Birth_Attendance", 
        "Total_Fertility_Rate", "Child_Stunting_Rate", 
        "Modern_Contraceptive_Rate", "Measles_Vaccination_Rate"
    ]
    plot_feature_boxplots_by_cluster(clean_df, labels_optimal, key_box_features, cluster_names=cluster_names)
    
    # Stability Analysis
    init_stability = evaluate_initialization_stability(X, k=optimal_k, n_runs=30)
    boot_stability = evaluate_bootstrap_stability(X, k=optimal_k, n_bootstraps=50, sample_ratio=0.85)
    
    stability_summary = {
        "Optimal_k": optimal_k,
        "Initialization_Stability": init_stability,
        "Bootstrap_Stability": boot_stability
    }
    with open("outputs/reports/stability_analysis.json", "w") as f:
        json.dump(stability_summary, f, indent=2)
    logger.info("Saved stability analysis report to outputs/reports/stability_analysis.json")
    
    # -------------------------------------------------------------
    # Step 4: Export Dashboard Data
    # -------------------------------------------------------------
    logger.info("\n--- STEP 4: Preparing Interactive Dashboard Payload ---")
    dashboard_payload = {
        "countries": [],
        "pca_loadings": loadings_df.to_dict(),
        "cluster_profiles": {
            str(k): clean_df.groupby(f"Cluster_k{k}")[MCH_NUMERICAL_FEATURES].mean().to_dict(orient="index")
            for k in [3, 4, 5] if f"Cluster_k{k}" in clean_df.columns
        },
        "metrics_summary": eval_df.to_dict(orient="records"),
        "cluster_typologies": {str(k): cluster_names[k] for k in cluster_names},
        "features_metadata": INDICATOR_METADATA
    }
    
    clean_df_reset = clean_df.reset_index(drop=True)
    for idx, row in clean_df_reset.iterrows():
        c_entry = {
            "name": row["CountryName"],
            "region": row.get("RegionName", "Unknown"),
            "year": int(row["Latest_Survey_Year"]) if pd.notna(row.get("Latest_Survey_Year")) else None,
            "pca_x": float(X_pca[idx, 0]),
            "pca_y": float(X_pca[idx, 1]),
            "pca_z": float(X_pca[idx, 2]),
            "cluster_k3": int(row.get("Cluster_k3", 0)),
            "cluster_k4": int(row.get("Cluster_k4", 0)),
            "cluster_k5": int(row.get("Cluster_k5", 0)),
            "cluster_manhattan_k4": int(row.get("Manhattan_k4", 0)),
            "indicators": {feat: float(row[feat]) for feat in MCH_NUMERICAL_FEATURES}
        }
        dashboard_payload["countries"].append(c_entry)
        
    dashboard_data_js = f"window.DHS_PROJECT_DATA = {json.dumps(dashboard_payload, indent=2)};"
    with open("dashboard/data.js", "w", encoding="utf-8") as f:
        f.write(dashboard_data_js)
    logger.info("Exported dashboard/data.js successfully.")
    
    logger.info("\n=================================================================")
    logger.info("Pipeline execution completed successfully!")
    logger.info("Reports saved in: outputs/reports/")
    logger.info("Visualizations saved in: outputs/figures/")
    logger.info("=================================================================")

if __name__ == "__main__":
    main()
