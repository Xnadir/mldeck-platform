"""
Model Registry — version, tag, and manage trained models.
"""

import json
import os
from datetime import datetime

REGISTRY_FILE = "model_registry.json"


def _load_registry() -> list:
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r") as f:
            return json.load(f)
    return []


def _save_registry(models: list):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(models, f, indent=2)


def register_model(experiment_id: str, name: str, description: str = "", tags: list = None) -> dict:
    """Register a model from an experiment run."""
    registry = _load_registry()

    # auto-increment version
    existing = [m for m in registry if m["name"] == name]
    version = len(existing) + 1

    model = {
        "id": f"{name}_v{version}",
        "name": name,
        "version": version,
        "experiment_id": experiment_id,
        "description": description,
        "tags": tags or [],
        "stage": "development",
        "registered_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    registry.insert(0, model)
    _save_registry(registry)
    return model


def update_stage(model_id: str, stage: str) -> dict:
    """Update model stage: development, staging, production, archived."""
    registry = _load_registry()
    for m in registry:
        if m["id"] == model_id:
            m["stage"] = stage
            m["updated_at"] = datetime.now().isoformat()
            _save_registry(registry)
            return m
    return {"error": "Model not found"}


def get_registry() -> list:
    return _load_registry()
