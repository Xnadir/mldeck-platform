"""
MLDeck — FastAPI server
Run with: python app.py
"""

import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import uvicorn

from experiments import run_experiment, get_experiments, compare_experiments
from models import register_model, update_stage, get_registry

app = FastAPI(title="MLDeck")
app.mount("/static", StaticFiles(directory="static"), name="static")

_current_df = None
_current_filename = ""


class RegisterInput(BaseModel):
    experiment_id: str
    name: str
    description: str = ""


class StageInput(BaseModel):
    model_id: str
    stage: str


@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    global _current_df, _current_filename
    content = await file.read()
    try:
        _current_df = pd.read_csv(io.StringIO(content.decode("utf-8")))
        _current_filename = file.filename
    except Exception as e:
        raise HTTPException(400, f"Failed to parse CSV: {e}")

    stats = {}
    for col in _current_df.columns:
        stats[col] = {
            "dtype": str(_current_df[col].dtype),
            "unique": int(_current_df[col].nunique()),
            "missing": int(_current_df[col].isna().sum()),
        }

    return {
        "filename": file.filename,
        "rows": len(_current_df),
        "columns": list(_current_df.columns),
        "stats": stats,
    }


@app.post("/api/experiment")
async def experiment(
    target: str = Form(...),
    features: str = Form(...),
    model_type: str = Form("random_forest"),
):
    if _current_df is None:
        raise HTTPException(400, "Upload a dataset first")

    feature_list = [f.strip() for f in features.split(",")]
    for f in feature_list + [target]:
        if f not in _current_df.columns:
            raise HTTPException(400, f"Column '{f}' not found")

    try:
        result = run_experiment(_current_df, target, feature_list, model_type)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/api/experiments")
async def list_experiments():
    return {"experiments": get_experiments()}


@app.post("/api/register")
async def register(body: RegisterInput):
    result = register_model(body.experiment_id, body.name, body.description)
    return result


@app.post("/api/stage")
async def stage(body: StageInput):
    if body.stage not in ["development", "staging", "production", "archived"]:
        raise HTTPException(400, "Invalid stage")
    result = update_stage(body.model_id, body.stage)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@app.get("/api/registry")
async def registry():
    return {"models": get_registry()}


if __name__ == "__main__":
    print("\n🎛️ Starting MLDeck Platform...")
    print("   Open http://localhost:8000 in your browser\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
