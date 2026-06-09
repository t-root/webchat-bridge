"""Load ai_models_config.json for the Playwright bridge."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "ai_models_config.json")


@lru_cache(maxsize=1)
def load_config() -> dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_model_by_id(model_id: str | None) -> dict[str, Any] | None:
    config = load_config()
    needle = (model_id or "").lower()

    for key, model in (config.get("models") or {}).items():
        mid = (model.get("model") or key).lower()
        if mid == needle:
            return {"key": key, **model}
    return None


def list_models() -> list[dict[str, Any]]:
    config = load_config()
    return [
        {
            "key": key,
            "name": model.get("name"),
            "model": model.get("model") or key,
            "url": model.get("url"),
        }
        for key, model in (config.get("models") or {}).items()
    ]
