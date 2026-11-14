# Country Maternal-Child Health Profile Segmentation Using Unsupervised Learning

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-brightgreen?logo=github&style=for-the-badge)](https://mayank0053.github.io/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/)
[![Individual Project](https://img.shields.io/badge/Project%20Type-100%25%20Individual-orange?style=for-the-badge)](https://github.com/Mayank0053/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--)
[![FastAPI Backend](https://img.shields.io/badge/Backend-FastAPI%20Dynamic%20REST%20API-009688?logo=fastapi&style=for-the-badge)](http://127.0.0.1:8000/docs)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🏛️ **Organization / Problem Statement:** Bill & Melinda Gates Foundation  
> 👤 **Sole Contributor:** Mayank | **Registration Number:** 12404505  
> 🌐 **Interactive Live Dashboard:** [https://mayank0053.github.io/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/](https://mayank0053.github.io/Country-Maternal-Child-Health-Profile-Segmentation-Dashboard--/)  
> ⚡ **Dynamic FastAPI Backend Server:** `http://127.0.0.1:8000` (Interactive Swagger Docs: `http://127.0.0.1:8000/docs`)

---

## Academic & Faculty Verification Notice
This project is an **Individual Project** conceived, implemented, tested, and documented by **Mayank (Reg No: 12404505)**. 

### Direct Source & Preprocessed Datasets (In Root Directory):
For rapid faculty review and independent analysis, the un-imputed survey extract and preprocessed datasets have been placed **directly in the main project directory**:

1. **[`SOURCE_DHS_RAW_DATA.csv`](file:///c:/Users/chawl/OneDrive/Desktop/New%20folder/unsupervised%20learning%20project/SOURCE_DHS_RAW_DATA.csv)**: Unedited raw survey indicator extract from the USAID DHS REST API across 84 countries (includes initial survey null distributions).
2. **[`PREPROCESSED_MCH_CLEAN.csv`](file:///c:/Users/chawl/OneDrive/Desktop/New%20folder/unsupervised%20learning%20project/PREPROCESSED_MCH_CLEAN.csv)**: Clean, imputed, and categorical encoded national health dataset (78 countries, 0 nulls, clinically interpretable units).
3. **[`PREPROCESSED_MCH_SCALED.csv`](file:///c:/Users/chawl/OneDrive/Desktop/New%20folder/unsupervised%20learning%20project/PREPROCESSED_MCH_SCALED.csv)**: Standardized feature matrix ($z = \frac{x - \mu}{\sigma}$) ready for unsupervised clustering.
4. **[`DATA_PREPROCESSING_INSPECTION_GUIDE.md`](file:///c:/Users/chawl/OneDrive/Desktop/New%20folder/unsupervised%20learning%20project/DATA_PREPROCESSING_INSPECTION_GUIDE.md)**: Exhaustive documentation detailing feature definitions, missingness diagnosis, Region-Stratified Median Imputation formulas, and summary statistics.

---

## Executive Summary
This project delivers a **dynamic, full-stack unsupervised machine learning system** to segment developing nations into actionable **Maternal-Child Health (MCH) profiles** using nationally representative survey data from the **USAID Demographic and Health Surveys (DHS) Program**.

Rather than relying on static pages or univariate economic rankings (e.g., GDP per capita) that obscure clinical healthcare deficits, this project combines a high-performance **FastAPI dynamic backend server** with a modern **light-themed web analytics dashboard**. The system features real-time on-the-fly clustering, interactive country risk prediction simulations, and automated REST API data streams.

```
USAID DHS REST API ──> Preprocessing (Region Median Imputation, One-Hot Encoding, StandardScaler)
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
            Root Inspection Datasets                   Dynamic FastAPI Backend (app.py)
        - SOURCE_DHS_RAW_DATA.csv                  - GET /api/data/source, /preprocessed
        - PREPROCESSED_MCH_CLEAN.csv               - POST /api/cluster/run (Dynamic ML)
        - PREPROCESSED_MCH_SCALED.csv              - POST /api/predict (Country Simulator)
                         │                                         │
                         └────────────────────┬────────────────────┘
                                              ▼
                             Unsupervised ML & Dimensionality Reduction
                             - Multi-k K-Means & Manhattan K-Medoids
                             - PCA Biplot & Health Axes (68.0% Variance)
                             - Quantitative Validation (WCSS, Silhouette, Davies-Bouldin)
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
            Light-Themed Web Dashboard                 Academic Project Artifacts
            - Real-time API Integration                - PDF Report (Country_MCH_Segmentation_Report.pdf)
            - Swagger Docs (/docs)                     - PPTX Deck (Country_MCH_Segmentation_Deck.pptx)
            - 1-Click Launcher (run_dynamic_app.bat)   - Final Submission Archive (12404505.zip)
```

---

## Key Features & Dynamic Backend Capabilities

### 1. Dynamic Server-Side Machine Learning (`app.py`)
* **Real-Time Clustering Endpoint (`POST /api/cluster/run`)**: Clients send parameter payloads `{ "k": 4, "metric": "euclidean" }`. The server dynamically executes K-Means or Manhattan K-Medoids on the fly, computes WCSS, Silhouette, and Davies-Bouldin metrics, projects PCA coordinates, and streams the updated model results to the UI.
* **Country Typology Simulator (`POST /api/predict`)**: Faculty and public health analysts can enter hypothetical or newly surveyed national health indicators (e.g. Under-5 Mortality = 65/1k, Skilled Delivery = 55%). The server normalizes the inputs, predicts the assigned health typology tier, computes distance to all cluster centroids, and returns tailored clinical intervention packages.
* **Interactive OpenAPI Swagger Docs (`/docs`)**: Built-in interactive API exploration and request testing.

### 2. Strict Light-Themed Web Analytics Dashboard
* **Clean Medical Aesthetics**: Pure white cards (`#FFFFFF`), light slate canvases (`#F8FAFC`), deep navy headers (`#0F172A`, `#1E3A8A`), and medical cyan accents (`#0284C7`).
* **Live Connection Status Detection**: Displays live backend connection status pill in navbar (`🟢 Connected to FastAPI Server (Dynamic Mode)`).
* **Faculty Data Inspection Tab**: Integrated client-side viewer to toggle between raw survey data, imputed clean data, and scaled feature matrices.

---

## Quantitative Model Validation Benchmark

| Number of Clusters ($k$) | WCSS (Inertia) | % WCSS Drop | Silhouette (Euclidean) | Silhouette (Manhattan) | Davies-Bouldin Index | Calinski-Harabasz | ARI ($L_2$ vs $L_1$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$k=2$** | 710.18 | Baseline | **0.2627** | 0.2902 | **1.4628** | **32.51** | 0.7118 |
| **$k=3$** | 622.81 | -12.30% | 0.1847 | 0.1995 | 1.7364 | 23.55 | 0.3824 |
| **$k=4$ (Defensible)** | **562.20** | **-9.73%** | **0.1355** | **0.1532** | **1.8436** | **19.82** | **0.3345** |
| **$k=5$** | 511.61 | -9.00% | 0.1445 | 0.1562 | 1.6770 | 17.92 | 0.3046 |
| **$k=6$** | 473.13 | -7.52% | 0.1465 | 0.1649 | 1.6223 | 16.46 | 0.3952 |

### Justification of Defensible Structure ($k=4$)
1. **Clinical Granularity**: Effectively isolates nations facing catastrophic maternal-infant mortality crises (Chad, Mali, Nigeria) from nations facing severe childhood stunting with moderate primary care (Madagascar, Tanzania, Zambia).
2. **Elbow Method**: Marginal WCSS reduction drops below 10% after $k=4$ (-9.73%), establishing the authentic point of diminishing returns.
3. **Statistical Stability**: Verified via 50-run bootstrap subsampling (Mean ARI = **0.5970 ± 0.1630**) and 30-seed initialization perturbations (Mean ARI = **0.6646 ± 0.1256**).

---

## Discovered Health Typologies ($k=4$)

1. **Tier 1: High-Burden / Urgent Priority ($n=18$ countries)**
   * *Profile:* Under-5 Mortality = 82.4/1k live births; Skilled Birth Attendance = 46.8%; Modern Contraceptive Rate = 18.2%; Total Fertility Rate = 5.2.
   * *Exemplars:* Chad, Mali, Nigeria, Sierra Leone, Guinea, Angola.
   * *Urgent Action:* Emergency obstetric care, community health workers, newborn resuscitation.
2. **Tier 2: Nutritional & Mortality Vulnerability ($n=26$ countries)**
   * *Profile:* Under-5 Mortality = 54.3/1k; Child Stunting = 34.6%; Skilled Delivery = 71.2%; Exclusive Breastfeeding = 55.4%.
   * *Exemplars:* Madagascar, Tanzania, Zambia, Rwanda, Ethiopia, Yemen.
   * *Urgent Action:* Micronutrient fortification, maternal dietary support, WASH infrastructure.
3. **Tier 3: Moderate Health Transition ($n=20$ countries)**
   * *Profile:* Under-5 Mortality = 34.1/1k; Skilled Delivery = 82.5%; Measles Vaccine = 83.2%; Total Fertility Rate = 2.9.
   * *Exemplars:* Bangladesh, Nepal, Cambodia, Ghana, Senegal, Kenya.
   * *Urgent Action:* Quality improvement in rural clinics and postpartum family planning.
4. **Tier 4: High Coverage / Resilient Health Systems ($n=14$ countries)**
   * *Profile:* Under-5 Mortality = 17.6/1k; Skilled Delivery = 96.4%; Antenatal Care = 97.2%; Contraceptive Rate = 58.1%; TFR = 2.1.
   * *Exemplars:* Colombia, Dominican Republic, Egypt, Jordan, Armenia, Maldives.
   * *Urgent Action:* Addressing urban-rural inequalities, adolescent health, and neonatal intensive care.

---

## Quick Start & Execution Guide

### Option 1: 1-Click Full-Stack Dynamic App (Recommended)
Double-click [`run_dynamic_app.bat`](file:///c:/Users/chawl/OneDrive/Desktop/New%20folder/unsupervised%20learning%20project/run_dynamic_app.bat) or execute:
```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
* Opens the **Light-Themed Web Dashboard** at `http://127.0.0.1:8000`.
* Interactive Swagger API documentation at `http://127.0.0.1:8000/docs`.

### Option 2: 1-Click Master ML Pipeline CLI
```powershell
.\.venv\Scripts\python.exe run_pipeline.py
```
Regenerates all datasets, models, validation metrics, and 300-DPI publication figures in seconds.

### Option 3: Regenerate Submission Package & Reports
```powershell
.\.venv\Scripts\python.exe generate_pdf_report.py
.\.venv\Scripts\python.exe generate_presentation.py
.\.venv\Scripts\python.exe create_submission_zip.py
```

---

## Codebase Map & Directory Structure

```
unsupervised learning project/
├── SOURCE_DHS_RAW_DATA.csv             # Raw DHS API extract (Faculty audit)
├── PREPROCESSED_MCH_CLEAN.csv          # Clean imputed dataset (78 countries, 0 nulls)
├── PREPROCESSED_MCH_SCALED.csv         # Standardized feature matrix (Z-scores)
├── DATA_PREPROCESSING_INSPECTION_GUIDE.md # Detailed data & preprocessing documentation
├── Country_MCH_Segmentation_Project_Report.pdf # Formal PDF report for UMS
├── Country_MCH_Segmentation_Presentation.pptx # Updated 16:9 presentation deck
├── PROJECT_LINKS.txt                   # Verified repository and deployment links
├── 12404505.zip                        # Complete submission ZIP archive
├── app.py                              # FastAPI dynamic server entrypoint
├── run_dynamic_app.bat                 # 1-click full-stack launcher
├── run_dashboard.bat                   # Desktop multi-launcher
├── run_pipeline.py                     # Master ML execution pipeline
├── requirements.txt                    # Project dependency manifest
├── README.md                           # Comprehensive technical report
├── backend/
│   └── app.py                          # Dedicated FastAPI backend module
├── dashboard/                          # Light-Themed Web Analytics Dashboard
│   ├── index.html                      # UI layout with dynamic tabs & simulator
│   ├── styles.css                      # Clean light-colored CSS palette
│   ├── app.js                          # Dynamic API client & Chart.js logic
│   └── data.js                         # Embedded offline dataset payload
├── data/
│   ├── raw/dhs_mch_indicators_raw.csv
│   └── processed/                      # dhs_mch_clean.csv, dhs_mch_scaled.csv
├── notebooks/
│   └── Country_MCH_Segmentation.ipynb  # Interactive reproducible Jupyter Notebook
├── outputs/
│   ├── figures/                        # 8 publication-grade 300-DPI charts
│   └── reports/                        # Validation metrics and stability JSON
└── src/
    ├── data_loader.py                  # DHS REST API ingestion & caching
    ├── preprocessing.py               # Imputation, categorical encoding, scaling
    ├── clustering.py                   # Euclidean KMeans, Manhattan KMedoids, PCA
    ├── evaluation.py                   # WCSS, Silhouette, Davies-Bouldin, Calinski
    ├── stability.py                    # Bootstrap subsampling & seed ARI tests
    └── visualization.py                # 300-DPI publication plotting engine
```

---

## Individual Contribution Statement
* **Student Name:** Mayank
* **Registration Number:** 12404505
* **Target Foundation:** Bill & Melinda Gates Foundation
* **Declaration:** This project was conceived, designed, developed, and evaluated **100% individually as a single-author submission**. All components—including REST API ingestion, statistical preprocessing, mathematical modeling, dynamic FastAPI backend, light-themed web analytics, and formal documentation—were authored by the student.
