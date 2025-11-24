# Bank Statement Insight API

A lightweight FastAPI service that accepts a CSV bank statement upload and returns an AI-style analysis of spending habits. The analyzer normalizes the data, groups spending by category, surfaces top merchants, detects monthly trends, and shares a short habit note so users can understand where their money goes.

## Features

- Upload a CSV bank statement via `/analyze` and receive a structured JSON summary.
- Built-in `/analyze/sample` endpoint that analyzes the included sample statement for quick demos.
- Simple heuristic categorization based on merchant keywords and month-to-month trend detection.
- Tested analysis logic for predictable, repeatable insights.

## Project layout

- `app/analyzer.py` — core logic for normalizing statements, categorizing merchants, and generating a `SpendingSummary`.
- `app/main.py` — FastAPI app exposing health, sample analysis, and upload endpoints.
- `sample_data/sample_statement.csv` — example input file for quick testing.
- `tests/` — basic unit tests covering the analyzer.
- `requirements.txt` — pinned dependencies.

## Getting started

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the FastAPI server:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. Try the sample analysis from another terminal:

   ```bash
   curl http://localhost:8000/analyze/sample | python -m json.tool
   ```

4. Upload your own statement (must include `date`, `description`, and `amount` columns; outflow amounts should be negative):

   ```bash
   curl -X POST "http://localhost:8000/analyze" \
     -F "file=@/path/to/your_statement.csv"
   ```

## Running tests

```bash
pytest
```

## CSV format expectations

- Columns required: `date`, `description`, `amount` (case-insensitive; extra columns are ignored).
- Dates should be parseable by Pandas; invalid rows are dropped.
- Negative amounts are treated as spending and converted to positive values for reporting.

## Spending habit insight rules

- Categories are inferred from keyword matches (e.g., `uber` → transport, `cinema` → entertainment).
- The analyzer highlights the largest spending category, compares the first and last month totals, and flags heavy dining if it exceeds 25% of spend.

## Roadmap ideas

- Configurable category keyword lists per user.
- Better merchant clustering using embeddings.
- Visual dashboards for category and trend exploration.
