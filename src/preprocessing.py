"""
Preprocessing module for Country Maternal-Child Health Profile Segmentation.
Implements missing value handling (region-stratified median imputation),
categorical encoding of geographic regions, and feature standardization.
"""

import os
import logging
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any
from sklearn.preprocessing import StandardScaler, RobustScaler, OneHotEncoder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MCH_NUMERICAL_FEATURES = [
    "Under5_Mortality_Rate",
    "Infant_Mortality_Rate",
    "Neonatal_Mortality_Rate",
    "Total_Fertility_Rate",
    "Adolescent_Fertility_Rate",
    "Antenatal_Care_Skilled_Provider",
    "Skilled_Birth_Attendance",
    "Modern_Contraceptive_Rate",
    "Child_Stunting_Rate",
    "Child_Wasting_Rate",
    "Exclusive_Breastfeeding_Rate",
    "Measles_Vaccination_Rate",
    "BCG_Vaccination_Rate"
]

CATEGORICAL_FEATURES = ["RegionName"]

ID_METADATA_COLS = ["CountryName", "DHS_CountryCode", "ISO3_CountryCode", "Latest_Survey_Year", "RegionName"]

def handle_missing_values(df: pd.DataFrame, 
                          max_missing_ratio: float = 0.50,
                          region_col: str = "RegionName") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Handles missing values using a two-tier domain-informed approach:
    1. Filter out countries with missing values exceeding max_missing_ratio.
    2. Impute remaining missing values using Region-stratified median.
    3. Backfill any edge cases with global feature median.
    """
    logger.info("Executing missing value management...")
    working_df = df.copy()
    
    # 1. Filter sparse countries
    missing_counts = working_df[MCH_NUMERICAL_FEATURES].isna().sum(axis=1)
    missing_ratio = missing_counts / len(MCH_NUMERICAL_FEATURES)
    valid_mask = missing_ratio <= max_missing_ratio
    dropped_countries = working_df.loc[~valid_mask, "CountryName"].tolist()
    
    if dropped_countries:
        logger.info(f"Filtered {len(dropped_countries)} countries with >{int(max_missing_ratio*100)}% missing values: {dropped_countries}")
    
    filtered_df = working_df[valid_mask].copy()
    
    # Track pre-imputation null statistics
    null_stats = filtered_df[MCH_NUMERICAL_FEATURES].isna().sum().to_dict()
    
    # 2. Region-stratified median imputation
    imputed_df = filtered_df.copy()
    if region_col in imputed_df.columns:
        for feat in MCH_NUMERICAL_FEATURES:
            # Calculate region medians
            region_medians = imputed_df.groupby(region_col)[feat].transform("median")
            imputed_df[feat] = imputed_df[feat].fillna(region_medians)
    
    # 3. Global median fallback for features where an entire region was missing
    for feat in MCH_NUMERICAL_FEATURES:
        global_median = imputed_df[feat].median()
        imputed_df[feat] = imputed_df[feat].fillna(global_median)
        
    remaining_nulls = imputed_df[MCH_NUMERICAL_FEATURES].isna().sum().sum()
    logger.info(f"Imputation completed. Remaining nulls: {remaining_nulls}")
    
    metadata = {
        "dropped_countries": dropped_countries,
        "initial_null_stats": null_stats,
        "final_country_count": len(imputed_df)
    }
    
    return imputed_df, metadata

def encode_categorical_features(df: pd.DataFrame,
                                cat_cols: List[str] = CATEGORICAL_FEATURES) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Encodes categorical geographic variables using One-Hot Encoding.
    Returns the dataframe with one-hot encoded columns and the standalone encoded dataframe.
    """
    logger.info(f"Encoding categorical features: {cat_cols}")
    df_encoded = df.copy()
    
    ohe = OneHotEncoder(sparse_output=False, drop=None, handle_unknown="ignore")
    cat_data = df_encoded[cat_cols].fillna("Unknown")
    ohe_matrix = ohe.fit_transform(cat_data)
    ohe_col_names = [f"Region_{cat.replace(' ', '_').replace('&', 'and')}" for cat in ohe.get_feature_names_out(cat_cols)]
    
    ohe_df = pd.DataFrame(ohe_matrix, columns=ohe_col_names, index=df_encoded.index)
    df_combined = pd.concat([df_encoded, ohe_df], axis=1)
    
    return df_combined, ohe_df

def scale_features(df: pd.DataFrame, 
                   feature_cols: List[str] = MCH_NUMERICAL_FEATURES,
                   scaler_type: str = "standard") -> Tuple[pd.DataFrame, Any]:
    """
    Scales numerical features using StandardScaler (zero mean, unit variance)
    or RobustScaler (median and interquartile range).
    """
    logger.info(f"Scaling numerical features using {scaler_type} scaler...")
    if scaler_type.lower() == "robust":
        scaler = RobustScaler()
    else:
        scaler = StandardScaler()
        
    scaled_matrix = scaler.fit_transform(df[feature_cols])
    scaled_df = pd.DataFrame(scaled_matrix, columns=feature_cols, index=df.index)
    return scaled_df, scaler

def run_preprocessing_pipeline(raw_csv_path: str = "data/raw/dhs_mch_indicators_raw.csv",
                               clean_output_path: str = "data/processed/dhs_mch_clean.csv",
                               scaled_output_path: str = "data/processed/dhs_mch_scaled.csv") -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Executes full preprocessing: missing value imputation, categorical encoding,
    and feature standardization, saving clean and scaled datasets.
    """
    os.makedirs(os.path.dirname(clean_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(scaled_output_path), exist_ok=True)
    
    raw_df = pd.read_csv(raw_csv_path)
    logger.info(f"Loaded raw dataset from {raw_csv_path} with shape {raw_df.shape}")
    
    # 1. Handle missing values
    imputed_df, missing_meta = handle_missing_values(raw_df)
    
    # 2. Encode categorical variables
    imputed_df, ohe_df = encode_categorical_features(imputed_df)
    
    # 3. Standardize numerical features
    scaled_df, scaler = scale_features(imputed_df, MCH_NUMERICAL_FEATURES, scaler_type="standard")
    
    # Attach identifiers for downstream traceability
    for col in ["CountryName", "RegionName", "Latest_Survey_Year"]:
        if col in imputed_df.columns:
            scaled_df[col] = imputed_df[col]
            
    # Save processed outputs
    imputed_df.to_csv(clean_output_path, index=False)
    scaled_df.to_csv(scaled_output_path, index=False)
    
    logger.info(f"Clean unscaled dataset saved to {clean_output_path}")
    logger.info(f"Scaled dataset saved to {scaled_output_path}")
    
    return imputed_df, scaled_df, missing_meta

if __name__ == "__main__":
    from data_loader import build_raw_mch_dataset
    build_raw_mch_dataset()
    clean_df, scaled_df, meta = run_preprocessing_pipeline()
    print("Preprocessing successful!")
    print(f"Countries processed: {len(clean_df)}")
    print("Clean summary:")
    print(clean_df[MCH_NUMERICAL_FEATURES].describe().T[["mean", "std", "min", "50%", "max"]])
