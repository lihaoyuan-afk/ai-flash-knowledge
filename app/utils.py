import json
import re
from typing import Any


URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)


def first_url(text: str) -> str | None:
    match = URL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_json_object(raw: str) -> dict[str, Any]:
    stripped = raw.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?", "", stripped, flags=re.IGNORECASE).strip()
        stripped = re.sub(r"```$", "", stripped).strip()

    try:
        loaded = json.loads(stripped)
        if isinstance(loaded, dict):
            return loaded
    except json.JSONDecodeError:
        pass

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM response did not contain a JSON object")

    loaded = json.loads(stripped[start : end + 1])
    if not isinstance(loaded, dict):
        raise ValueError("LLM response JSON was not an object")
    return loaded


def clean_tags(tags: list[str] | None, limit: int = 3) -> list[str]:
    cleaned: list[str] = []
    for tag in tags or []:
        normalized = str(tag).strip()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized[:30])
        if len(cleaned) >= limit:
            break
    return cleaned or ["未分类"]


def chunk_text(text: str, chunk_size: int = 1900) -> list[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)] or [""]
