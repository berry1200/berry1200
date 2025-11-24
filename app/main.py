from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from .analyzer import analyze_file_like, summarize_file

app = FastAPI(title="Bank Statement Insight API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_statement(file: UploadFile = File(...)) -> JSONResponse:
    content = await file.read()
    summary = analyze_file_like([content])
    return JSONResponse(
        {
            "total_spent": summary.total_spent,
            "category_breakdown": summary.category_breakdown,
            "monthly_totals": summary.monthly_totals,
            "top_merchants": summary.top_merchants,
            "habit_note": summary.habit_note,
        }
    )


@app.get("/analyze/sample")
def analyze_sample() -> JSONResponse:
    summary = summarize_file("sample_data/sample_statement.csv")
    return JSONResponse(
        {
            "total_spent": summary.total_spent,
            "category_breakdown": summary.category_breakdown,
            "monthly_totals": summary.monthly_totals,
            "top_merchants": summary.top_merchants,
            "habit_note": summary.habit_note,
        }
    )
