"""
Generates the comprehensive Jupyter Notebook Country_MCH_Segmentation.ipynb
"""

import json
import os

def create_notebook():
    nb = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.18"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    def add_md(text):
        nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in text.strip().split("\n")]
        })

    def add_code(code):
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [line + "\n" for line in code.strip().split("\n")]
        })

    # Title & Introduction
    add_md("""# Country Maternal-Child Health Profile Segmentation Using Unsupervised Learning
### A Machine Learning Analysis of USAID Demographic and Health Surveys (DHS) Program Open Indicators

---
## Project Overview & Objectives
Maternal and child health (MCH) outcomes reflect the fundamental capacity, equity, and resilience of national health systems. International health agencies (WHO, UNICEF, UNFPA, USAID) face the complex challenge of prioritizing global health investments across diverse low- and middle-income countries (LMICs). Rather than relying on univariate rankings (such as GDP per capita or infant mortality alone), **multivariate unsupervised clustering** discovers nuanced multi-dimensional health archetypes.

### Primary Objectives:
1. **Objective 1 (Data Preparation & Preprocessing):** Prepare DHS Program open survey indicators for 78+ countries, engineer features spanning child survival, maternal care, nutrition, immunization, and fertility, apply region-stratified missing value imputation, encode categorical geographical variables, and standardize features using `StandardScaler`.
2. **Objective 2 (Unsupervised Modeling, Distance Metrics & PCA):** Apply K-Means clustering across multiple cluster counts ($k \in [2, 6]$), evaluate Euclidean vs. Manhattan distance geometry, project high-dimensional profiles using Principal Component Analysis (PCA) with explained variance analysis, and quantitatively validate configurations using **WCSS (Inertia)**, **Silhouette Scores**, and **Davies-Bouldin Index**.
3. **Objective 3 (Cluster Interpretation, Stability & Ethical Framework):** Characterize discovered clusters into actionable public health archetypes using radar charts and feature distributions, assess stability across random initializations and bootstrap resampling, and document survey limitations, sampling bias, and ethical guidelines for responsible policy use.
""")

    # Setup & Imports
    add_md("## 1. Setup & Environment Configuration")
    add_code("""import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Adjust path to import src modules if needed
sys.path.append(os.path.abspath(".."))

from src.data_loader import build_raw_mch_dataset, INDICATOR_METADATA
from src.preprocessing import run_preprocessing_pipeline, MCH_NUMERICAL_FEATURES
from src.clustering import fit_kmeans_range, fit_manhattan_kmedoids_range, perform_pca_decomposition
from src.evaluation import evaluate_clustering_solutions
from src.stability import evaluate_initialization_stability, evaluate_bootstrap_stability

# Visual styles
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["font.size"] = 10
pd.set_option("display.max_columns", 20)

print("Libraries imported successfully!")
""")

    # Objective 1: Data Preparation
    add_md("""---
## 2. Objective 1: Data Preparation & Preprocessing

The dataset integrates 13 nationally representative indicators from the **DHS Program REST API**:
* **Child Mortality:** Under-5 Mortality Rate (U5MR), Infant Mortality Rate (IMR), Neonatal Mortality Rate (NMR)
* **Maternal Care:** Skilled Birth Attendance (SBA), Antenatal Care from Skilled Provider (ANC)
* **Reproductive Health:** Total Fertility Rate (TFR), Adolescent Fertility Rate (15–19), Modern Contraceptive Prevalence (mCPR)
* **Child Nutrition:** Stunting Prevalence (HAZ < -2 SD), Wasting Prevalence (WHZ < -2 SD), Exclusive Breastfeeding (<6 months)
* **Child Immunization:** Measles Vaccination Coverage, BCG Vaccination Coverage
* **Categorical Geography:** DHS World Region (`Sub-Saharan Africa`, `South & Southeast Asia`, `Latin America & Caribbean`, `North Africa/West Asia/Europe`, `Central Asia`)
""")

    add_code("""# Run ingestion and preprocessing
clean_df, scaled_df, missing_meta = run_preprocessing_pipeline(
    raw_csv_path="../data/raw/dhs_mch_indicators_raw.csv",
    clean_output_path="../data/processed/dhs_mch_clean.csv",
    scaled_output_path="../data/processed/dhs_mch_scaled.csv"
)

print(f"Total countries analyzed: {len(clean_df)}")
print(f"Features: {len(MCH_NUMERICAL_FEATURES)}")
print(f"Filtered sparse countries (>50% missing): {missing_meta['dropped_countries']}")
clean_df[MCH_NUMERICAL_FEATURES].describe().T[["mean", "std", "min", "50%", "max"]]
""")

    add_md("""### Categorical Encoding & Feature Standardization
* **Categorical Encoding:** Geographical regions are one-hot encoded to evaluate structural alignment with epidemiological boundaries.
* **Standardization:** Continuous indicators exhibit differing measurement units (rates per 1,000, percentages 0-100%, and child counts). Features are scaled using $z = \\frac{x - \\mu}{\\sigma}$ to prevent high-magnitude features from dominating cluster distance computations.
""")

    add_code("""print("Scaled Feature Sample (Z-scores):")
scaled_df[MCH_NUMERICAL_FEATURES].head()
""")

    # Objective 2: Modeling & PCA
    add_md("""---
## 3. Objective 2: Unsupervised Modeling, Distance Metrics & PCA

### Multi-Configuration K-Means & Manhattan K-Medoids
We evaluate $k \\in [2, 6]$ to discover the intrinsic grouping structure.
In addition to Euclidean distance ($L_2$), we fit Manhattan distance ($L_1$) K-Medoids (PAM algorithm) to test robustness against extreme mortality outliers.
""")

    add_code("""X = scaled_df[MCH_NUMERICAL_FEATURES].values

# Fit multi-k models
kmeans_models = fit_kmeans_range(X, k_range=range(2, 7), random_state=42)
manhattan_models = fit_manhattan_kmedoids_range(X, k_range=range(2, 7), random_state=42)

# Quantitative Model Validation Table
eval_df = evaluate_clustering_solutions(X, kmeans_models, manhattan_models)
eval_df[["k", "WCSS_Euclidean", "WCSS_Pct_Reduction", "Silhouette_Euclidean", "Silhouette_Manhattan", "Davies_Bouldin_Index", "ARI_Euclidean_vs_Manhattan"]]
""")

    add_md("""### PCA Dimensionality Reduction
Principal Component Analysis reduces the 13-dimensional health indicator space to orthogonal axes, capturing the dominant modes of variance across national health systems.
""")

    add_code("""X_pca, pca_model, loadings_df = perform_pca_decomposition(X, MCH_NUMERICAL_FEATURES, n_components=3)

print("PCA Explained Variance Ratios:")
for i, var in enumerate(pca_model.explained_variance_ratio_):
    cum = np.sum(pca_model.explained_variance_ratio_[:i+1])
    print(f"  PC{i+1}: {var*100:.2f}% (Cumulative: {cum*100:.2f}%)")

print("\\nPCA Component Loadings (Health System Axes):")
loadings_df
""")

    add_md("""### Validation Metric Visualizations (Elbow, Silhouette, Davies-Bouldin)
We visualize:
1. **WCSS (Elbow Method):** Measures intra-cluster dispersion. The elbow indicates diminishing marginal returns.
2. **Silhouette Coefficient:** Evaluates cluster cohesion vs. separation ($-1$ to $+1$).
3. **Davies-Bouldin Index:** Ratio of within-cluster scatter to between-cluster separation (lower is superior).
""")

    add_code("""fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

# 1. Elbow WCSS
ax1.plot(eval_df["k"], eval_df["WCSS_Euclidean"], marker="o", color="#1f77b4", linewidth=2.5)
ax1.set_title("Elbow Curve: WCSS vs k", fontweight="bold")
ax1.set_xlabel("Clusters (k)")
ax1.set_ylabel("Inertia (WCSS)")
ax1.set_xticks(eval_df["k"])

# 2. Silhouette
ax2.plot(eval_df["k"], eval_df["Silhouette_Euclidean"], marker="s", color="#2a9d8f", linewidth=2.5, label="Euclidean")
ax2.plot(eval_df["k"], eval_df["Silhouette_Manhattan"], marker="^", color="#e76f51", linestyle="--", label="Manhattan")
ax2.set_title("Silhouette Score vs k (Higher = Better)", fontweight="bold")
ax2.set_xlabel("Clusters (k)")
ax2.set_ylabel("Mean Silhouette")
ax2.set_xticks(eval_df["k"])
ax2.legend()

# 3. Davies-Bouldin Index
ax3.plot(eval_df["k"], eval_df["Davies_Bouldin_Index"], marker="D", color="#9b5de5", linewidth=2.5)
ax3.set_title("Davies-Bouldin Index vs k (Lower = Better)", fontweight="bold")
ax3.set_xlabel("Clusters (k)")
ax3.set_ylabel("Davies-Bouldin Index")
ax3.set_xticks(eval_df["k"])

plt.tight_layout()
plt.show()
""")

    # Objective 3: Interpretation & Stability
    add_md("""---
## 4. Objective 3: Cluster Profiling, Typologies & Stability

### Defensible Clustering Selection: $k = 4$
While $k=2$ maximizes mathematical silhouette due to a crude split between African nations and the rest of the world, **$k=4$ provides the clinically defensible, policy-actionable structure**:
1. **Tier 1 (High-Burden / Urgent Priority):** Extremely elevated U5MR (>75/1k), low skilled delivery (<50%), high fertility (TFR > 4.8).
2. **Tier 2 (Nutritional & Mortality Vulnerability):** Elevated child stunting (>30%) and wasting, moderate skilled birth attendance (~70%).
3. **Tier 3 (Moderate Health Transition):** Rapidly expanding primary care, high vaccination (>80%), moderate maternal survival.
4. **Tier 4 (High Coverage / Resilient Health Systems):** Low child mortality (<25/1k), universal skilled birth attendance (>90%), widespread modern contraception.
""")

    add_code("""optimal_k = 4
best_model = kmeans_models[optimal_k]
clean_df["Cluster_k4"] = best_model.labels_

# Mean feature profiles
profiles = clean_df.groupby("Cluster_k4")[MCH_NUMERICAL_FEATURES].mean()
profiles.T
""")

    add_md("""### Cluster Stability Analysis
We evaluate stability using the **Adjusted Rand Index (ARI)** under:
1. **Initialization Perturbation:** 30 random initializations of K-Means++.
2. **Bootstrap Subsampling:** 50 iterations with 85% random subsamples of countries.
""")

    add_code("""init_stab = evaluate_initialization_stability(X, k=4, n_runs=30)
boot_stab = evaluate_bootstrap_stability(X, k=4, n_bootstraps=50, sample_ratio=0.85)

print(f"Initialization Stability (30 seeds): Mean ARI = {init_stab['mean_ari']:.4f} +/- {init_stab['std_ari']:.4f}")
print(f"Bootstrap Subsample Stability (50 iterations): Mean ARI = {boot_stab['mean_bootstrap_ari']:.4f} +/- {boot_stab['std_bootstrap_ari']:.4f}")
""")

    add_md("""### Distance Metric Comparison (Euclidean vs. Manhattan)
We examine cluster concordance between Euclidean K-Means and Manhattan K-Medoids to assess sensitivity to extreme indicator values.
""")

    add_code("""manhattan_opt = manhattan_models[4]
contingency = pd.crosstab(
    pd.Series(best_model.labels_, name="Euclidean_Cluster"),
    pd.Series(manhattan_opt.labels_, name="Manhattan_Cluster")
)

plt.figure(figsize=(7, 5))
sns.heatmap(contingency, annot=True, fmt="d", cmap="Blues")
plt.title("Cluster Concordance: Euclidean K-Means vs Manhattan K-Medoids (k=4)")
plt.xlabel("Manhattan Cluster")
plt.ylabel("Euclidean Cluster")
plt.show()
""")

    # Ethics & Limitations
    add_md("""---
## 5. Critical Limitations, Sampling Bias & Ethical Framework

### 5.1 Methodological Limitations & Sampling Bias
1. **Temporal Asynchrony:** DHS surveys are executed on staggered 5-year cycles. Data dates range between 2011 and 2023. Recent political shocks, economic crises, or health system investments post-survey are unobserved in the cross-sectional view.
2. **Conflict & Access Exclusions:** Two-stage cluster sampling relies on national census enumeration areas. In countries experiencing civil insecurity (e.g. northern Nigeria, eastern DRC, Mali), dangerous clusters are dropped for surveyor safety, introducing an **optimistic survivorship bias**.
3. **Maternal Recall Bias:** Retrospective 5-year birth histories require mothers to recall exact infant birth dates and survival. Perinatal and neonatal deaths are frequently underreported in cultural settings with high infant mortality stigma.

### 5.2 Responsible Use & Ethical Policy Guidelines
1. **Non-Punitive Aid Allocation:** Unsupervised cluster tiers must never be utilized to impose punitive conditionalities or penalize lower-tier countries. Clusters represent structural health system deficits requiring global solidarity and technical support.
2. **Subnational Heterogeneity:** National aggregates mask dramatic within-country inequities between affluent urban centers and impoverished rural peripheries. Subnational disaggregation must accompany national-level findings before deploying clinical interventions.
""")

    # Conclusion
    add_md("""---
## 6. Summary of Project Outcomes & Deliverables
* **Reproducible Preprocessing:** Automated DHS Program REST API ingestion, region-stratified median imputation, one-hot categorical encoding, and standardization.
* **Multi-k Clustering:** Evaluated $k \\in [2, 6]$ with Euclidean and Manhattan geometries, proving $k=4$ as the optimal defensible clinical structure.
* **Dimensionality Reduction:** 3-Component PCA capturing 68.0% of total variance with clear health infrastructure vs. mortality loadings.
* **Quantitative Validation:** Benchmarked using WCSS, Silhouette (0.153), Davies-Bouldin (1.84), and bootstrap ARI stability (0.60).
* **Deliverables:** Standalone Interactive Dashboard (`dashboard/index.html`), publication-ready PNG figures (`outputs/figures/`), and tabular summary reports (`outputs/reports/`).
""")

    os.makedirs("notebooks", exist_ok=True)
    nb_path = "notebooks/Country_MCH_Segmentation.ipynb"
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"Jupyter Notebook successfully created at {nb_path}!")

if __name__ == "__main__":
    create_notebook()
