from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from dateutil import parser


def normalize_whitespace(s: Any) -> str | None:
    if s is None:
        return None
    s = str(s).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return None
    return re.sub(r"\s+", " ", s)


def to_number(v: Any) -> float | None:
    if v is None:
        return None
    if isinstance(v, (int, float)) and not pd.isna(v):
        return float(v)
    s = str(v).strip().replace(",", "")
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return None
    s = re.sub(r"[^\d\.\-]", "", s)
    if s in {"", "-", ".", "-."}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def to_date(v: Any):
    if v is None:
        return pd.NaT
    if isinstance(v, str):
        v = v.strip()
    if v in {"", "nan", "None", None}:
        return pd.NaT
    try:
        return pd.to_datetime(parser.parse(str(v), dayfirst=False), errors="coerce")
    except Exception:
        return pd.NaT


def safe_text_from_column_value(cell: Dict[str, Any]) -> Any:
    if not cell:
        return None

    text = cell.get("text")
    if text not in [None, ""]:
        return text

    raw_value = cell.get("value")
    if raw_value in [None, ""]:
        return None

    try:
        parsed = json.loads(raw_value)
        if isinstance(parsed, dict):
            if "text" in parsed:
                return parsed["text"]
            if "label" in parsed:
                return parsed["label"]
            if "date" in parsed:
                return parsed["date"]
        return str(parsed)
    except Exception:
        return raw_value


def board_to_dataframe(board_data) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for item in board_data.items:
        row = {"_item_id": item.id, "_item_name": item.name}
        for col_title, cell in item.column_values.items():
            row[col_title] = safe_text_from_column_value(cell)
        rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    return df


def normalize_deals_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    caveats: List[str] = []
    if df.empty:
        return df, ["Deals board returned no rows."]

    rename_map = {
        "_item_name": "deal_name",
        "Deal Name": "deal_name",
        "Owner code": "owner_code",
        "Client Code": "client_code",
        "Deal Status": "deal_status",
        "Close Date (A)": "actual_close_date",
        "Closure Probability": "closure_probability",
        "Masked Deal value": "deal_value",
        "Tentative Close Date": "tentative_close_date",
        "Deal Stage": "deal_stage",
        "Product deal": "product_deal",
        "Sector/service": "sector",
        "Created Date": "created_date",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    text_cols = [
        "deal_name", "owner_code", "client_code", "deal_status",
        "deal_stage", "product_deal", "sector"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_whitespace)

    for col in ["closure_probability", "deal_value"]:
        if col in df.columns:
            df[col] = df[col].apply(to_number)

    for col in ["actual_close_date", "tentative_close_date", "created_date"]:
        if col in df.columns:
            df[col] = df[col].apply(to_date)

    if "closure_probability" in df.columns:
        # if values are 0-100, convert to 0-1
        mask = df["closure_probability"].notna() & (df["closure_probability"] > 1)
        df.loc[mask, "closure_probability"] = df.loc[mask, "closure_probability"] / 100.0
        df["closure_probability"] = df["closure_probability"].clip(lower=0, upper=1)

    if "deal_value" in df.columns and df["deal_value"].isna().mean() > 0.1:
        caveats.append("A meaningful share of deals are missing deal_value.")

    if "closure_probability" in df.columns and df["closure_probability"].isna().mean() > 0.1:
        caveats.append("A meaningful share of deals are missing closure_probability, so weighted pipeline may be understated.")

    if "sector" in df.columns:
        missing_sector = df["sector"].isna().mean()
        if missing_sector > 0:
            caveats.append(f"{missing_sector:.0%} of deals are missing sector labels.")

    return df, caveats


def normalize_work_orders_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    caveats: List[str] = []
    if df.empty:
        return df, ["Work Orders board returned no rows."]

    rename_map = {
        "_item_name": "deal_name",
        "Deal name masked": "deal_name",
        "Customer Name Code": "customer_code",
        "Serial #": "serial_no",
        "Nature of Work": "nature_of_work",
        "Last executed month of recurring project": "last_executed_month",
        "Execution Status": "execution_status",
        "Data Delivery Date": "data_delivery_date",
        "Date of PO/LOI": "po_loi_date",
        "Document Type": "document_type",
        "Probable Start Date": "probable_start_date",
        "Probable End Date": "probable_end_date",
        "BD/KAM Personnel code": "owner_code",
        "Sector": "sector",
        "Type of Work": "type_of_work",
        "Is any Skylark software platform part of the client deliverables in this deal?": "platform_part",
        "Last invoice date": "last_invoice_date",
        "latest invoice no.": "invoice_no",
        "Amount in Rupees (Excl of GST) (Masked)": "amount_ex_gst",
        "Amount in Rupees (Incl of GST) (Masked)": "amount_inc_gst",
        "Billed Value in Rupees (Excl of GST.) (Masked)": "billed_ex_gst",
        "Billed Value in Rupees (Incl of GST.) (Masked)": "billed_inc_gst",
        "Collected Amount in Rupees (Incl of GST.) (Masked)": "collected_inc_gst",
        "Amount to be billed in Rs. (Exl. of GST) (Masked)": "to_be_billed_ex_gst",
        "Amount to be billed in Rs. (Incl. of GST) (Masked)": "to_be_billed_inc_gst",
        "Amount Receivable (Masked)": "amount_receivable",
        "AR Priority account": "ar_priority_account",
        "Quantity by Ops": "quantity_by_ops",
        "Quantities as per PO": "quantity_as_per_po",
        "Quantity billed (till date)": "quantity_billed_till_date",
        "Balance in quantity": "balance_quantity",
        "Invoice Status": "invoice_status",
        "Expected Billing Month": "expected_billing_month",
        "Actual Billing Month": "actual_billing_month",
        "Actual Collection Month": "actual_collection_month",
        "WO Status (billed)": "wo_status_billed",
        "Collection status": "collection_status",
        "Collection Date": "collection_date",
        "Billing Status": "billing_status",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    text_cols = [
        "deal_name", "customer_code", "serial_no", "nature_of_work",
        "execution_status", "document_type", "owner_code", "sector",
        "type_of_work", "platform_part", "invoice_no", "invoice_status",
        "expected_billing_month", "actual_billing_month",
        "actual_collection_month", "wo_status_billed",
        "collection_status", "billing_status"
    ]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].apply(normalize_whitespace)

    numeric_cols = [
        "amount_ex_gst", "amount_inc_gst", "billed_ex_gst", "billed_inc_gst",
        "collected_inc_gst", "to_be_billed_ex_gst", "to_be_billed_inc_gst",
        "amount_receivable", "quantity_by_ops", "quantity_as_per_po",
        "quantity_billed_till_date", "balance_quantity"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_number)

    date_cols = [
        "data_delivery_date", "po_loi_date", "probable_start_date",
        "probable_end_date", "last_invoice_date", "collection_date"
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].apply(to_date)

    for col in ["sector", "execution_status", "billing_status", "collection_status"]:
        if col in df.columns:
            missing = df[col].isna().mean()
            if missing > 0.15:
                caveats.append(f"A material share of work orders are missing {col} values.")

    return df, caveats


def normalize_all(deals_board, work_orders_board):
    deals_raw = board_to_dataframe(deals_board)
    work_orders_raw = board_to_dataframe(work_orders_board)

    deals_df, deals_caveats = normalize_deals_df(deals_raw)
    work_orders_df, work_orders_caveats = normalize_work_orders_df(work_orders_raw)

    return deals_df, work_orders_df, deals_caveats + work_orders_caveats