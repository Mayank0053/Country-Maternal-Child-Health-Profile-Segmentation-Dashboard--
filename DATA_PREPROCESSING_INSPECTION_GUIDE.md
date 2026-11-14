# Faculty Inspection Guide: Source Data & Preprocessing Pipeline
## Project: Country Maternal-Child Health Profile Segmentation Using Unsupervised Learning
### Organization / Problem Statement: Bill & Melinda Gates Foundation
### Individual Contributor: Mayank | Registration Number: 12404505

---

## 1. Overview for Faculty Review
This document provides a rigorous technical breakdown of the data sources, ingestion protocols, cleaning logic, missing value imputation strategy, categorical encoding, and feature standardization employed in this project.

All datasets have been placed **directly in the root directory** for rapid faculty verification and independent analysis:

| File in Root Directory | Description | Dimension | Status |
| :--- | :--- | :---: | :--- |
| **`SOURCE_DHS_RAW_DATA.csv`** | Direct raw extract from USAID DHS Program REST API | 84 rows × 19 cols | Raw, un-imputed survey totals |
| **`PREPROCESSED_MCH_CLEAN.csv`** | Clean, imputed, and categorized national health dataset | 78 rows × 26 cols | 0 nulls, clinically interpretable units |
| **`PREPROCESSED_MCH_SCALED.csv`** | Standardized feature matrix ready for unsupervised ML | 78 rows × 16 cols | Standard normal ($z = \frac{x - \mu}{\sigma}$) |

---

## 2. Source Data Provenance & API Ingestion
* **Primary Authority:** USAID Demographic and Health Surveys (DHS) Program open indicator repository.
* **REST API Endpoint:** `https://api.dhsprogram.com/rest/dhs/data`
* **Query Parameters:**
  - `indicatorIds`: 13 specific MCH indicator codes
  - `selectSurveys`: `latest` (guarantees the most recent nationally representative survey per country)
  - `f`: `json`
* **Metadata Enriched:** Country ISO-3 codes, DHS Geographic Regions (`Sub-Saharan Africa`, `South & Southeast Asia`, `Latin America & Caribbean`, `North Africa/West Asia/Europe`, `Central Asia`), and Survey Years.
* **National Totals Isolation:** Only records where `IsTotal == 1` and `CharacteristicCategory == 'Total'` were extracted to avoid sub-group contamination.

---

## 3. The 13 Core Maternal-Child Health Features

| # | Feature Name | Clinical Domain | Source Indicator ID | Unit | Clinical Significance |
| :---: | :--- | :--- | :--- | :---: | :--- |
| 1 | `Under5_Mortality_Rate` | Child Survival | `CM_ECMT_C_U5M` | Deaths / 1k live births | Core SDG 3.2 metric; measures overall child survival capacity |
| 2 | `Infant_Mortality_Rate` | Child Survival | `CM_ECMT_C_IMR` | Deaths / 1k live births | Deaths in first year of life; sensitive to sanitation & nutrition |
| 3 | `Neonatal_Mortality_Rate` | Child Survival | `CM_ECMT_C_NNR` | Deaths / 1k live births | Deaths in first 28 days; sensitive to intrapartum obstetric care |
| 4 | `Skilled_Birth_Attendance` | Maternal Care | `RH_DELA_C_SKP` | Percentage (%) | Delivery by doctor, nurse, or midwife; key maternal mortality reducer |
| 5 | `Antenatal_Care_Skilled_Provider` | Maternal Care | `RH_ANCP_W_SKP` | Percentage (%) | Early detection of pregnancy complications & pre-eclampsia |
| 6 | `Total_Fertility_Rate` | Reproductive | `FE_FRTR_W_TFR` | Births / woman | Lifetime fertility; correlates with demographic transition stage |
| 7 | `Adolescent_Fertility_Rate` | Reproductive | `FE_FRTR_W_A15` | Births / 1k teens (15-19) | High-risk obstetric outcomes & female educational attainment |
| 8 | `Modern_Contraceptive_Rate` | Family Planning | `FP_CUSM_W_MOD` | Percentage (%) | Family planning access among married/in-union women |
| 9 | `Child_Stunting_Rate` | Child Nutrition | `CN_NUTS_C_HA2` | Percentage (%) | Chronic malnutrition (Height-for-Age < -2 SD); cognitive deficit risk |
| 10 | `Child_Wasting_Rate` | Child Nutrition | `CN_NUTS_C_WH2` | Percentage (%) | Acute malnutrition (Weight-for-Height < -2 SD); immediate mortality risk |
| 11 | `Exclusive_Breastfeeding_Rate` | Infant Feeding | `CN_IYCB_C_EXB` | Percentage (%) | Infants <6m exclusively breastfed; provides maternal antibodies |
| 12 | `Measles_Vaccination_Rate` | Immunization | `CH_VACS_C_MSL` | Percentage (%) | Coverage among children 12-23m; key indicator of vaccine cold chains |
| 13 | `BCG_Vaccination_Rate` | Immunization | `CH_VACS_C_BCG` | Percentage (%) | Tuberculosis vaccine at birth; indicator of early primary healthcare contact |

---

## 4. Preprocessing Methodology & Scientific Justification

### A. Missingness Diagnosis & Sparse Survey Filtering
In international survey research, missing values occur under two distinct mechanisms:
1. **Structural Survey Non-Administration:** In specialized DHS surveys (e.g., AIDS Indicator Surveys [AIS] or Malaria Indicator Surveys [MIS]), anthropometric nutrition and child mortality modules are entirely omitted.
2. **Item-Level Non-Response:** Rare omissions in full DHS surveys due to localized data collection challenges.

**Filtering Rule:** Countries with $>50\%$ missing indicators were dropped because imputing more than half of a country's clinical profile would fabricate synthetic health systems. Six countries were filtered: `Cameroon`, `El Salvador`, `Liberia`, `Niger`, `Togo`, and `Uganda`. This left **78 robust national profiles**.

### B. Region-Stratified Median Imputation
Instead of simple mean or global median imputation (which would drag low-resource African nations toward global averages or vice-versa), we implemented **Region-Stratified Median Imputation**:
$$\hat{x}_{ij} = \text{median}(\{x_{kj} \mid \text{Region}(k) = \text{Region}(i), x_{kj} \text{ observed}\})$$

* **Why Regional?** Health infrastructure, disease burdens (e.g. malaria endemicity), and maternal mortality exhibit severe spatial autocorrelation. Imputing with the regional median preserves authentic epidemiological baselines.
* **Zero Remaining Nulls:** Any residual missing values where an entire region lacked an indicator were backfilled with the global median. Verified **0 remaining nulls** in `PREPROCESSED_MCH_CLEAN.csv`.

### C. Categorical Encoding of World Regions
Geographic region is a nominal categorical variable. It was encoded using **One-Hot Encoding** (`pd.get_dummies` / `OneHotEncoder`), creating explicit binary features (`Region_Sub-Saharan_Africa`, `Region_South_Asia`, etc.) for comparative regional profiling and supervised validation.

### D. Numerical Feature Standardization
The 13 indicators operate on vastly disparate mathematical scales:
* Mortality rates: $0 - 150+$ deaths per 1,000 live births
* Care and immunization rates: $0 - 100\%$
* Total fertility: $1.5 - 7.5$ children per woman

Without scaling, K-Means distance calculations would be completely dominated by high-variance mortality rates while ignoring fertility and wasting percentages. We applied standard z-score normalization:
$$z = \frac{x - \mu}{\sigma}$$
Resulting in zero mean and unit variance across all 13 features in `PREPROCESSED_MCH_SCALED.csv`.

---

## 5. Summary Statistics: Before vs. After Preprocessing

| Indicator | Raw Null Count (out of 84) | Clean Null Count (out of 78) | Mean (Clean) | Std Dev (Clean) | Min (Clean) | Max (Clean) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `Under5_Mortality_Rate` | 6 | **0** | 50.14 | 25.82 | 9.00 | 122.00 |
| `Infant_Mortality_Rate` | 6 | **0** | 37.62 | 17.41 | 8.00 | 81.00 |
| `Neonatal_Mortality_Rate`| 6 | **0** | 22.41 | 8.92 | 5.00 | 44.00 |
| `Skilled_Birth_Attendance`| 6 | **0** | 72.81 | 21.36 | 20.00 | 99.80 |
| `Antenatal_Care_Skilled` | 2 | **0** | 87.92 | 13.58 | 34.00 | 99.90 |
| `Total_Fertility_Rate` | 0 | **0** | 3.65 | 1.34 | 1.20 | 7.30 |
| `Adolescent_Fertility_Rate`| 0 | **0** | 78.42 | 41.21 | 5.00 | 192.00 |
| `Modern_Contraceptive_Rate`| 5 | **0** | 36.19 | 17.82 | 4.80 | 74.60 |
| `Child_Stunting_Rate` | 22 | **0** | 26.83 | 9.78 | 5.80 | 54.00 |
| `Child_Wasting_Rate` | 22 | **0** | 6.74 | 4.29 | 0.80 | 23.30 |
| `Exclusive_Breastfeeding` | 9 | **0** | 52.31 | 16.89 | 9.70 | 88.00 |
| `Measles_Vaccination` | 17 | **0** | 76.91 | 16.23 | 32.00 | 99.00 |
| `BCG_Vaccination` | 17 | **0** | 88.42 | 12.31 | 45.00 | 99.90 |

---

## 6. How the Faculty Can Run & Verify This Pipeline
1. **Interactive REST API & Web Dashboard:** Run `run_dynamic_app.bat` to launch the live FastAPI server at `http://127.0.0.1:8000` with interactive Swagger API docs at `/docs` and the live Light-Themed Dashboard.
2. **Independent CLI Execution:** Run `python run_pipeline.py` to regenerate all clean CSVs, figures, and validation reports from scratch in ~3 seconds.
3. **Interactive Python Inspection:** Open `notebooks/Country_MCH_Segmentation.ipynb` to step through the preprocessing and clustering cells interactively.
