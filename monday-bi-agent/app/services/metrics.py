from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd


def quarter_date_range(ref: Optional[pd.Timestamp] = None) -> Tuple[pd.Timestamp, pd.Timestamp]:
    ref = ref or pd.Timestamp.today().normalize()
    q = ref.quarter
    year = ref.year
    start = pd.Timestamp(year=year, month=(q - 1) * 3 + 1, day=1)
    end = start + pd.offsets.QuarterEnd()
    return start, end


def apply_timeframe(df: pd.DataFrame, timeframe: Optional[str], date_col: str) -> pd.DataFrame:
    if df.empty or date_col not in df.columns:
        return df

    tf = (timeframe or "").strip().lower()

    if tf in {"this quarter", "current quarter", "quarter"}:
        start, end = quarter_date_range()
        return df[(df[date_col] >= start) & (df[date_col] <= end)]

    if tf in {"this month", "current month", "month"}:
        now = pd.Timestamp.today().normalize()
        start = pd.Timestamp(year=now.year, month=now.month, day=1)
        end = start + pd.offsets.MonthEnd()
        return df[(df[date_col] >= start) & (df[date_col] <= end)]

    if tf in {"this year", "current year", "year"}:
        now = pd.Timestamp.today().normalize()
        start = pd.Timestamp(year=now.year, month=1, day=1)
        end = pd.Timestamp(year=now.year, month=12, day=31)
        return df[(df[date_col] >= start) & (df[date_col] <= end)]

    return df


def apply_sector(df: pd.DataFrame, sector: Optional[str]) -> pd.DataFrame:
    if df.empty or not sector or "sector" not in df.columns:
        return df

    sector = sector.strip().lower()

    # sector synonyms to capture business language
    SECTOR_SYNONYMS = {
        "energy": ["energy", "renewable", "renewables", "power", "powerline", "solar", "wind", "grid"],
        "mining": ["mining"],
        "railways": ["rail", "railway", "railways"],
        "infrastructure": ["infra", "infrastructure"],
    }

    keywords = SECTOR_SYNONYMS.get(sector, [sector])

    mask = False
    sector_series = df["sector"].fillna("").str.lower()

    for kw in keywords:
        mask = mask | sector_series.str.contains(kw, regex=False)

    return df[mask]


def compute_deals_metrics(deals_df: pd.DataFrame, sector: Optional[str], timeframe: Optional[str]) -> Dict:
    if deals_df.empty:
        return {"deals_available": False}

    base = deals_df.copy()
    base = apply_sector(base, sector)
    date_col = "tentative_close_date" if "tentative_close_date" in base.columns else "created_date"
    base = apply_timeframe(base, timeframe, date_col)

    result = {
        "deals_available": True,
        "row_count": int(len(base)),
        "sector_filter": sector,
        "timeframe": timeframe,
    }

    if "deal_value" in base.columns:
        result["open_pipeline"] = float(base["deal_value"].fillna(0).sum())

    if {"deal_value", "closure_probability"}.issubset(base.columns):
        result["weighted_pipeline"] = float(
            (base["deal_value"].fillna(0) * base["closure_probability"].fillna(0)).sum()
        )

    if "deal_status" in base.columns:
        result["deal_status_breakdown"] = (
            base["deal_status"].fillna("Unknown").value_counts(dropna=False).to_dict()
        )

    if "deal_stage" in base.columns:
        result["deal_stage_breakdown"] = (
            base["deal_stage"].fillna("Unknown").value_counts(dropna=False).to_dict()
        )

    if "sector" in deals_df.columns:
        sector_df = deals_df.copy()
        sector_df = apply_timeframe(sector_df, timeframe, date_col)
        grouped = (
            sector_df.groupby("sector", dropna=False)["deal_value"]
            .sum(min_count=1)
            .fillna(0)
            .sort_values(ascending=False)
        )
        result["deal_value_by_sector"] = {str(k): float(v) for k, v in grouped.items()}

    return result


def compute_work_order_metrics(work_orders_df: pd.DataFrame, sector: Optional[str], timeframe: Optional[str]) -> Dict:
    if work_orders_df.empty:
        return {"work_orders_available": False}

    base = work_orders_df.copy()
    base = apply_sector(base, sector)
    date_col = "probable_end_date" if "probable_end_date" in base.columns else "po_loi_date"
    base = apply_timeframe(base, timeframe, date_col)

    result = {
        "work_orders_available": True,
        "row_count": int(len(base)),
        "sector_filter": sector,
        "timeframe": timeframe,
    }

    if "execution_status" in base.columns:
        result["execution_status_breakdown"] = (
            base["execution_status"].fillna("Unknown").value_counts(dropna=False).to_dict()
        )

    if "billing_status" in base.columns:
        result["billing_status_breakdown"] = (
            base["billing_status"].fillna("Unknown").value_counts(dropna=False).to_dict()
        )

    if "collection_status" in base.columns:
        result["collection_status_breakdown"] = (
            base["collection_status"].fillna("Unknown").value_counts(dropna=False).to_dict()
        )

    numeric_fields = [
        "amount_inc_gst",
        "billed_inc_gst",
        "collected_inc_gst",
        "to_be_billed_inc_gst",
        "amount_receivable",
    ]
    for field in numeric_fields:
        if field in base.columns:
            result[field] = float(base[field].fillna(0).sum())

    if {"billing_status", "amount_receivable"}.issubset(base.columns):
        risk_df = base[
            base["billing_status"].fillna("").str.lower().isin(
                {"update required", "partially billed", "open"}
            )
        ].copy()
        result["billing_risk_receivable"] = float(risk_df["amount_receivable"].fillna(0).sum())
        result["billing_risk_count"] = int(len(risk_df))

    if "sector" in work_orders_df.columns and "amount_receivable" in work_orders_df.columns:
        sector_df = work_orders_df.copy()
        sector_df = apply_timeframe(sector_df, timeframe, date_col)
        grouped = (
            sector_df.groupby("sector", dropna=False)["amount_receivable"]
            .sum(min_count=1)
            .fillna(0)
            .sort_values(ascending=False)
        )
        result["receivable_by_sector"] = {str(k): float(v) for k, v in grouped.items()}

    return result


def compute_cross_board_summary(deals_metrics: Dict, wo_metrics: Dict) -> Dict:
    summary = {
        "deals_row_count": deals_metrics.get("row_count", 0),
        "work_orders_row_count": wo_metrics.get("row_count", 0),
        "weighted_pipeline": deals_metrics.get("weighted_pipeline"),
        "open_pipeline": deals_metrics.get("open_pipeline"),
        "receivables": wo_metrics.get("amount_receivable"),
        "to_be_billed": wo_metrics.get("to_be_billed_inc_gst"),
        "billing_risk_count": wo_metrics.get("billing_risk_count"),
        "billing_risk_receivable": wo_metrics.get("billing_risk_receivable"),
    }
    return summary


def build_metrics_package(question: str, routed_query, deals_df: pd.DataFrame, work_orders_df: pd.DataFrame, caveats: List[str]) -> Dict:
    deals_metrics = compute_deals_metrics(deals_df, routed_query.sector, routed_query.timeframe)
    wo_metrics = compute_work_order_metrics(work_orders_df, routed_query.sector, routed_query.timeframe)
    cross = compute_cross_board_summary(deals_metrics, wo_metrics)

    return {
        "question": question,
        "route": routed_query.model_dump(),
        "deals_metrics": deals_metrics,
        "work_order_metrics": wo_metrics,
        "cross_board_summary": cross,
        "data_quality_caveats": caveats,
    }