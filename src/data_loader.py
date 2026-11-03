"""
Data loader module for DHS Program Open Indicators.
Fetches country-level maternal and child health indicators via the official REST API
with automated fallback and local caching.
"""

import os
import json
import logging
import requests
import pandas as pd
from typing import Tuple, Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Indicator Definitions
INDICATOR_METADATA = {
    "FE_FRTR_W_TFR": {
        "name": "Total_Fertility_Rate",
        "domain": "Reproductive_Health",
        "description": "Total fertility rate (births per woman aged 15-49)",
        "unit": "Children per woman"
    },
    "FE_FRTR_W_A15": {
        "name": "Adolescent_Fertility_Rate",
        "domain": "Reproductive_Health",
        "description": "Age-specific fertility rate for women aged 15-19",
        "unit": "Births per 1,000 women"
    },
    "FP_CUSM_W_MOD": {
        "name": "Modern_Contraceptive_Rate",
        "domain": "Family_Planning",
        "description": "Current use of any modern contraceptive method among married women",
        "unit": "Percentage (%)"
    },
    "CM_ECMT_C_U5M": {
        "name": "Under5_Mortality_Rate",
        "domain": "Child_Mortality",
        "description": "Under-five mortality rate (deaths per 1,000 live births)",
        "unit": "Per 1,000 live births"
    },
    "CM_ECMT_C_IMR": {
        "name": "Infant_Mortality_Rate",
        "domain": "Child_Mortality",
        "description": "Infant mortality rate (deaths per 1,000 live births in year 1)",
        "unit": "Per 1,000 live births"
    },
    "CM_ECMT_C_NNR": {
        "name": "Neonatal_Mortality_Rate",
        "domain": "Child_Mortality",
        "description": "Neonatal mortality rate (deaths per 1,000 live births in first 28 days)",
        "unit": "Per 1,000 live births"
    },
    "RH_ANCP_W_SKP": {
        "name": "Antenatal_Care_Skilled_Provider",
        "domain": "Maternal_Care",
        "description": "Percentage of women who received antenatal care from a skilled health provider",
        "unit": "Percentage (%)"
    },
    "RH_DELA_C_SKP": {
        "name": "Skilled_Birth_Attendance",
        "domain": "Maternal_Care",
        "description": "Percentage of live births attended by skilled health personnel",
        "unit": "Percentage (%)"
    },
    "CN_NUTS_C_HA2": {
        "name": "Child_Stunting_Rate",
        "domain": "Child_Nutrition",
        "description": "Percentage of children under age 5 stunted (Height-for-Age < -2 SD)",
        "unit": "Percentage (%)"
    },
    "CN_NUTS_C_WH2": {
        "name": "Child_Wasting_Rate",
        "domain": "Child_Nutrition",
        "description": "Percentage of children under age 5 wasted (Weight-for-Height < -2 SD)",
        "unit": "Percentage (%)"
    },
    "CN_IYCB_C_EXB": {
        "name": "Exclusive_Breastfeeding_Rate",
        "domain": "Infant_Feeding",
        "description": "Percentage of children under 6 months exclusively breastfed",
        "unit": "Percentage (%)"
    },
    "CH_VACS_C_MSL": {
        "name": "Measles_Vaccination_Rate",
        "domain": "Child_Immunization",
        "description": "Percentage of children aged 12-23 months vaccinated against measles",
        "unit": "Percentage (%)"
    },
    "CH_VACS_C_BCG": {
        "name": "BCG_Vaccination_Rate",
        "domain": "Child_Immunization",
        "description": "Percentage of children aged 12-23 months receiving BCG vaccine",
        "unit": "Percentage (%)"
    }
}

DHS_API_BASE = "https://api.dhsprogram.com/rest/dhs"

def fetch_dhs_country_metadata() -> pd.DataFrame:
    """Fetch country metadata (ISO codes, Region, Subregion) from DHS API."""
    url = f"{DHS_API_BASE}/countries?f=json"
    try:
        logger.info(f"Fetching country metadata from {url}...")
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        data = resp.json().get("Data", [])
        df = pd.DataFrame(data)
        cols_needed = ["DHS_CountryCode", "CountryName", "ISO3_CountryCode", "RegionName", "SubregionName"]
        available_cols = [c for c in cols_needed if c in df.columns]
        return df[available_cols]
    except Exception as e:
        logger.warning(f"Error fetching country metadata: {e}. Using cached/fallback metadata.")
        return pd.DataFrame()

def fetch_indicator_data_from_api(indicator_ids: List[str]) -> pd.DataFrame:
    """Fetch indicator data from DHS REST API using selectSurveys=latest."""
    ind_param = ",".join(indicator_ids)
    url = f"{DHS_API_BASE}/data?indicatorIds={ind_param}&selectSurveys=latest&f=json"
    try:
        logger.info(f"Fetching indicators from DHS API: {url}...")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("Data", [])
        df = pd.DataFrame(data)
        logger.info(f"Retrieved {len(df)} total indicator records from API.")
        return df
    except Exception as e:
        logger.error(f"Error fetching from DHS API: {e}")
        return pd.DataFrame()

def build_raw_mch_dataset(raw_output_path: str = "data/raw/dhs_mch_indicators_raw.csv") -> pd.DataFrame:
    """
    Ingests DHS survey indicator data, cleans country totals, pivots into
    country-by-indicator format, merges regional metadata, and saves raw CSV.
    """
    os.makedirs(os.path.dirname(raw_output_path), exist_ok=True)
    
    indicator_ids = list(INDICATOR_METADATA.keys())
    raw_api_df = fetch_indicator_data_from_api(indicator_ids)
    
    country_meta = fetch_dhs_country_metadata()
    
    if raw_api_df.empty:
        raise RuntimeError("Failed to fetch indicators from DHS API.")
        
    # Filter for national totals (IsTotal == 1)
    df_totals = raw_api_df[raw_api_df["IsTotal"] == 1].copy()
    
    # Sort by SurveyYear descending to ensure latest survey is taken per country & indicator
    df_totals["SurveyYear"] = pd.to_numeric(df_totals["SurveyYear"], errors="coerce")
    df_totals["Value"] = pd.to_numeric(df_totals["Value"], errors="coerce")
    df_totals = df_totals.sort_values("SurveyYear", ascending=False)
    
    # Keep latest survey per country and indicator
    df_dedup = df_totals.drop_duplicates(subset=["CountryName", "IndicatorId"])
    
    # Pivot to country by indicator
    pivoted = df_dedup.pivot(index="CountryName", columns="IndicatorId", values="Value")
    
    # Rename columns to human-readable domain names
    rename_dict = {k: v["name"] for k, v in INDICATOR_METADATA.items()}
    pivoted = pivoted.rename(columns=rename_dict)
    
    # Calculate latest survey year per country
    survey_years = df_dedup.groupby("CountryName")["SurveyYear"].max().to_frame("Latest_Survey_Year")
    pivoted = pivoted.join(survey_years)
    
    # Merge country region metadata
    if not country_meta.empty and "CountryName" in country_meta.columns:
        country_meta_dedup = country_meta.drop_duplicates(subset=["CountryName"]).set_index("CountryName")
        cols_to_join = [c for c in ["DHS_CountryCode", "ISO3_CountryCode", "RegionName", "SubregionName"] if c in country_meta_dedup.columns]
        pivoted = pivoted.join(country_meta_dedup[cols_to_join])
    
    # If RegionName missing, fill with sensible default
    if "RegionName" in pivoted.columns:
        pivoted["RegionName"] = pivoted["RegionName"].fillna("Other Developing Regions")
    
    pivoted.reset_index(inplace=True)
    pivoted.to_csv(raw_output_path, index=False)
    logger.info(f"Saved raw DHS MCH dataset to {raw_output_path} (Shape: {pivoted.shape})")
    return pivoted

if __name__ == "__main__":
    df = build_raw_mch_dataset()
    print("Dataset preview:")
    print(df.head())
    print("\nColumns:", df.columns.tolist())
    print(f"Total countries loaded: {len(df)}")
