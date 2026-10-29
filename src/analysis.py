"""Pure-pandas analytics (no Streamlit) so they are unit-testable."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import AGE_LABELS, LEVEL_ORDER


def present_age_groups(df: pd.DataFrame) -> list[str]:
    have = set(df["AgeGroup"].unique())
    return [a for a in AGE_LABELS if a in have]


def kpis(enr: pd.DataFrame, users_all: pd.DataFrame) -> dict:
    n = len(enr)
    learners = enr["UserID"].nunique()
    g = enr.drop_duplicates("UserID")["Gender"].value_counts()
    female, male = int(g.get("Female", 0)), int(g.get("Male", 0))
    top_age = enr["AgeGroup"].value_counts().idxmax() if n else "-"
    top_cat = enr["CourseCategory"].value_counts().idxmax() if n else "-"
    top_level = enr["CourseLevel"].value_counts().idxmax() if n else "-"
    return {
        "total_enrollments": n,
        "active_learners": learners,
        "avg_per_learner": n / learners if learners else 0.0,
        "courses_in_use": enr["CourseID"].nunique(),
        "female": female,
        "male": male,
        "female_pct": female / learners * 100 if learners else 0.0,
        "male_pct": male / learners * 100 if learners else 0.0,
        "gender_ratio": (female / male) if male else np.nan,
        "top_age": top_age,
        "top_category": top_cat,
        "top_level": top_level,
        "free_pct": (enr["CourseType"].eq("Free").mean() * 100) if n else 0.0,
    }


def age_distribution(users: pd.DataFrame) -> pd.DataFrame:
    d = users.groupby("AgeGroup").size().reindex(AGE_LABELS).dropna().astype(int).reset_index(name="Learners")
    d["Share %"] = d["Learners"] / d["Learners"].sum() * 100
    return d


def enrollments_by_age(enr: pd.DataFrame) -> pd.DataFrame:
    d = enr.groupby("AgeGroup").agg(Enrollments=("TransactionID", "count"), Learners=("UserID", "nunique"))
    d = d.reindex(AGE_LABELS).dropna().astype(int).reset_index()
    d["Enrollments per learner"] = d["Enrollments"] / d["Learners"]
    d["Share %"] = d["Enrollments"] / d["Enrollments"].sum() * 100
    return d


def gender_summary(enr: pd.DataFrame) -> pd.DataFrame:
    d = enr.groupby("Gender").agg(Enrollments=("TransactionID", "count"), Learners=("UserID", "nunique")).reset_index()
    d["Enrollments per learner"] = d["Enrollments"] / d["Learners"]
    d["Learner share %"] = d["Learners"] / d["Learners"].sum() * 100
    return d


def count_by(enr: pd.DataFrame, col: str) -> pd.DataFrame:
    d = enr.groupby(col).size().reset_index(name="Enrollments").sort_values("Enrollments", ascending=False)
    d["Share %"] = d["Enrollments"] / d["Enrollments"].sum() * 100
    return d.reset_index(drop=True)


def category_popularity(enr: pd.DataFrame) -> pd.DataFrame:
    """Category Popularity Index = category share / equal share (100 = average)."""
    d = count_by(enr, "CourseCategory")
    k = len(d)
    d["Popularity Index"] = d["Enrollments"] / d["Enrollments"].sum() * k * 100 if k else 0
    return d


def level_distribution(enr: pd.DataFrame) -> pd.DataFrame:
    d = enr.groupby("CourseLevel").size().reindex(LEVEL_ORDER).dropna().astype(int).reset_index(name="Enrollments")
    d["Share %"] = d["Enrollments"] / d["Enrollments"].sum() * 100
    return d


def crosstab(enr: pd.DataFrame, row: str, col: str, normalize: str | None = None) -> pd.DataFrame:
    ct = pd.crosstab(enr[row], enr[col])
    if row == "AgeGroup":
        ct = ct.reindex([a for a in AGE_LABELS if a in ct.index])
    if col == "CourseLevel":
        ct = ct[[c for c in LEVEL_ORDER if c in ct.columns]]
    if row == "CourseLevel":
        ct = ct.reindex([c for c in LEVEL_ORDER if c in ct.index])
    if normalize == "row":
        ct = ct.div(ct.sum(axis=1), axis=0) * 100
    elif normalize == "col":
        ct = ct.div(ct.sum(axis=0), axis=1) * 100
    return ct


def top_pairs(enr: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    """Most over-indexed segment x category pairs (lift vs overall category share)."""
    overall = enr["CourseCategory"].value_counts(normalize=True)
    rows = []
    for (age, gen), seg in enr.groupby(["AgeGroup", "Gender"]):
        if len(seg) < 30:
            continue
        share = seg["CourseCategory"].value_counts(normalize=True)
        for cat, s in share.items():
            rows.append({"Segment": f"{age} / {gen}", "Category": cat, "Segment share %": s * 100,
                         "Platform share %": overall[cat] * 100, "Lift": s / overall[cat],
                         "Enrollments": int(round(s * len(seg)))})
    return pd.DataFrame(rows).sort_values("Lift", ascending=False).head(n).reset_index(drop=True)


def per_learner(enr: pd.DataFrame) -> pd.DataFrame:
    d = enr.groupby("UserID").agg(
        Courses=("CourseID", "nunique"), Age=("Age", "first"), AgeGroup=("AgeGroup", "first"),
        Gender=("Gender", "first"),
        Beginner=("CourseLevel", lambda s: (s == "Beginner").sum()),
        Intermediate=("CourseLevel", lambda s: (s == "Intermediate").sum()),
        Advanced=("CourseLevel", lambda s: (s == "Advanced").sum()),
        Free=("CourseType", lambda s: (s == "Free").sum()),
    ).reset_index()
    return d


def courses_per_learner_hist(pl: pd.DataFrame) -> pd.DataFrame:
    return pl.groupby("Courses").size().reset_index(name="Learners")


def concentration(pl: pd.DataFrame) -> pd.DataFrame:
    """Lorenz-style curve: cumulative share of enrollments vs share of learners (most active first)."""
    s = pl["Courses"].sort_values(ascending=False).reset_index(drop=True)
    cum_enr = s.cumsum() / s.sum() * 100
    cum_lrn = (np.arange(1, len(s) + 1)) / len(s) * 100
    return pd.DataFrame({"Learners %": cum_lrn, "Enrollments %": cum_enr.values})


def share_of_top(pl: pd.DataFrame, pct: float) -> float:
    s = pl["Courses"].sort_values(ascending=False)
    k = max(1, int(round(len(s) * pct / 100)))
    return s.head(k).sum() / s.sum() * 100


def learner_stage(pl: pd.DataFrame) -> pd.Series:
    """Classify each learner by the highest level they have taken."""
    def f(r):
        if r["Advanced"] > 0:
            return "Reached Advanced"
        if r["Intermediate"] > 0:
            return "Reached Intermediate"
        return "Beginner only"
    return pl.apply(f, axis=1)


def monthly(enr: pd.DataFrame) -> pd.DataFrame:
    return enr.groupby("Month").size().reset_index(name="Enrollments")


def cramers_v(ct: pd.DataFrame) -> float:
    """Association strength between two categorical variables (0-1)."""
    if ct.shape[0] < 2 or ct.shape[1] < 2 or ct.values.sum() == 0:
        return float("nan")
    obs = ct.values.astype(float)
    exp = obs.sum(1, keepdims=True) @ obs.sum(0, keepdims=True) / obs.sum()
    chi2 = ((obs - exp) ** 2 / exp).sum()
    return float(np.sqrt(chi2 / (obs.sum() * (min(obs.shape) - 1))))
