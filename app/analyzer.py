from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd


@dataclass
class SpendingSummary:
    total_spent: float
    category_breakdown: Dict[str, float]
    monthly_totals: Dict[str, float]
    top_merchants: List[Tuple[str, float]]
    habit_note: str


CATEGORY_KEYWORDS = {
    "groceries": ["grocery", "supermarket", "market", "store"],
    "dining": ["cafe", "restaurant", "bar", "dining", "food"],
    "entertainment": ["cinema", "movie", "stream", "game", "concert"],
    "transport": ["uber", "lyft", "taxi", "bus", "train", "fuel", "gas"],
    "housing": ["rent", "mortgage", "apartment"],
    "utilities": ["utility", "electric", "water", "internet", "phone"],
    "shopping": ["shop", "amazon", "mall", "clothes", "retail"],
    "health": ["pharmacy", "clinic", "doctor", "health", "medical"],
}


REQUIRED_COLUMNS = {"date", "description", "amount"}


class StatementFormatError(ValueError):
    """Raised when a statement CSV is missing required columns."""


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={col: col.strip().lower() for col in df.columns})
    if not REQUIRED_COLUMNS.issubset(df.columns):
        raise StatementFormatError(
            "Statement must include date, description, and amount columns"
        )

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "amount", "description"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df = df[df["amount"] < 0].copy()  # treat outflow as positive spend
    df["amount"] = df["amount"].abs()
    df["description"] = df["description"].str.lower()
    return df


def _categorize(description: str) -> str:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in description for keyword in keywords):
            return category
    return "other"


def load_statement(path: Path | str) -> pd.DataFrame:
    return pd.read_csv(path)


def analyze_statement(df: pd.DataFrame) -> SpendingSummary:
    df = _normalize_dataframe(df)
    if df.empty:
        return SpendingSummary(0.0, {}, {}, [], "No spending data found.")

    df["category"] = df["description"].apply(_categorize)
    df["month"] = df["date"].dt.to_period("M").astype(str)

    total_spent = float(df["amount"].sum())
    category_breakdown = (
        df.groupby("category")["amount"].sum().sort_values(ascending=False).to_dict()
    )
    monthly_totals = (
        df.groupby("month")["amount"].sum().sort_index().to_dict()
    )
    top_merchants = (
        df.groupby("description")["amount"].sum().sort_values(ascending=False).head(5)
    )
    top_merchants_list: List[Tuple[str, float]] = list(top_merchants.items())

    habit_note = _build_habit_note(category_breakdown, monthly_totals)

    return SpendingSummary(
        total_spent=total_spent,
        category_breakdown=category_breakdown,
        monthly_totals=monthly_totals,
        top_merchants=top_merchants_list,
        habit_note=habit_note,
    )


def _build_habit_note(
    category_breakdown: Dict[str, float], monthly_totals: Dict[str, float]
) -> str:
    if not category_breakdown:
        return "No spending activity detected."

    top_category, top_amount = next(iter(category_breakdown.items()))
    note_parts = [
        f"You spend the most on {top_category} (${top_amount:.2f}).",
    ]

    if len(monthly_totals) >= 2:
        months = list(monthly_totals.items())
        first, last = months[0], months[-1]
        trend = "up" if last[1] > first[1] else "down"
        note_parts.append(
            f"Spending trend from {first[0]} to {last[0]} is trending {trend}."
        )

    if "dining" in category_breakdown and category_breakdown["dining"] > 0.25 * sum(
        category_breakdown.values()
    ):
        note_parts.append("Dining accounts for more than a quarter of your spending.")

    return " ".join(note_parts)


def summarize_file(path: Path | str) -> SpendingSummary:
    df = load_statement(path)
    return analyze_statement(df)


def analyze_file_like(file_like: Iterable[bytes]) -> SpendingSummary:
    df = pd.read_csv(BytesIO(b"".join(file_like)))
    return analyze_statement(df)
