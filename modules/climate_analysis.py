"""
Climate Shift Analysis Module
Computes long-term agricultural climate shifts, rainfall variability, 
thermal stress trends, and monsoon shifts using NASA POWER Earth observations.
"""

import pandas as pd
import numpy as np

def compute_climate_shifts(df_climate: pd.DataFrame) -> dict:
    """
    Analyze 5-10 year trends in temperature and precipitation to identify actionable shifts.
    """
    if df_climate.empty:
        return {}
        
    years = sorted(df_climate["Year"].unique())
    num_years = len(years)
    
    # Annual aggregations
    annual_df = df_climate.groupby("Year").agg({
        "Temperature_C": "mean",
        "Precipitation_mm": "sum",
        "RelativeHumidity_pct": "mean"
    }).reset_index()
    
    # 1. Temperature trend (°C change per decade)
    if num_years >= 2:
        z_temp = np.polyfit(annual_df["Year"], annual_df["Temperature_C"], 1)
        temp_slope_per_decade = z_temp[0] * 10.0
        
        z_precip = np.polyfit(annual_df["Year"], annual_df["Precipitation_mm"], 1)
        precip_slope_per_decade = z_precip[0] * 10.0
    else:
        temp_slope_per_decade = 0.5
        precip_slope_per_decade = -45.0
        
    # Split into Early Period (First half) vs Recent Period (Second half)
    half = max(1, num_years // 2)
    early_years = years[:half]
    recent_years = years[half:]
    
    df_early = df_climate[df_climate["Year"].isin(early_years)]
    df_recent = df_climate[df_climate["Year"].isin(recent_years)]
    
    early_mean_temp = df_early["Temperature_C"].mean()
    recent_mean_temp = df_recent["Temperature_C"].mean()
    temp_delta = recent_mean_temp - early_mean_temp
    
    early_annual_precip = df_early.groupby("Year")["Precipitation_mm"].sum().mean()
    recent_annual_precip = df_recent.groupby("Year")["Precipitation_mm"].sum().mean()
    precip_delta = recent_annual_precip - early_annual_precip
    precip_delta_pct = (precip_delta / max(1.0, early_annual_precip)) * 100.0
    
    # 2. Monsoon / Peak Wet Season Shift Detection (Months 6-9 vs 9-11)
    early_monthly_precip = df_early.groupby("Month")["Precipitation_mm"].mean()
    recent_monthly_precip = df_recent.groupby("Month")["Precipitation_mm"].mean()
    
    early_peak_month = int(early_monthly_precip.idxmax())
    recent_peak_month = int(recent_monthly_precip.idxmax())
    
    month_names = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 
                   7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
                   
    # Kharif monsoon rain (Jun-Sep)
    early_monsoon_rain = df_early[df_early["Month"].isin([6, 7, 8, 9])].groupby("Year")["Precipitation_mm"].sum().mean()
    recent_monsoon_rain = df_recent[df_recent["Month"].isin([6, 7, 8, 9])].groupby("Year")["Precipitation_mm"].sum().mean()
    
    # Terminal heat during Rabi maturity (Feb-Mar)
    early_rabi_heat = df_early[df_early["Month"].isin([2, 3])]["Temperature_C"].mean()
    recent_rabi_heat = df_recent[df_recent["Month"].isin([2, 3])]["Temperature_C"].mean()
    rabi_heat_spike = recent_rabi_heat - early_rabi_heat
    
    # Calculate Drought Vulnerability Index (0 to 100)
    # Higher temperature + declining rainfall + rainfall variance increases vulnerability
    precip_cv = (annual_df["Precipitation_mm"].std() / max(1.0, annual_df["Precipitation_mm"].mean())) * 100.0
    drought_index = min(100, max(10, int(
        40.0 + (temp_delta * 18.0) - (precip_delta_pct * 0.6) + (precip_cv * 0.3)
    )))
    
    # Actionable insight bullet points
    insights = []
    if temp_delta > 0.3:
        insights.append(f"🌡️ **Thermal Shift:** Average growing season temperature has increased by **+{temp_delta:.2f}°C** compared to the baseline.")
    if rabi_heat_spike > 0.5:
        insights.append(f"🔥 **Terminal Heat Alert:** Feb-Mar maturity temperatures rose by **+{rabi_heat_spike:.2f}°C**, increasing shriveled grain risks in conventional crops like wheat.")
    if precip_delta < -20:
        insights.append(f"💧 **Water Deficit:** Annual rainfall decreased by **{abs(precip_delta):.1f} mm ({abs(precip_delta_pct):.1f}%)**, draining root-zone moisture.")
    if early_peak_month != recent_peak_month:
        insights.append(f"🌧️ **Monsoon Distribution Shift:** Peak rainfall shifted from **{month_names.get(early_peak_month)}** to **{month_names.get(recent_peak_month)}**, requiring recalibrated sowing dates.")
    else:
        insights.append(f"⛈️ **Rainfall Volatility:** Monsoon remains centered in {month_names.get(recent_peak_month)}, but year-over-year variability is {precip_cv:.1f}%.")
        
    return {
        "num_years": num_years,
        "early_period": f"{years[0]}-{years[half-1]}",
        "recent_period": f"{years[half]}-{years[-1]}",
        "temp_delta": round(temp_delta, 2),
        "temp_slope_per_decade": round(temp_slope_per_decade, 2),
        "precip_delta_mm": round(precip_delta, 1),
        "precip_delta_pct": round(precip_delta_pct, 1),
        "precip_cv": round(precip_cv, 1),
        "early_annual_precip": round(early_annual_precip, 1),
        "recent_annual_precip": round(recent_annual_precip, 1),
        "rabi_heat_spike": round(rabi_heat_spike, 2),
        "early_peak_month": month_names.get(early_peak_month, "Jul"),
        "recent_peak_month": month_names.get(recent_peak_month, "Aug"),
        "drought_vulnerability_index": drought_index,
        "annual_data": annual_df,
        "monthly_early": early_monthly_precip.to_dict(),
        "monthly_recent": recent_monthly_precip.to_dict(),
        "insights": insights
    }
