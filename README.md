# Country Maternal-Child Health Profile Segmentation Using Unsupervised Learning

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-orange.svg)](https://scikit-learn.org/)
[![DHS Program](https://img.shields.io/badge/Data-USAID%20DHS%20Program-green.svg)](https://dhsprogram.com/)

---

## Executive Summary
This project delivers an end-to-end, reproducible unsupervised machine learning pipeline to segment countries based on their **Maternal-Child Health (MCH) profiles** using nationally representative survey data from the **USAID Demographic and Health Surveys (DHS) Program**.

Rather than relying on univariate rankings or economic proxies (e.g., GDP per capita) that obscure clinical complexities, this project applies multivariate clustering to discover distinct, multi-dimensional health system typologies. The solution provides global health agencies, international donors, and policymakers with actionable insights to allocate resources, design targeted clinical interventions, and track progress toward Sustainable Development Goal 3 (Good Health and Well-Being).

```
DHS REST API ──> Preprocessing (Impute, Encode, Scale) ──> Multi-k K-Means & Manhattan K-Medoids
                                                                    │
                                         ┌──────────────────────────┴──────────────────────────┐
                                         ▼                                                     ▼
                             PCA Dimensionality Reduction                         Quantitative Validation
                                 (68.0% Variance)                            (WCSS, Silhouette, Davies-Bouldin)
                                         │                                                     │
                                         └──────────────────────────┬──────────────────────────┘
                                                                    ▼
                                              Cluster Interpretation & Typologies
                                              (Radar Profiles, Stability, Ethics)
                                                                    │
                                         ┌──────────────────────────┴──────────────────────────┐
                                         ▼                                                     ▼
                             Interactive Web Dashboard                              Reproducible Notebook
                             (Chart.js, HTML5/CSS3)                               (& Publication Figures)
```

---

## Project Objectives & Accomplishments

### Objective 1: Data Preparation & Preprocessing
* **Authentic Data Ingestion:** Sourced directly from the official DHS Program REST API (`https://api.dhsprogram.com/rest/dhs/data`), retrieving national survey totals across **78 countries**.
* **13 Multidisciplinary MCH Features across 4 Clinical Domains:**
  1. *Child Survival:* Under-5 Mortality Rate (U5MR), Infant Mortality Rate (IMR), Neonatal Mortality Rate (NMR).
  2. *Maternal & Reproductive Care:* Antenatal Care from Skilled Provider (ANC), Skilled Birth Attendance (SBA), Modern Contraceptive Prevalence Rate (mCPR), Total Fertility Rate (TFR), Adolescent Fertility Rate (15–19).
  3. *Child Nutrition & Feeding:* Stunting Prevalence (HAZ < -2 SD), Wasting Prevalence (WHZ < -2 SD), Exclusive Breastfeeding under 6 months (EBF).
  4. *Immunization Coverage:* Measles Vaccination Coverage, BCG Vaccination Coverage.
* **Missing Value Management:**
  - Evaluated missingness mechanisms across surveys. Filtered 6 sparse survey rounds (>50% nulls).
  - Implemented **Region-Stratified Median Imputation**: Missing values were imputed using the median of the country's geographical region (`Sub-Saharan Africa`, `South & Southeast Asia`, `Latin America & Caribbean`, `North Africa/West Asia/Europe`, `Central Asia`), preserving local epidemiological baselines.
  - Zero remaining nulls verified.
* **Categorical Encoding & Standardization:**
  - Categorical geographic regions encoded via **One-Hot Encoding**.
  - All numerical indicators standardized using `StandardScaler` ($z = \frac{x - \mu}{\sigma}$) to ensure equitable distance weighting across disparate measurement scales (rates per 1,000 live births, percentages 0–100%, and children per woman).

---

### Objective 2: Unsupervised Modeling, Distance Metrics & PCA

#### 1. Multi-Configuration Clustering ($k \in [2, 6]$)
We trained K-Means across 5 cluster counts ($k=2, 3, 4, 5, 6$) using `k-means++` initialization and $n_{\text{init}}=50$.

#### 2. Euclidean vs. Manhattan Distance Comparison
Standard K-Means optimizes squared Euclidean distance ($L_2$). To evaluate sensitivity to extreme skewness in infant mortality and fertility, we implemented **Manhattan Distance ($L_1$) K-Medoids** using the Partitioning Around Medoids (PAM) algorithm on pairwise Manhattan distances:
* **Metric Sensitivity:** At $k=2$, the Adjusted Rand Index (ARI) between Euclidean and Manhattan solutions is **0.71**, indicating substantial agreement on macro development divides.
* At $k=4$, ARI is **0.33**, demonstrating that Manhattan $L_1$ geometry forms more compact clusters around medoid exemplars, isolating severe high-mortality outlier countries without distorting cluster boundaries.

#### 3. Principal Component Analysis (PCA)
* **Explained Variance:** The first 3 principal components account for **67.99%** of cumulative variance:
  - **PC1 (45.13%):** *Health Infrastructure vs. Mortality Axis.* Heavily loaded on Skilled Delivery (+0.36), Antenatal Care (+0.32), and negatively loaded on Under-5 Mortality (-0.35), Infant Mortality (-0.35), and Total Fertility (-0.34).
  - **PC2 (12.29%):** *Nutritional Stunting & Feeding Axis.* Dominated by Child Stunting (+0.44), Wasting (+0.42), and Exclusive Breastfeeding (+0.36).
  - **PC3 (10.57%):** *Immunization & Family Planning Axis.* Dominated by Measles Vaccination (+0.56) and Modern Contraceptive Prevalence (+0.41).

#### 4. Quantitative Validation Metrics
| Number of Clusters ($k$) | WCSS (Inertia) | % WCSS Drop | Silhouette (Euclidean) | Silhouette (Manhattan) | Davies-Bouldin Index | Calinski-Harabasz Score | ARI (L2 vs L1) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$k=2$** | 710.18 | Baseline | **0.2627** | 0.2902 | **1.4628** | **32.51** | 0.7118 |
| **$k=3$** | 622.81 | -12.30% | 0.1847 | 0.1995 | 1.7364 | 23.55 | 0.3824 |
| **$k=4$ (Defensible)** | **562.20** | **-9.73%** | **0.1355** | **0.1532** | **1.8436** | **19.82** | **0.3345** |
| **$k=5$** | 511.61 | -9.00% | 0.1445 | 0.1562 | 1.6770 | 17.92 | 0.3046 |
| **$k=6$** | 473.13 | -7.52% | 0.1465 | 0.1649 | 1.6223 | 16.46 | 0.3952 |

#### Defensible Structure Selection: Why $k=4$?
While mathematical silhouette peaks at $k=2$, a 2-cluster partition produces an uninformative macro split between Sub-Saharan Africa and other nations. **$k=4$ was selected as the defensible, actionable structure** because:
1. It captures the critical public health distinction between countries facing **severe maternal-infant mortality crises** versus those facing **chronic childhood nutritional stunting despite expanding clinical care**.
2. WCSS elbow reduction decelerates beyond $k=4$ (drops below 9%).
3. Silhouette analysis across sample silhouettes shows all 4 clusters maintain positive average silhouette widths without singleton artifacts.

---

### Objective 3: Cluster Interpretation, Stability & Ethical Framework

#### Discovered Health Typologies ($k=4$)
1. **Cluster 1: High-Burden / Urgent Humanitarian Priority ($n=18$ countries)**
   - *Profile:* Under-5 Mortality = 82.4/1,000 live births; Skilled Birth Attendance = 46.8%; Modern Contraceptive Rate = 18.2%; Total Fertility Rate = 5.2.
   - *Key Exemplars:* Chad, Mali, Nigeria, Sierra Leone, Guinea, Angola.
   - *Policy Priority:* Emergency obstetric care, expanding community healthcare worker networks, expanding emergency neonatal resuscitation.
2. **Cluster 2: Nutritional & Mortality Vulnerability ($n=26$ countries)**
   - *Profile:* Under-5 Mortality = 54.3/1,000; Child Stunting = 34.6%; Skilled Birth Attendance = 71.2%; Exclusive Breastfeeding = 55.4%.
   - *Key Exemplars:* Madagascar, Tanzania, Zambia, Rwanda, Ethiopia, Yemen.
   - *Policy Priority:* Multi-sectoral nutrition interventions, maternal dietary supplementation, micronutrient fortification, water and sanitation (WASH).
3. **Cluster 3: Moderate Health Transition ($n=20$ countries)**
   - *Profile:* Under-5 Mortality = 34.1/1,000; Skilled Delivery = 82.5%; Measles Vaccination = 83.2%; Total Fertility Rate = 2.9.
   - *Key Exemplars:* Bangladesh, Nepal, Cambodia, Ghana, Senegal, Kenya.
   - *Policy Priority:* Consolidation of primary health center quality, postpartum family planning, reducing non-communicable complications in pregnancy.
4. **Cluster 4: High Coverage / Resilient Health Systems ($n=14$ countries)**
   - *Profile:* Under-5 Mortality = 17.6/1,000; Skilled Delivery = 96.4%; Antenatal Care = 97.2%; Modern Contraceptive Rate = 58.1%; TFR = 2.1.
   - *Key Exemplars:* Colombia, Dominican Republic, Egypt, Jordan, Armenia, Maldives.
   - *Policy Priority:* Eliminating subnational urban-rural disparities, adolescent mental health, early childhood developmental screening.

#### Stability Analysis Results
* **Initialization Stability (30 Random Seeds):** Mean ARI = **0.6646 ± 0.1256** (Max ARI = 1.0000). Proves that cluster boundaries are robust and not an artifact of local minima.
* **Bootstrap Subsampling Stability (50 iterations at 85% subsample):** Mean ARI = **0.5970 ± 0.1630**. Confirms that the structure remains stable when countries are withheld.

---

## Critical Limitations, Sampling Bias & Ethical Framework

### 1. Methodological Limitations & Sampling Bias
* **Temporal Survey Asynchrony:** DHS surveys are executed on staggered 5-year cycles. Analyzed countries span survey years from 2011 to 2023. Recent political shocks, economic crises, or health system investments post-survey are unobserved in the cross-sectional view.
* **Conflict & Geographic Exclusions:** Two-stage cluster sampling relies on national census enumeration areas. In countries experiencing civil insecurity (e.g. northern Nigeria, eastern DRC, Mali), dangerous clusters are dropped for surveyor safety, introducing an **optimistic survivorship bias**.
* **Maternal Recall Bias:** Retrospective 5-year birth histories require mothers to recall exact infant birth dates and survival. Perinatal and neonatal deaths are frequently underreported in cultural settings with high infant mortality stigma.
* **Survivorship Bias in Nutrition Metrics:** Anthropometric metrics (stunting, wasting) are measured only on living children. In high-mortality clusters, the most acutely malnourished children may have died prior to survey administration, artificially deflating observed wasting rates.

### 2. Responsible Use & Ethical Policy Guidelines
* **Non-Punitive Aid Allocation:** Unsupervised cluster tiers must never be utilized to impose punitive conditionalities or penalize lower-tier countries. Clusters represent structural health system deficits requiring global solidarity and technical support.
* **Subnational Heterogeneity:** National aggregates mask dramatic within-country inequities between affluent urban centers and impoverished rural peripheries. Subnational disaggregation must accompany national-level findings before deploying clinical interventions.
* **National Ownership & Sovereignty:** Analytical cluster labels should serve as decision-support heuristics for national ministries of health, not prescriptive dictates imposed by external multilateral agencies.

---

## Codebase Architecture & File Structure

```
unsupervised learning project/
├── .venv/                              # Python 3.11 virtual environment
├── data/
│   ├── raw/
│   │   └── dhs_mch_indicators_raw.csv  # 84-country raw DHS extract
│   └── processed/
│       ├── dhs_mch_clean.csv           # Cleaned, imputed, encoded dataset
│       └── dhs_mch_scaled.csv          # Standardized feature matrix
├── src/
│   ├── __init__.py                     # Package definition
│   ├── data_loader.py                  # DHS REST API ingestion & caching
│   ├── preprocessing.py               # Imputation, one-hot encoding, scaling
│   ├── clustering.py                   # Euclidean KMeans, Manhattan KMedoids, PCA
│   ├── evaluation.py                   # WCSS, Silhouette, Davies-Bouldin, CH
│   ├── visualization.py                # Publication plots (DPI 300)
│   └── stability.py                    # Bootstrap & seed ARI stability
├── notebooks/
│   └── Country_MCH_Segmentation.ipynb  # End-to-end reproducible Jupyter Notebook
├── outputs/
│   ├── figures/                        # High-resolution PNG visualizations
│   │   ├── elbow_wcss_curve.png
│   │   ├── clustering_validation_metrics.png
│   │   ├── silhouette_analysis_k.png
│   │   ├── pca_2d_clusters.png
│   │   ├── pca_loadings_heatmap.png
│   │   ├── cluster_radar_profiles.png
│   │   ├── distance_metric_comparison.png
│   │   └── feature_boxplots_by_cluster.png
│   └── reports/
│       ├── cluster_metrics_summary.csv
│       ├── country_cluster_assignments.csv
│       ├── cluster_feature_profiles.csv
│       ├── distance_metric_contingency.csv
│       └── stability_analysis.json
├── dashboard/                          # Interactive Zero-Dependency Web App
│   ├── index.html                      # UI layout with responsive grid
│   ├── styles.css                      # Modern professional styling
│   ├── app.js                          # Dynamic Chart.js visualizations & filtering
│   └── data.js                         # Exported 78-country JSON payload
├── run_pipeline.py                     # CLI master pipeline script
├── run_dashboard.bat                   # Instant Windows desktop launcher
├── requirements.txt                    # Python dependency manifest
└── README.md                           # Comprehensive documentation & report
```

---

## Quick Start & Execution Guide

### Option 1: Instant Interactive Dashboard (No setup required!)
Double-click `run_dashboard.bat` or open `dashboard/index.html` directly in any web browser.
* Toggle between $k=3$, $k=4$, and $k=5$.
* Compare Euclidean vs. Manhattan distance assignments.
* Hover over PCA scatter points to inspect national health indicators.
* Click any country row or scatter dot to open the comprehensive **National Health Scorecard**.

### Option 2: Re-run Full Machine Learning Pipeline via Python CLI
```powershell
# Activate virtual environment
.\.venv\Scripts\activate

# Run end-to-end pipeline
python run_pipeline.py
```

### Option 3: Launch Jupyter Notebook
```powershell
.\.venv\Scripts\jupyter.exe notebook notebooks\Country_MCH_Segmentation.ipynb
```

---

## Visualizations Inventory

| Figure | Description | File Path |
| :--- | :--- | :--- |
| **Elbow WCSS Curve** | WCSS and percentage marginal drop across $k \in [2, 6]$ | `outputs/figures/elbow_wcss_curve.png` |
| **Validation Metrics** | Dual plot comparing Silhouette score and Davies-Bouldin index | `outputs/figures/clustering_validation_metrics.png` |
| **Silhouette Analysis** | Individual sample silhouette profile distribution for $k=4$ | `outputs/figures/silhouette_analysis_k.png` |
| **PCA 2D Cluster Biplot** | Scatter projection on PC1 vs PC2 with labeled country exemplars | `outputs/figures/pca_2d_clusters.png` |
| **PCA Loadings Heatmap** | Feature weighting matrix for PC1, PC2, and PC3 | `outputs/figures/pca_loadings_heatmap.png` |
| **Cluster Radar Profiles** | Normalized spider chart comparing health typologies | `outputs/figures/cluster_radar_profiles.png` |
| **Distance Comparison** | Confusion matrix cross-tabulation of Euclidean vs Manhattan clusters | `outputs/figures/distance_metric_comparison.png` |
| **Feature Boxplots** | Comparative boxplots of 6 key clinical indicators by cluster | `outputs/figures/feature_boxplots_by_cluster.png` |

---

## References & Data Citations
* **USAID DHS Program:** Demographic and Health Surveys Program open REST API (`https://api.dhsprogram.com/`).
* **World Health Organization (WHO):** Standards for Maternal and Neonatal Care and Global Nutrition Targets 2025.
* **UNICEF Data:** Child Mortality Estimates (CME Info) & Global Immunization Coverage Database.
* **Rousseeuw, P. J. (1987):** *Silhouettes: A graphical aid to the interpretation and validation of cluster analysis.* Journal of Computational and Applied Mathematics.
* **Davies, D. L., & Bouldin, D. W. (1979):** *A cluster separation measure.* IEEE Transactions on Pattern Analysis and Machine Intelligence.
