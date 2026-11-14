"""
FastAPI Dynamic Backend Server for Country Maternal-Child Health Profile Segmentation.
Provides REST API endpoints for data inspection, dynamic on-the-fly clustering,
country health profile prediction, and metrics calculation.
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from scipy.spatial.distance import cdist

# Add project root to sys.path
CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(CURR_DIR, "data", "processed", "dhs_mch_scaled.csv")):
    ROOT_DIR = CURR_DIR
else:
    ROOT_DIR = os.path.abspath(os.path.join(CURR_DIR, ".."))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.preprocessing import MCH_NUMERICAL_FEATURES, scale_features
from src.clustering import ManhattanKMedoids, perform_pca_decomposition
from src.data_loader import INDICATOR_METADATA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FastAPIBackend")

# Initialize FastAPI App
app = FastAPI(
    title="Country Maternal-Child Health Segmentation API",
    description="Dynamic Backend API for DHS Program Maternal-Child Health Profile Segmentation & Unsupervised Machine Learning",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for cross-origin client support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data at startup
RAW_DATA_PATH = os.path.join(ROOT_DIR, "data", "raw", "dhs_mch_indicators_raw.csv")
CLEAN_DATA_PATH = os.path.join(ROOT_DIR, "data", "processed", "dhs_mch_clean.csv")
SCALED_DATA_PATH = os.path.join(ROOT_DIR, "data", "processed", "dhs_mch_scaled.csv")

raw_df = pd.read_csv(RAW_DATA_PATH) if os.path.exists(RAW_DATA_PATH) else pd.DataFrame()
clean_df = pd.read_csv(CLEAN_DATA_PATH) if os.path.exists(CLEAN_DATA_PATH) else pd.DataFrame()
scaled_df = pd.read_csv(SCALED_DATA_PATH) if os.path.exists(SCALED_DATA_PATH) else pd.DataFrame()

# Precompute baseline models
X_baseline = scaled_df[MCH_NUMERICAL_FEATURES].values if not scaled_df.empty else np.zeros((1, 13))
baseline_kmeans = KMeans(n_clusters=4, init="k-means++", n_init=50, random_state=42).fit(X_baseline)
baseline_pca = PCA(n_components=3, random_state=42).fit(X_baseline)

# Pydantic Schemas for Validation
class ClusterRequest(BaseModel):
    k: int = Field(default=4, ge=2, le=8, description="Number of clusters (k)")
    metric: str = Field(default="euclidean", description="Distance metric: euclidean or manhattan")
    features: Optional[List[str]] = Field(default=None, description="Subset of features to cluster on")

class PredictRequest(BaseModel):
    Under5_Mortality_Rate: float = Field(..., ge=0, le=250, description="Deaths per 1,000 live births")
    Infant_Mortality_Rate: Optional[float] = Field(default=None, ge=0, le=200)
    Neonatal_Mortality_Rate: Optional[float] = Field(default=None, ge=0, le=100)
    Skilled_Birth_Attendance: float = Field(..., ge=0, le=100, description="Percentage (%)")
    Antenatal_Care_Skilled_Provider: Optional[float] = Field(default=None, ge=0, le=100)
    Total_Fertility_Rate: float = Field(..., ge=0.5, le=10.0, description="Children per woman")
    Adolescent_Fertility_Rate: Optional[float] = Field(default=None, ge=0, le=300)
    Modern_Contraceptive_Rate: Optional[float] = Field(default=None, ge=0, le=100)
    Child_Stunting_Rate: float = Field(..., ge=0, le=100, description="Percentage (%)")
    Child_Wasting_Rate: Optional[float] = Field(default=None, ge=0, le=50)
    Exclusive_Breastfeeding_Rate: Optional[float] = Field(default=None, ge=0, le=100)
    Measles_Vaccination_Rate: Optional[float] = Field(default=None, ge=0, le=100)
    BCG_Vaccination_Rate: Optional[float] = Field(default=None, ge=0, le=100)

def assign_typology_names(profiles_df: pd.DataFrame) -> Dict[int, str]:
    """Dynamically assign public health typologies based on cluster U5MR rankings."""
    sorted_clusters = profiles_df["Under5_Mortality_Rate"].sort_values(ascending=False).index.tolist()
    names = {}
    if len(sorted_clusters) == 4:
        names[sorted_clusters[0]] = "High-Burden / Urgent Priority"
        names[sorted_clusters[1]] = "Nutritional & Mortality Vulnerability"
        names[sorted_clusters[2]] = "Moderate Health Transition"
        names[sorted_clusters[3]] = "High Coverage / Resilient Health Systems"
    elif len(sorted_clusters) == 3:
        names[sorted_clusters[0]] = "High-Burden / Critical Priority"
        names[sorted_clusters[1]] = "Moderate Health Transition"
        names[sorted_clusters[2]] = "High Coverage / Resilient Primary Care"
    else:
        for idx, c in enumerate(sorted_clusters):
            names[c] = f"Health Profile Tier {idx + 1}"
    return names

# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------

@app.get("/api/status", tags=["System Status"])
def get_system_status():
    """Returns dynamic server status, dataset dimensions, and ML readiness."""
    return {
        "status": "online",
        "backend_mode": "FastAPI Dynamic Server",
        "total_countries_analyzed": len(clean_df),
        "total_features": len(MCH_NUMERICAL_FEATURES),
        "dataset_loaded": not clean_df.empty,
        "default_k": 4,
        "available_metrics": ["euclidean", "manhattan"],
        "api_documentation": "/docs"
    }

@app.get("/api/data/source", tags=["Faculty Data Inspection"])
def get_source_raw_data(
    region: Optional[str] = Query(None, description="Filter by DHS Region"),
    search: Optional[str] = Query(None, description="Search by Country Name"),
    limit: int = Query(100, ge=1, le=200)
):
    """
    Returns the exact un-imputed raw DHS source survey indicator records
    as fetched directly from the USAID DHS REST API.
    """
    if raw_df.empty:
        raise HTTPException(status_code=404, detail="Raw dataset not found on server.")
    
    df_filtered = raw_df.copy()
    if region and "RegionName" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["RegionName"].str.contains(region, case=False, na=False)]
    if search and "CountryName" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["CountryName"].str.contains(search, case=False, na=False)]
        
    records = df_filtered.head(limit).replace({np.nan: None}).to_dict(orient="records")
    
    # Calculate null statistics per indicator
    null_counts = {col: int(raw_df[col].isna().sum()) for col in MCH_NUMERICAL_FEATURES if col in raw_df.columns}
    
    return {
        "dataset_type": "Source Raw DHS Indicator Survey Data",
        "source_api": "https://api.dhsprogram.com/rest/dhs/data",
        "total_records": len(df_filtered),
        "raw_null_counts": null_counts,
        "records": records
    }

@app.get("/api/data/preprocessed", tags=["Faculty Data Inspection"])
def get_preprocessed_clean_data(
    region: Optional[str] = Query(None, description="Filter by DHS Region"),
    search: Optional[str] = Query(None, description="Search by Country Name"),
    limit: int = Query(100, ge=1, le=200)
):
    """
    Returns the cleaned, imputed, and categorical encoded national health dataset
    with zero remaining nulls in original clinical units.
    """
    if clean_df.empty:
        raise HTTPException(status_code=404, detail="Clean dataset not found on server.")
        
    df_filtered = clean_df.copy()
    if region and "RegionName" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["RegionName"].str.contains(region, case=False, na=False)]
    if search and "CountryName" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["CountryName"].str.contains(search, case=False, na=False)]
        
    records = df_filtered.head(limit).replace({np.nan: None}).to_dict(orient="records")
    summary_stats = clean_df[MCH_NUMERICAL_FEATURES].describe().T[["mean", "std", "min", "50%", "max"]].to_dict(orient="index")
    
    return {
        "dataset_type": "Preprocessed & Imputed MCH Dataset",
        "imputation_method": "Region-Stratified Median Imputation",
        "remaining_nulls": int(clean_df[MCH_NUMERICAL_FEATURES].isna().sum().sum()),
        "total_countries": len(df_filtered),
        "summary_statistics": summary_stats,
        "records": records
    }

@app.get("/api/data/scaled", tags=["Faculty Data Inspection"])
def get_preprocessed_scaled_data():
    """Returns the standardized feature matrix with zero mean and unit variance (z-scores)."""
    if scaled_df.empty:
        raise HTTPException(status_code=404, detail="Scaled dataset not found.")
    return {
        "dataset_type": "Standardized Feature Matrix (StandardScaler)",
        "scaling_formula": "z = (x - mean) / std",
        "features": MCH_NUMERICAL_FEATURES,
        "records": scaled_df.replace({np.nan: None}).to_dict(orient="records")
    }

@app.post("/api/cluster/run", tags=["Dynamic ML Clustering"])
def run_dynamic_clustering(req: ClusterRequest):
    """
    Executes real-time dynamic clustering on the server with user-defined parameters:
    number of clusters k, distance metric (euclidean/manhattan), and custom features.
    """
    features = req.features if req.features else MCH_NUMERICAL_FEATURES
    for f in features:
        if f not in clean_df.columns:
            raise HTTPException(status_code=400, detail=f"Feature '{f}' not recognized.")
            
    # Extract feature matrix and scale
    X = scaled_df[features].values
    k = req.k
    metric = req.metric.lower()
    
    # Run dynamic clustering
    if metric == "manhattan":
        model = ManhattanKMedoids(n_clusters=k, random_state=42).fit(X)
        labels = model.labels_.tolist()
        wcss = float(model.inertia_)
    else:
        model = KMeans(n_clusters=k, init="k-means++", n_init=30, random_state=42).fit(X)
        labels = model.labels_.tolist()
        wcss = float(model.inertia_)
        
    # Dynamic Validation Metrics
    sil_euclidean = float(silhouette_score(X, labels, metric="euclidean"))
    sil_manhattan = float(silhouette_score(X, labels, metric="manhattan"))
    db_index = float(davies_bouldin_score(X, labels))
    ch_score = float(calinski_harabasz_score(X, labels))
    
    # Compute dynamic PCA biplot coordinates
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X)
    explained_variance = [float(v) * 100 for v in pca.explained_variance_ratio_]
    
    # Attach labels to working copy
    df_work = clean_df.copy()
    df_work["Cluster"] = labels
    
    # Dynamic cluster profiles
    profiles_df = df_work.groupby("Cluster")[MCH_NUMERICAL_FEATURES].mean()
    typologies = assign_typology_names(profiles_df)
    
    # Build country items with dynamic cluster and PCA coordinates
    countries_output = []
    for idx, row in df_work.reset_index(drop=True).iterrows():
        c_label = int(labels[idx])
        countries_output.append({
            "name": row["CountryName"],
            "region": row.get("RegionName", "Unknown"),
            "year": int(row["Latest_Survey_Year"]) if pd.notna(row.get("Latest_Survey_Year")) else None,
            "cluster": c_label,
            "cluster_name": typologies.get(c_label, f"Cluster {c_label + 1}"),
            "pca_x": float(X_pca[idx, 0]),
            "pca_y": float(X_pca[idx, 1]),
            "indicators": {feat: float(row[feat]) for feat in MCH_NUMERICAL_FEATURES}
        })
        
    return {
        "status": "success",
        "parameters": {
            "k": k,
            "distance_metric": metric,
            "features_used": features
        },
        "metrics": {
            "wcss_inertia": round(wcss, 2),
            "silhouette_euclidean": round(sil_euclidean, 4),
            "silhouette_manhattan": round(sil_manhattan, 4),
            "davies_bouldin_index": round(db_index, 4),
            "calinski_harabasz_score": round(ch_score, 2),
            "pca_explained_variance_pct": [round(v, 2) for v in explained_variance]
        },
        "cluster_typologies": {str(k_id): name for k_id, name in typologies.items()},
        "cluster_profiles": profiles_df.to_dict(orient="index"),
        "countries": countries_output
    }

@app.post("/api/predict", tags=["Country Profile Simulator"])
def predict_country_archetype(req: PredictRequest):
    """
    Simulates and predicts the maternal-child health cluster assignment
    for a hypothetical or newly surveyed country.
    """
    # Fill defaults with clean dataset medians if omitted
    input_dict = req.dict()
    full_vector = []
    for feat in MCH_NUMERICAL_FEATURES:
        val = input_dict.get(feat)
        if val is None:
            val = float(clean_df[feat].median())
        full_vector.append(val)
        
    # Scale input using baseline parameters
    means = clean_df[MCH_NUMERICAL_FEATURES].mean().values
    stds = clean_df[MCH_NUMERICAL_FEATURES].std().values
    scaled_vector = (np.array(full_vector) - means) / stds
    scaled_matrix = scaled_vector.reshape(1, -1)
    
    # Predict with baseline model
    pred_cluster = int(baseline_kmeans.predict(scaled_matrix)[0])
    
    # Compute distances to all 4 centroids
    centroids = baseline_kmeans.cluster_centers_
    distances = cdist(scaled_matrix, centroids, metric="euclidean")[0].tolist()
    
    # Project into baseline PCA space
    pca_coords = baseline_pca.transform(scaled_matrix)[0].tolist()
    
    profiles_df = clean_df.groupby("Cluster_k4")[MCH_NUMERICAL_FEATURES].mean() if "Cluster_k4" in clean_df.columns else clean_df.groupby(baseline_kmeans.labels_)[MCH_NUMERICAL_FEATURES].mean()
    typologies = assign_typology_names(profiles_df)
    cluster_name = typologies.get(pred_cluster, f"Cluster {pred_cluster + 1}")
    
    # Clinical intervention recommendations
    recommendations = []
    if full_vector[0] > 70 or full_vector[3] < 50:
        recommendations.append("Priority 1: Immediate expansion of Emergency Obstetric and Newborn Care (EmONC) facilities.")
        recommendations.append("Priority 2: Train and deploy community health worker cadres for active maternal surveillance.")
    if full_vector[8] > 30:
        recommendations.append("Priority 3: Multi-sectoral childhood stunting prevention and maternal dietary supplementation.")
    if full_vector[7] < 25:
        recommendations.append("Priority 4: Remove legal and logistical barriers to modern family planning commodities.")
    if not recommendations:
        recommendations.append("Maintain high-coverage primary care and address subnational urban-rural disparities.")
        
    return {
        "predicted_cluster_id": pred_cluster + 1,
        "assigned_typology": cluster_name,
        "pca_projection": {
            "pc1": round(pca_coords[0], 3),
            "pc2": round(pca_coords[1], 3),
            "pc3": round(pca_coords[2], 3)
        },
        "centroid_distances": [round(d, 3) for d in distances],
        "clinical_action_recommendations": recommendations,
        "input_indicators_analyzed": dict(zip(MCH_NUMERICAL_FEATURES, full_vector))
    }

@app.get("/api/export/{dataset_type}", tags=["Faculty Data Inspection"])
def export_dataset_csv(dataset_type: str):
    """Directly downloads raw, clean, or scaled CSV datasets."""
    file_map = {
        "raw": os.path.join(ROOT_DIR, "SOURCE_DHS_RAW_DATA.csv"),
        "clean": os.path.join(ROOT_DIR, "PREPROCESSED_MCH_CLEAN.csv"),
        "scaled": os.path.join(ROOT_DIR, "PREPROCESSED_MCH_SCALED.csv")
    }
    target = file_map.get(dataset_type.lower())
    if not target or not os.path.exists(target):
        raise HTTPException(status_code=404, detail="Requested file not found on server.")
    return FileResponse(target, media_type="text/csv", filename=os.path.basename(target))

# Mount frontend dashboard
DASHBOARD_DIR = os.path.join(ROOT_DIR, "dashboard")
if os.path.exists(DASHBOARD_DIR):
    app.mount("/", StaticFiles(directory=DASHBOARD_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
