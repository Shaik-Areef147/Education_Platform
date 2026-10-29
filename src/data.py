"""Data loading, integration and validation for EduPro."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "EduPro_Online_Platform.xlsx"

AGE_BINS = [0, 17, 25, 35, 45, 200]
AGE_LABELS = ["<18", "18-25", "26-35", "36-45", "45+"]
LEVEL_ORDER = ["Beginner", "Intermediate", "Advanced"]

REQUIRED = {
    "Users": ["UserID", "UserName", "Age", "Gender"],
    "Courses": ["CourseID", "CourseName", "CourseCategory", "CourseType", "CourseLevel"],
    "Transactions": ["TransactionID", "UserID", "CourseID", "TransactionDate"],
}


class DataError(Exception):
    """Raised when the workbook does not have the expected structure."""


def add_age_group(ages: pd.Series) -> pd.Series:
    return pd.cut(ages, bins=AGE_BINS, labels=AGE_LABELS).astype(str)


def integrate(sheets: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Validate sheets, join Users <-> Transactions <-> Courses.

    Returns (enrollments, users, quality_report).
    """
    for sheet, cols in REQUIRED.items():
        if sheet not in sheets:
            raise DataError(f"Missing sheet '{sheet}'. Found: {list(sheets)}")
        missing = [c for c in cols if c not in sheets[sheet].columns]
        if missing:
            raise DataError(f"Sheet '{sheet}' is missing columns: {missing}")

    users = sheets["Users"][REQUIRED["Users"]].copy()
    courses = sheets["Courses"].copy()
    tx = sheets["Transactions"][REQUIRED["Transactions"]].copy()

    for df, key in ((users, "UserID"), (courses, "CourseID"), (tx, "TransactionID")):
        df[key] = df[key].astype(str).str.strip()
    tx["UserID"] = tx["UserID"].astype(str).str.strip()
    tx["CourseID"] = tx["CourseID"].astype(str).str.strip()

    report = {
        "users": len(users),
        "courses": len(courses),
        "transactions": len(tx),
        "duplicate_users": int(users.duplicated("UserID").sum()),
        "duplicate_courses": int(courses.duplicated("CourseID").sum()),
        "duplicate_transactions": int(tx.duplicated("TransactionID").sum()),
        "orphan_user_ids": int((~tx["UserID"].isin(users["UserID"])).sum()),
        "orphan_course_ids": int((~tx["CourseID"].isin(courses["CourseID"])).sum()),
        "missing_values": int(
            users.isna().sum().sum() + tx.isna().sum().sum()
            + courses[REQUIRED["Courses"]].isna().sum().sum()
        ),
    }

    users = users.drop_duplicates("UserID")
    courses = courses.drop_duplicates("CourseID")
    tx = tx.drop_duplicates("TransactionID")

    users["Age"] = pd.to_numeric(users["Age"], errors="coerce")
    users = users.dropna(subset=["Age"])
    users["Age"] = users["Age"].astype(int)
    users["Gender"] = users["Gender"].astype(str).str.strip().str.title()
    users["AgeGroup"] = add_age_group(users["Age"])

    tx["TransactionDate"] = pd.to_datetime(tx["TransactionDate"], errors="coerce")

    course_cols = ["CourseID", "CourseName", "CourseCategory", "CourseType", "CourseLevel"]
    for opt in ("CoursePrice", "CourseRating", "CourseDuration"):
        if opt in courses.columns:
            course_cols.append(opt)
    enr = tx.merge(users, on="UserID", how="inner").merge(
        courses[course_cols], on="CourseID", how="inner"
    )
    enr["Month"] = enr["TransactionDate"].dt.to_period("M").dt.to_timestamp()
    report["joined_rows"] = len(enr)
    report["dropped_rows"] = report["transactions"] - len(enr)
    report["date_min"] = enr["TransactionDate"].min()
    report["date_max"] = enr["TransactionDate"].max()
    return enr.reset_index(drop=True), users.reset_index(drop=True), report


@st.cache_data(show_spinner="Loading EduPro data...")
def load_default() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    sheets = pd.read_excel(DATA_FILE, sheet_name=None, engine="openpyxl")
    return integrate(sheets)


@st.cache_data(show_spinner="Reading uploaded workbook...")
def load_uploaded(raw: bytes) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    import io

    sheets = pd.read_excel(io.BytesIO(raw), sheet_name=None, engine="openpyxl")
    return integrate(sheets)
