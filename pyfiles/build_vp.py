import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np
from pathlib import Path
from typing import Sequence, Optional

def time_inputs(start: str, end: str):
    s = pd.to_datetime(start)
    e = pd.to_datetime(end)

    e_eff = e - pd.Timedelta(nanoseconds=1)

    years = list(range(s.year, e_eff.year + 1))
    single_year = (len(years) == 1)
    year_label = str(years[0]) if single_year else f"{years[0]}-{years[-1]}"

    return years, single_year, year_label
    

def build_variation_pattern(
    value_columns: Sequence[str], 
    weights = False,
    name = str,
    save = False,
    start = str,
    end = str,
    single_year = str,
    year_label = str
):

    base = "https://api.energidataservice.dk/dataset/ProductionConsumptionSettlement"

    params = {
        "start": start,
        "end": end,
        "timezone": "UTC",
        "columns": "HourUTC,PriceArea," + ",".join(value_columns),
        "sort": "HourUTC asc",
        "limit": 0,
    }

    r = requests.get(base, params=params, timeout=60)
    r.raise_for_status()
    df = pd.DataFrame(r.json().get("records", []))

    df["HourUTC"] = pd.to_datetime(df["HourUTC"])
    df = df.loc[~((df["HourUTC"].dt.month == 2) & (df["HourUTC"].dt.day == 29))].copy()

    # combine selected value columns into one value series
    for c in value_columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["value"] = df[list(value_columns)].sum(axis=1, min_count=1)  # ignores all-NaN rows

    # DK total by hour
    df_dk = df.groupby("HourUTC")["value"].sum()

    # multi-year typical-hour profile
    if not single_year:
        template = pd.date_range("2021-01-01 00:00", periods=8760, freq="h")
        key = template.strftime("%m-%d %H")
        df_dk = (
            df_dk.groupby(df_dk.index.strftime("%m-%d %H")).mean()
            .reindex(key)
            .reset_index(drop=True)
        )
    else:
        df_dk = df_dk.reset_index(drop=True)

    # add extra day
    df_dk_8784 = pd.concat([df_dk, df_dk.iloc[:24]], ignore_index=True)

    # save
    if save:
        out = fr'..\ZipEnergyPLAN163\energyPlan Data\Distributions\{year_label}_{name}.txt'
        df_dk_8784.to_csv(out, sep="\t", index=False, header=False)

    # shares (weighted by combined value)
    if weights:
        total = df["value"].sum()
        s_DK1 = df.loc[df["PriceArea"] == "DK1", "value"].sum() / total if total else 0.0
        s_DK2 = 1 - s_DK1
        return df_dk_8784, s_DK1, s_DK2
    else:
        return df_dk_8784

# same but does not aggregate to one year
def fetch_pcs_timeseries(
    value_columns: Sequence[str],
    start: str,
    end: str,
    *,
    timezone: str = "UTC",
    price_areas: Optional[Sequence[str]] = None,   # e.g. ["DK1"] or ["DK1","DK2"]; None = all
    aggregate_price_areas: bool = True,            # True => DK total per hour
    save_path: Optional[str] = None,               # e.g. r"..\out\dk_total.tsv"
) -> pd.DataFrame:
    """
    Pulls raw hourly data from EnergiDataService (ProductionConsumptionSettlement)
    and returns datetime + value across the requested span (multiple years OK).

    - No "typical year" averaging
    - No leap-day removal
    - No extra day appended
    """

    base = "https://api.energidataservice.dk/dataset/ProductionConsumptionSettlement"
    params = {
        "start": start,
        "end": end,
        "timezone": timezone,
        "columns": "HourUTC,PriceArea," + ",".join(value_columns),
        "sort": "HourUTC asc",
        "limit": 0,
    }

    r = requests.get(base, params=params, timeout=60)
    r.raise_for_status()
    df = pd.DataFrame(r.json().get("records", []))
    if df.empty:
        out = pd.DataFrame({"HourUTC": pd.to_datetime([]), "value": pd.Series(dtype="float64")})
        if save_path:
            out.to_csv(save_path, sep="\t", index=False)
        return out

    # parse time
    df["HourUTC"] = pd.to_datetime(df["HourUTC"], utc=True, errors="coerce")

    # optional area filter
    if price_areas is not None:
        df = df[df["PriceArea"].isin(price_areas)].copy()

    # combine selected columns into one value
    for c in value_columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["value"] = df[list(value_columns)].sum(axis=1, min_count=1)

    # keep just datetime + value (either DK total per hour or per-area rows)
    if aggregate_price_areas:
        out = (
            df.groupby("HourUTC", as_index=False)["value"]
              .sum(min_count=1)
              .sort_values("HourUTC")
        )
    else:
        out = df[["HourUTC", "value", "PriceArea"]].sort_values(["HourUTC", "PriceArea"])

    if save_path:
        out.to_csv(save_path, sep="\t", index=False)

    return out