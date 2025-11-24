import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from app.analyzer import analyze_statement, summarize_file


def test_analyze_sample_file():
    summary = summarize_file(Path("sample_data/sample_statement.csv"))

    assert round(summary.total_spent, 2) == 1428.25
    assert "groceries" in summary.category_breakdown
    assert summary.habit_note


def test_analyze_dataframe_trend():
    df = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-02-01"],
            "description": ["restaurant", "restaurant"],
            "amount": [-10, -30],
        }
    )

    summary = analyze_statement(df)
    assert summary.category_breakdown["dining"] == 40
    assert "trending up" in summary.habit_note
